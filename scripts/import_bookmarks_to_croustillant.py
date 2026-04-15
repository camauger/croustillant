#!/usr/bin/env python3
# Pipeline d'import : favoris Chrome → recipe-scrapers → Croustillant (Neon DB).

"""
import_bookmarks_to_croustillant.py
====================================
Pipeline d'import : Chrome Bookmarks → recipe-scrapers → Croustillant (Neon DB)

Étapes :
  1. Lit le fichier Bookmarks de Chrome (JSON)
  2. Extrait les URLs d'un dossier spécifique (ex: "Recettes")
  3. Scrape chaque URL avec recipe-scrapers (wild_mode pour 631+ sites)
  4. Transforme en schéma Croustillant (JSONB ingredients/instructions)
  5. Insère dans Neon DB ou exporte en JSON

Usage :
  # Export JSON (sans connexion DB) — pour valider avant d'insérer
  python scripts/import_bookmarks_to_croustillant.py --dry-run

  # Import direct dans Neon DB
  python scripts/import_bookmarks_to_croustillant.py

  # Spécifier un dossier de favoris différent
  python scripts/import_bookmarks_to_croustillant.py --folder "Cuisine"

  # Importer depuis un fichier HTML exporté de Chrome
  python scripts/import_bookmarks_to_croustillant.py --html bookmarks.html

Dépendances :
  pip install -r scripts/requirements.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_html

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REQUEST_DELAY_SECONDS = 1.5

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Modèle de données Croustillant
# ---------------------------------------------------------------------------


@dataclass
class CroustillantRecipe:
    """Recette alignée sur neon-schema.sql et l'API Croustillant."""

    titre: str
    temps_preparation: str = ""
    temps_cuisson: str = ""
    rendement: str = ""
    ingredients: list[dict] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    image_url: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    source_url: str = ""


# ---------------------------------------------------------------------------
# Étape 1 : Extraire les URLs depuis les favoris Chrome
# ---------------------------------------------------------------------------


def find_chrome_bookmarks_path() -> Path:
    """Trouve le fichier Bookmarks de Chrome selon l'OS."""
    system = platform.system()
    home = Path.home()

    candidates = []
    if system == "Linux":
        candidates = [
            home / ".config/google-chrome/Default/Bookmarks",
            home / ".config/chromium/Default/Bookmarks",
            home / ".config/google-chrome-beta/Default/Bookmarks",
        ]
    elif system == "Darwin":
        candidates = [
            home / "Library/Application Support/Google/Chrome/Default/Bookmarks",
            home / "Library/Application Support/Chromium/Default/Bookmarks",
        ]
    elif system == "Windows":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        candidates = [
            local / "Google/Chrome/User Data/Default/Bookmarks",
        ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Fichier Bookmarks Chrome introuvable. "
        f"Candidats testés : {[str(p) for p in candidates]}"
    )


def extract_urls_from_bookmarks_json(
    bookmarks_path: Path,
    folder_name: str,
) -> list[dict[str, str]]:
    """Extrait les URLs d'un dossier (recherche récursive, insensible à la casse)."""
    with open(bookmarks_path, encoding="utf-8") as f:
        data = json.load(f)

    results: list[dict[str, str]] = []
    target = folder_name.lower()

    def walk(node: dict, in_target: bool = False) -> None:
        node_type = node.get("type", "")
        name = node.get("name", "").lower()

        if node_type == "folder" and target in name:
            in_target = True

        if node_type == "url" and in_target:
            results.append({
                "title": node.get("name", ""),
                "url": node.get("url", ""),
            })

        for child in node.get("children", []):
            walk(child, in_target)

    for root_key in data.get("roots", {}):
        root_node = data["roots"][root_key]
        if isinstance(root_node, dict):
            walk(root_node)

    return results


