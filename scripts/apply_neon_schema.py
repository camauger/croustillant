#!/usr/bin/env python3
# Applique neon-schema.sql sur la base pointée par DATABASE_URL (.env).

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = REPO_ROOT / "neon-schema.sql"


def load_project_env() -> None:
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


def split_pg_sql(text: str) -> list[str]:
    """Découpe le script en instructions (; hors blocs $$ ... $$)."""
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(text)
    in_dollar = False
    while i < n:
        if i + 1 < n and text[i : i + 2] == "$$":
            in_dollar = not in_dollar
            buf.append("$$")
            i += 2
            continue
        if text[i] == ";" and not in_dollar:
            stmt = "".join(buf).strip()
            if stmt:
                parts.append(stmt)
            buf = []
            i += 1
            continue
        buf.append(text[i])
        i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def main() -> int:
    load_project_env()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Erreur: définissez DATABASE_URL dans .env ou l'environnement.")
        return 1

    if not SCHEMA_FILE.is_file():
        print(f"Fichier introuvable: {SCHEMA_FILE}")
        return 1

    try:
        import psycopg2
    except ImportError:
        print("Erreur: pip install psycopg2-binary")
        return 1

    sql_text = SCHEMA_FILE.read_text(encoding="utf-8")
    statements = split_pg_sql(sql_text)

    try:
        conn = psycopg2.connect(url, connect_timeout=30)
    except Exception as e:
        print(f"Connexion impossible: {e}")
        return 1

    conn.autocommit = True
    n_ok = 0
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                s = stmt.strip()
                if not s:
                    continue
                if not any(
                    ln.strip() and not ln.strip().startswith("--")
                    for ln in s.splitlines()
                ):
                    continue
                cur.execute(s)
                n_ok += 1
    except Exception as e:
        print(f"Erreur SQL (instruction ~{n_ok + 1}): {e}")
        return 1
    finally:
        conn.close()

    print(f"Schéma appliqué ({n_ok} instruction(s)) — table recipes et index prêts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
