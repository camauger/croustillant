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

  # Pipeline en deux temps : 1) export JSON, 2) révision manuelle du fichier, 3) insertion BD
  python scripts/import_bookmarks_to_croustillant.py --folder Cuisine --dry-run -o recettes.json
  python scripts/import_bookmarks_to_croustillant.py --from-json recettes.json

  # Vérifier les liens (404, etc.) et optionnellement une copie Bookmarks sans les morts
  python scripts/import_bookmarks_to_croustillant.py --folder Cuisine --check-urls
  python scripts/import_bookmarks_to_croustillant.py --folder Cuisine --check-urls --prune-bookmarks Bookmarks.nettoyes

Dépendances :
  pip install -r scripts/requirements.txt

Limites :
  - Seules les pages avec métadonnées de recette (souvent schema.org / JSON-LD) sont importées.
  - Les favoris non recettes (DIY, commerce, articles) échouent — normal.
  - Paywalls (402) et anti-bots (403) ne sont pas contournables sans navigateur / session.
  - Tester sur un sous-ensemble : --max 10 --dry-run
  - --check-urls : un 403 « bot » n’est pas un 404 ; par défaut seuls 404 et 410 sont retirés au prune.
"""

from __future__ import annotations

import argparse
import copy
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
from urllib.parse import parse_qsl, urlparse, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup
from recipe_scrapers import (
    NoSchemaFoundInWildMode,
    RecipeSchemaNotFound,
    WebsiteNotImplementedError,
    scrape_html,
)

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

# Timeouts (connect, read) — évite les blocages indéfinis sur serveurs lents
CONNECT_TIMEOUT_SECONDS = 8
READ_TIMEOUT_SECONDS = 25

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

HTTP_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

_TRACKING_QUERY_KEYS = frozenset({
    "fbclid", "gclid", "igshid", "_ga", "mc_eid", "mkt_tok", "mc_cid",
})
_TRACKING_KEY_PREFIXES = ("utm_",)

_http_session: requests.Session | None = None


def http_session() -> requests.Session:
    """Session HTTP réutilisable (mêmes en-têtes que le navigateur)."""
    global _http_session
    if _http_session is None:
        s = requests.Session()
        s.headers.update(HTTP_HEADERS)
        _http_session = s
    return _http_session


def normalize_bookmark_url(url: str) -> str:
    """Retire fbclid, utm_*, etc. (souvent inutiles et parfois problématiques)."""
    raw = url.strip()
    parsed = urlparse(raw)
    if not parsed.query:
        return raw
    kept: list[tuple[str, str]] = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        kl = key.lower()
        if kl in _TRACKING_QUERY_KEYS or any(
            kl.startswith(p) for p in _TRACKING_KEY_PREFIXES
        ):
            continue
        kept.append((key, val))
    new_query = urlencode(kept, doseq=True) if kept else ""
    return urlunparse(parsed._replace(query=new_query))


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


def recipe_from_export_dict(data: dict) -> CroustillantRecipe:
    """Construit une recette à partir d'un objet JSON (export --dry-run)."""
    titre = (data.get("titre") or "").strip()
    if not titre:
        raise ValueError("champ 'titre' requis et non vide")

    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list):
        ingredients = []

    instructions = data.get("instructions")
    if isinstance(instructions, str):
        instructions = [instructions] if instructions.strip() else []
    elif not isinstance(instructions, list):
        instructions = []

    tags = data.get("tags")
    if not isinstance(tags, list):
        tags = []

    return CroustillantRecipe(
        titre=titre,
        temps_preparation=str(data.get("temps_preparation") or ""),
        temps_cuisson=str(data.get("temps_cuisson") or ""),
        rendement=str(data.get("rendement") or ""),
        ingredients=ingredients,
        instructions=instructions,
        image_url=str(data.get("image_url") or ""),
        category=str(data.get("category") or ""),
        tags=[str(t) for t in tags],
        source_url=str(data.get("source_url") or ""),
    )