def extract_urls_from_bookmarks_html(
    html_path: Path,
    folder_name: str,
) -> list[dict[str, str]]:
    """Parse un export HTML Chrome (Bookmark Manager → Export)."""
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    results: list[dict[str, str]] = []
    target = folder_name.lower()

    for h3 in soup.find_all("h3"):
        if target in h3.get_text(strip=True).lower():
            dl = h3.find_next_sibling("dl")
            if dl:
                for a_tag in dl.find_all("a", href=True):
                    results.append({
                        "title": a_tag.get_text(strip=True),
                        "url": a_tag["href"],
                    })

    return results


# ---------------------------------------------------------------------------
# Étape 2 : Scraper les recettes
# ---------------------------------------------------------------------------


def quantity_to_float(raw: str) -> float:
    """Convertit une quantité texte (ex. 1/2, 1 1/2) en float pour l'API / liste d'achats."""
    s = raw.strip().replace(",", ".")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    try:
        parts = s.split()
        if len(parts) == 2 and "/" in parts[1]:
            return float(parts[0]) + float(Fraction(parts[1]))
        return float(Fraction(s))
    except (ValueError, ZeroDivisionError):
        return 0.0


def parse_ingredient_string(raw: str) -> dict:
    """
    Parse une ligne d'ingrédient en {nom, quantité, unité} (clés UI Croustillant).
    """
    pattern = r"""
        ^\s*
        (?P<qty>[\d\u00BC-\u00BE\u2150-\u215E./\s]+)?
        \s*
        (?P<unit>
            cups?|tbsp|tsp|tablespoons?|teaspoons?|oz|ounces?|lbs?|pounds?|
            g|kg|ml|l|litres?|liters?|
            tasses?|c\.\s*à\s*(?:soupe|thé|café)|
            cl|dl|
            pinch(?:es)?|pincées?|
            bunch(?:es)?|bottes?|
            cloves?|gousses?|
            slices?|tranches?|
            cans?|conserves?|boîtes?
        )?
        \s*(?:de\s+|d['']\s*|of\s+)?
        (?P<nom>.+?)
        \s*$
    """
    match = re.match(pattern, raw, re.IGNORECASE | re.VERBOSE)
    if match:
        qty_raw = (match.group("qty") or "").strip()
        return {
            "nom": match.group("nom").strip(),
            "quantité": quantity_to_float(qty_raw),
            "unité": (match.group("unit") or "").strip(),
        }
    return {"nom": raw.strip(), "quantité": 0.0, "unité": ""}


