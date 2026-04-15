#!/usr/bin/env python3
# Valide la connexion Neon et le schéma attendu par Croustillant.

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        env_path = REPO_ROOT / ".env"
        if not env_path.is_file():
            return
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1].replace('\\"', '"')
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            if key and key not in os.environ:
                os.environ[key] = val
    else:
        load_dotenv(REPO_ROOT / ".env")


EXPECTED_COLUMNS = {
    "id": "bigint",
    "titre": "text",
    "temps_preparation": "text",
    "temps_cuisson": "text",
    "rendement": "text",
    "ingredients": "jsonb",
    "instructions": "jsonb",
    "image_url": "text",
    "category": "text",
    "tags": "ARRAY",
    "source_url": "text",
    "created_at": "timestamp with time zone",
    "updated_at": "timestamp with time zone",
}

EXPECTED_INDEXES = {
    "idx_recipes_titre",
    "idx_recipes_category",
    "idx_recipes_ingredients",
    "idx_recipes_tags",
}


def main() -> int:
    _load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Erreur: DATABASE_URL manquant (fichier .env ou env).")
        return 1

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("Erreur: installez psycopg2-binary (pip install -r netlify/functions-python/requirements.txt)")
        return 1

    parsed = urlparse(url)
    host = parsed.hostname or "?"
    dbname = (parsed.path or "").lstrip("/") or "(default)"
    print(f"Connexion à l'hôte Neon : {host} (base: {dbname})")

    try:
        conn = psycopg2.connect(url, connect_timeout=15)
    except Exception as e:
        print(f"Échec de connexion: {e}")
        return 1

    ok = True
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT version() AS v, current_database() AS db")
        row = cur.fetchone() or {}
        ver = (row.get("v") or "?").split(",")[0]
        print(f"  PostgreSQL : {ver}")
        print(f"  Base active : {row.get('db', '?')}")

        cur.execute(
            """
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'recipes'
            ORDER BY ordinal_position
            """
        )
        cols = {r["column_name"]: r for r in cur.fetchall()}
        if not cols:
            print("ERREUR: la table public.recipes est absente. Exécutez neon-schema.sql dans Neon.")
            ok = False
        else:
            missing = set(EXPECTED_COLUMNS) - set(cols)
            if missing:
                print(f"ERREUR: colonnes manquantes: {sorted(missing)}")
                ok = False
            else:
                print(f"  Colonnes attendues : {len(EXPECTED_COLUMNS)}/{len(EXPECTED_COLUMNS)}")

        cur.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = 'recipes'
            """
        )
        idx_names = {r["indexname"] for r in cur.fetchall()}
        missing_idx = EXPECTED_INDEXES - idx_names
        if missing_idx:
            print(f"ATTENTION: index manquants sur recipes: {sorted(missing_idx)}")
            ok = False
        else:
            print(f"  Index présents : {len(EXPECTED_INDEXES)}/{len(EXPECTED_INDEXES)}")

        cur.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM pg_trigger t
                JOIN pg_class c ON c.oid = t.tgrelid
                WHERE c.relname = 'recipes' AND NOT t.tgisinternal
                  AND t.tgname = 'update_recipes_updated_at'
            ) AS trig_ok
            """
        )
        trig = cur.fetchone()
        if trig and not trig["trig_ok"]:
            print("ATTENTION: déclencheur update_recipes_updated_at introuvable sur recipes.")
            ok = False
        elif cols:
            print("  Déclencheur updated_at : présent")

        if cols:
            cur.execute("SELECT COUNT(*) AS n FROM recipes")
            count_row = cur.fetchone() or {}
            print(f"  Lignes dans recipes : {count_row.get('n', '?')}")

    conn.close()

    if ok:
        print("\nRésumé: schéma cohérent avec Croustillant (neon-schema.sql).")
        return 0
    print("\nRésumé: des problèmes détectés — appliquer ou corriger neon-schema.sql.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