def load_recipes_from_json(path: Path) -> list[CroustillantRecipe]:
    """Charge un tableau JSON de recettes (même format que l'export --dry-run)."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("le JSON doit être un tableau [...] de recettes")

    recipes: list[CroustillantRecipe] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            log.warning("Entrée %s ignorée (objet attendu)", i)
            continue
        try:
            recipes.append(recipe_from_export_dict(item))
        except ValueError as err:
            log.warning("Entrée %s ignorée: %s", i, err)

    return recipes


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
                    href = a_tag.get("href")
                    if not href:
                        continue
                    results.append({
                        "title": a_tag.get_text(strip=True),
                        "url": str(href),
                    })

    return results


def probe_url_http_status(url: str) -> tuple[Optional[int], str]:
    """GET en streaming pour obtenir le code final après redirections."""
    clean = normalize_bookmark_url(url)
    session = http_session()
    try:
        resp = session.get(
            clean,
            allow_redirects=True,
            timeout=(5, 12),
            stream=True,
        )
        code = resp.status_code
        resp.close()
        return code, ""
    except requests.RequestException as exc:
        return None, str(exc)


def parse_prune_codes(raw: str) -> set[int]:
    """Codes HTTP à considérés comme « morts » pour --prune-bookmarks."""
    out: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.add(int(part))
        except ValueError:
            log.warning("Code HTTP ignoré : %s", part)
    return out if out else {404, 410}


def prune_bookmarks_json_data(
    data: dict,
    folder_name: str,
    dead_urls: set[str],
) -> dict:
    """
    Copie profonde du JSON Bookmarks avec les favoris `url` retirés
    (dans le dossier cible uniquement, même logique que l'extraction).
    """
    out = copy.deepcopy(data)
    for root_key in out.get("roots", {}):
        root_node = out["roots"][root_key]
        if isinstance(root_node, dict):
            _prune_bookmark_node(root_node, folder_name, dead_urls, False)
    return out


def _prune_bookmark_node(
    node: dict,
    folder_name: str,
    dead_urls: set[str],
    in_target: bool,
) -> None:
    target = folder_name.lower()
    node_type = node.get("type", "")
    name = node.get("name", "").lower()

    if node_type == "folder" and target in name:
        in_target = True

    children = node.get("children")
    if not children:
        return

    new_children: list = []
    for child in children:
        if not isinstance(child, dict):
            new_children.append(child)
            continue
        ct = child.get("type", "")
        if ct == "url" and in_target:
            u = child.get("url", "")
            if u in dead_urls:
                log.info(
                    "  Supprimé : %s",
                    (u[:100] + "…") if len(u) > 100 else u,
                )
                continue
        if ct == "folder":
            _prune_bookmark_node(child, folder_name, dead_urls, in_target)
        new_children.append(child)
    node["children"] = new_children


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
    """Télécharge et scrape une URL de recette (schema.org / JSON-LD Recipe)."""
    clean_url = normalize_bookmark_url(url)
    if clean_url != url:
        log.info("    (URL nettoyée) %s", clean_url)

    try:
        session = http_session()
        response = session.get(
            clean_url,
            timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        log.warning("  ✗ HTTP error pour %s: %s", clean_url, e)
        return None

    try:
        scraper = scrape_html(
            html=response.text,
            org_url=clean_url,
            supported_only=False,
        )
    except WebsiteNotImplementedError as e:
        log.warning("  ✗ Domaine non supporté par recipe-scrapers: %s", e)
        return None
    except (NoSchemaFoundInWildMode, RecipeSchemaNotFound) as e:
        log.warning(
            "  ✗ Pas de schéma Recipe sur la page (article non recette, DIY, produit, ou site sans JSON-LD): %s",
            e,
        )
        return None
    except Exception as e:
        log.warning("  ✗ Erreur recipe-scrapers pour %s: %s", clean_url, e)
        return None

    try:
        titre = scraper.title() or urlparse(clean_url).path.strip("/").replace("-", " ").title()
    except Exception:
        titre = urlparse(clean_url).path.strip("/").replace("-", " ").title()

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
        host = urlparse(clean_url).hostname or ""
        host_clean = host.replace("www.", "")
        if host_clean:
            tags.append(host_clean)
    except Exception:
        pass
    if category:
        tags.append(category)

    if not ingredients and not instructions:
        log.warning(
            "  ✗ Extraction vide (ingrédients et instructions) — %s",
            clean_url,
        )
        return None

    try:
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
            source_url=clean_url,
        )
    except Exception as e:
        log.warning("  ✗ Erreur inattendue pour %s: %s", clean_url, e)
        return None


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
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        metavar="N",
        help="Limiter le nombre d'URLs à traiter (tests / sous-ensemble)",
    )
    parser.add_argument(
        "--from-json",
        metavar="FILE",
        default=None,
        help="Importer un JSON déjà exporté (--dry-run) dans la BD sans re-scraper",
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Vérifier chaque URL (HTTP) : affiche le code statut ; ne scrape pas les recettes",
    )
    parser.add_argument(
        "--prune-bookmarks",
        metavar="FICHIER_SORTIE",
        default=None,
        help="Avec --check-urls : écrire une copie du Bookmarks JSON sans les liens aux codes "
        "--prune-codes. Fermer Chrome avant de remplacer le fichier source.",
    )
    parser.add_argument(
        "--prune-codes",
        default="404,410",
        help="Codes HTTP retirés lors du prune (défaut: 404,410). Ex: 404,410,451",
    )

    args = parser.parse_args()

    if args.prune_bookmarks and not args.check_urls:
        parser.error("--prune-bookmarks requiert --check-urls")
    if args.prune_bookmarks and args.html:
        parser.error("--prune-bookmarks nécessite le fichier Bookmarks JSON Chrome (omettre --html)")
    if args.check_urls and args.from_json is not None:
        parser.error("--check-urls est incompatible avec --from-json")

    if args.check_urls:
        log.info("Vérification HTTP des favoris (dossier '%s')...", args.folder)
        bookmark_file: Optional[Path] = None
        if args.html:
            html_path = Path(args.html)
            if not html_path.exists():
                log.error("Fichier HTML introuvable : %s", html_path)
                sys.exit(1)
            bookmarks = extract_urls_from_bookmarks_html(html_path, args.folder)
        else:
            if args.bookmarks:
                bookmark_file = Path(args.bookmarks)
            else:
                bookmark_file = find_chrome_bookmarks_path()
            log.info("  Fichier Bookmarks : %s", bookmark_file)
            bookmarks = extract_urls_from_bookmarks_json(bookmark_file, args.folder)

        if not bookmarks:
            log.warning(
                "Aucun favori dans le dossier '%s'. Vérifiez --folder.",
                args.folder,
            )
            if bookmark_file is not None:
                _show_available_folders(bookmark_file)
            sys.exit(0)

        if args.max is not None and args.max > 0:
            bookmarks = bookmarks[: args.max]
            log.info("  (limité à %s URLs via --max)", len(bookmarks))

        prune_codes = parse_prune_codes(args.prune_codes)
        dead_urls: set[str] = set()
        err_n = 0
        dead_n = 0

        for i, bk in enumerate(bookmarks, 1):
            title = bk["title"]
            code, err_msg = probe_url_http_status(bk["url"])
            if code is None:
                err_n += 1
                log.warning(
                    "  [%s/%s] ERREUR — %s — %s",
                    i,
                    len(bookmarks),
                    title[:60],
                    err_msg[:80],
                )
            elif code in prune_codes:
                dead_n += 1
                dead_urls.add(bk["url"])
                log.warning(
                    "  [%s/%s] %s → %s (sera retiré si prune)",
                    i,
                    len(bookmarks),
                    code,
                    (title[:50] + "…") if len(title) > 50 else title,
                )
            else:
                log.info(
                    "  [%s/%s] %s → %s",
                    i,
                    len(bookmarks),
                    code,
                    (title[:50] + "…") if len(title) > 50 else title,
                )

            if i < len(bookmarks):
                time.sleep(args.delay)

        log.info(
            "Résumé : %s liens testés, %s erreurs réseau/timeout, "
            "%s à retirer (codes %s)",
            len(bookmarks),
            err_n,
            dead_n,
            sorted(prune_codes),
        )

        if args.prune_bookmarks:
            if bookmark_file is None:
                log.error("Fichier Bookmarks introuvable pour --prune-bookmarks.")
                sys.exit(1)
            out_path = Path(args.prune_bookmarks)
            with open(bookmark_file, encoding="utf-8") as f:
                full_data = json.load(f)
            pruned = prune_bookmarks_json_data(
                full_data, args.folder, dead_urls
            )
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(pruned, f, ensure_ascii=False)
            log.info(
                "Copie écrite : %s (%s favori(s) retiré(s)). "
                "Fermez Chrome, puis remplacez le fichier Bookmarks si besoin.",
                out_path,
                len(dead_urls),
            )
        sys.exit(0)

    if args.from_json is not None:
        if args.html is not None or args.bookmarks is not None:
            parser.error(
                "--from-json est incompatible avec --html et --bookmarks"
            )
        path = Path(args.from_json)
        if not path.is_file():
            log.error("Fichier introuvable : %s", path)
            sys.exit(1)
        try:
            recipes = load_recipes_from_json(path)
        except json.JSONDecodeError as e:
            log.error("JSON invalide : %s", e)
            sys.exit(1)
        except ValueError as e:
            log.error("%s", e)
            sys.exit(1)

        log.info("%s recette(s) chargée(s) depuis %s", len(recipes), path)
        if not recipes:
            log.warning("Aucune recette valide. Arrêt.")
            sys.exit(0)

        if args.dry_run:
            log.info(
                "Dry-run : pas d'insertion en base (fichier déjà relu / validé)."
            )
            sys.exit(0)

        db_url = args.database_url or os.environ.get("DATABASE_URL")
        if not db_url:
            log.error(
                "DATABASE_URL non définie pour l'import. "
                "Utilisez --database-url ou la variable d'environnement."
            )
            sys.exit(1)

        log.info("Insertion dans Neon DB...")
        inserted, errs = insert_recipes_to_neon(recipes, db_url)
        log.info("  ✓ %s traitées en base, %s erreurs", inserted, errs)
        sys.exit(0)

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

    if args.max is not None and args.max > 0:
        bookmarks = bookmarks[: args.max]
        log.info("  (limité à %s URLs via --max)", len(bookmarks))

    log.info("Scraping des recettes...")
    recipes: list[CroustillantRecipe] = []
    failed_urls: list[str] = []

    for i, bk in enumerate(bookmarks, 1):
        url = bk["url"]
        title = bk["title"]
        log.info("  [%s/%s] %s", i, len(bookmarks), title)
        log.info("    → %s", url)

        try:
            recipe = scrape_recipe(url)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            log.warning("  ✗ Erreur inattendue: %s", e)
            failed_urls.append(url)
            recipe = None

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
        db_url = args.database_url or os.environ.get("DATABASE_URL")
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