def scrape_recipe(url: str) -> Optional[CroustillantRecipe]:
    """Télécharge et scrape une URL de recette."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        log.warning("  ✗ HTTP error pour %s: %s", url, e)
        return None

    try:
        scraper = scrape_html(
            html=response.text,
            org_url=url,
            wild_mode=True,
        )
    except Exception as e:
        log.warning("  ✗ Parsing error pour %s: %s", url, e)
        return None

    try:
        titre = scraper.title() or urlparse(url).path.strip("/").replace("-", " ").title()
    except Exception:
        titre = urlparse(url).path.strip("/").replace("-", " ").title()

    raw_ingredients = []
    try:
        raw_ingredients = scraper.ingredients() or []
    except Exception:
        pass

    ingredients = [parse_ingredient_string(ing) for ing in raw_ingredients]

    instructions = []
    try:
        instructions = scraper.instructions_list() or []
    except Exception:
        try:
            raw = scraper.instructions() or ""
            instructions = [s.strip() for s in raw.split("\n") if s.strip()]
        except Exception:
            pass

    prep_time = ""
    cook_time = ""
    try:
        total = scraper.total_time()
        if total:
            prep_time = f"{total} min"
    except Exception:
        pass
    try:
        pt = scraper.prep_time()
        if pt:
            prep_time = f"{pt} min"
    except Exception:
        pass
    try:
        ct = scraper.cook_time()
        if ct:
            cook_time = f"{ct} min"
    except Exception:
        pass

    rendement = ""
    try:
        rendement = scraper.yields() or ""
    except Exception:
        pass

    image_url = ""
    try:
        image_url = scraper.image() or ""
    except Exception:
        pass

    category = ""
    try:
        category = scraper.category() or ""
    except Exception:
        pass

    tags = []
    try:
        host = urlparse(url).hostname or ""
        host_clean = host.replace("www.", "")
        if host_clean:
            tags.append(host_clean)
    except Exception:
        pass
    if category:
        tags.append(category)

    return CroustillantRecipe(
        titre=titre,
        temps_preparation=prep_time,
        temps_cuisson=cook_time,
        rendement=rendement,
        ingredients=ingredients,
        instructions=instructions,
        image_url=image_url,
        category=category,
        tags=tags,
        source_url=url,
    )


# ---------------------------------------------------------------------------
# Étape 3 : Insertion dans Neon DB
# ---------------------------------------------------------------------------


def insert_recipes_to_neon(
    recipes: list[CroustillantRecipe],
    database_url: str,
) -> tuple[int, int]:
    """Insère avec ON CONFLICT (titre) DO UPDATE. Retourne (traitées, erreurs)."""
    try:
        import psycopg2
        from psycopg2.extras import Json
    except ImportError:
        log.error("psycopg2 non installé. pip install psycopg2-binary")
        sys.exit(1)

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    ok = 0
    errors = 0

    for recipe in recipes:
        try:
            cur.execute(
                """
                INSERT INTO recipes (
                    titre, temps_preparation, temps_cuisson, rendement,
                    ingredients, instructions, image_url, category, tags
                )
                VALUES (
                    %(titre)s, %(temps_preparation)s, %(temps_cuisson)s, %(rendement)s,
                    %(ingredients)s, %(instructions)s, %(image_url)s, %(category)s, %(tags)s
                )
                ON CONFLICT (titre) DO UPDATE SET
                    temps_preparation = EXCLUDED.temps_preparation,
                    temps_cuisson = EXCLUDED.temps_cuisson,
                    rendement = EXCLUDED.rendement,
                    ingredients = EXCLUDED.ingredients,
                    instructions = EXCLUDED.instructions,
                    image_url = EXCLUDED.image_url,
                    category = EXCLUDED.category,
                    tags = EXCLUDED.tags
                """,
                {
                    "titre": recipe.titre,
                    "temps_preparation": recipe.temps_preparation,
                    "temps_cuisson": recipe.temps_cuisson,
                    "rendement": recipe.rendement,
                    "ingredients": Json(recipe.ingredients),
                    "instructions": Json(recipe.instructions),
                    "image_url": recipe.image_url,
                    "category": recipe.category,
                    "tags": recipe.tags,
                },
            )
            ok += 1
        except Exception as e:
            log.warning("  ✗ DB error pour '%s': %s", recipe.titre, e)
            conn.rollback()
            errors += 1
            continue

    conn.commit()
    cur.close()
    conn.close()

    return ok, errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import Chrome bookmark recipes into Croustillant (Neon DB)"
    )
    parser.add_argument(
        "--folder", "-f",
        default="Recettes",
        help="Nom du dossier de favoris à chercher (défaut: Recettes)",
    )
    parser.add_argument(
        "--bookmarks", "-b",
        default=None,
        help="Chemin vers le fichier Bookmarks JSON de Chrome (auto-détecté si omis)",
    )
    parser.add_argument(
        "--html",
        default=None,
        help="Chemin vers un fichier HTML exporté depuis Chrome (au lieu du JSON)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ne pas insérer en DB, exporter en JSON à la place",
    )
    parser.add_argument(
        "--output", "-o",
        default="croustillant_import.json",
        help="Fichier de sortie pour --dry-run (défaut: croustillant_import.json)",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="URL de connexion Neon DB (ou variable DATABASE_URL)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY_SECONDS,
        help=f"Délai entre les requêtes en secondes (défaut: {REQUEST_DELAY_SECONDS})",
    )

    args = parser.parse_args()

    log.info("Recherche des favoris dans le dossier '%s'...", args.folder)

    if args.html:
        html_path = Path(args.html)
        if not html_path.exists():
            log.error("Fichier HTML introuvable : %s", html_path)
            sys.exit(1)
        bookmarks = extract_urls_from_bookmarks_html(html_path, args.folder)
        bk_path: Optional[Path] = None
    else:
        if args.bookmarks:
            bk_path = Path(args.bookmarks)
        else:
            bk_path = find_chrome_bookmarks_path()
        log.info("  Fichier Bookmarks : %s", bk_path)
        bookmarks = extract_urls_from_bookmarks_json(bk_path, args.folder)

    if not bookmarks:
        log.warning(
            "Aucun favori trouvé dans le dossier '%s'. "
            "Vérifiez le nom du dossier avec --folder.",
            args.folder,
        )
        if bk_path is not None:
            _show_available_folders(bk_path)
        sys.exit(0)

    log.info("  → %s URLs trouvées", len(bookmarks))

    log.info("Scraping des recettes...")
    recipes: list[CroustillantRecipe] = []
    failed_urls: list[str] = []

    for i, bk in enumerate(bookmarks, 1):
        url = bk["url"]
        title = bk["title"]
        log.info("  [%s/%s] %s", i, len(bookmarks), title)
        log.info("    → %s", url)

        recipe = scrape_recipe(url)
        if recipe:
            log.info(
                "    ✓ %s (%s ingrédients)",
                recipe.titre,
                len(recipe.ingredients),
            )
            recipes.append(recipe)
        else:
            failed_urls.append(url)

        if i < len(bookmarks):
            time.sleep(args.delay)

    log.info(
        "\nRésultats : %s réussies, %s échouées",
        len(recipes),
        len(failed_urls),
    )

    if failed_urls:
        log.info("URLs échouées :")
        for failed in failed_urls:
            log.info("  ✗ %s", failed)

    if not recipes:
        log.warning("Aucune recette scrapée. Rien à importer.")
        sys.exit(0)

    if args.dry_run:
        output_path = Path(args.output)
        export_data = [
            {**asdict(r), "ingredients": r.ingredients, "instructions": r.instructions}
            for r in recipes
        ]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        log.info("Export JSON : %s (%s recettes)", output_path, len(recipes))
    else:
        db_url = (
            args.database_url
            or os.environ.get("DATABASE_URL")
            or os.environ.get("NETLIFY_DATABASE_URL")
        )
        if not db_url:
            log.error(
                "DATABASE_URL non définie. Options :\n"
                "  1. export DATABASE_URL='postgresql://...'\n"
                "  2. --database-url 'postgresql://...'\n"
                "  3. --dry-run pour exporter en JSON"
            )
            sys.exit(1)

        log.info("Insertion dans Neon DB...")
        inserted, skipped = insert_recipes_to_neon(recipes, db_url)
        log.info("  ✓ %s traitées en base, %s erreurs", inserted, skipped)


def _show_available_folders(bookmarks_path: Path) -> None:
    """Affiche les dossiers contenant des liens (aide au diagnostic)."""
    try:
        with open(bookmarks_path, encoding="utf-8") as f:
            data = json.load(f)

        folders: list[str] = []

        def walk(node: dict, path: str = "") -> None:
            if node.get("type") == "folder":
                name = node.get("name", "")
                full_path = f"{path}/{name}" if path else name
                child_count = len([
                    c for c in node.get("children", [])
                    if c.get("type") == "url"
                ])
                if child_count > 0:
                    folders.append(f"  • {full_path} ({child_count} liens)")
                for child in node.get("children", []):
                    walk(child, full_path)

        for root_key in data.get("roots", {}):
            root_node = data["roots"][root_key]
            if isinstance(root_node, dict):
                walk(root_node)

        if folders:
            log.info("\nDossiers disponibles avec des liens :")
            for folder_line in folders:
                log.info("%s", folder_line)
    except Exception:
        pass


if __name__ == "__main__":
    main()
