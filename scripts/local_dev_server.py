# Serveur de développement local : fichiers statiques (public/) + API Netlify (handlers Python).
# Netlify CLI n'exécute pas les fonctions Python en local ; ce script reproduit /api/* sur le même port.

from __future__ import annotations

import argparse
import importlib.util
import mimetypes
import sys
from types import ModuleType
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
FUNC_DIR = ROOT / "netlify" / "functions-python"


def _load_module(filename: str, as_name: str):
    path = FUNC_DIR / filename
    spec = importlib.util.spec_from_file_location(as_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ensure_functions_path() -> None:
    if str(FUNC_DIR) not in sys.path:
        sys.path.insert(0, str(FUNC_DIR))


def _build_event(
    method: str,
    path: str,
    query_string: str,
    body: str | None,
) -> dict:
    qparams = parse_qs(query_string)
    query_string_parameters = {k: v[0] for k, v in qparams.items()} if qparams else None
    return {
        "httpMethod": method,
        "path": path,
        "queryStringParameters": query_string_parameters,
        "body": body,
        "headers": {},
    }


class DevHandler(BaseHTTPRequestHandler):
    _recipes: ModuleType | None = None
    _recipe_detail: ModuleType | None = None
    _shopping_list: ModuleType | None = None

    @classmethod
    def _handlers(cls) -> tuple[ModuleType, ModuleType, ModuleType]:
        if cls._recipes is None:
            _ensure_functions_path()
            cls._recipes = _load_module("recipes.py", "recipes_mod")
            cls._recipe_detail = _load_module("recipe-detail.py", "recipe_detail_mod")
            cls._shopping_list = _load_module("shopping-list.py", "shopping_list_mod")
        assert cls._recipes is not None
        assert cls._recipe_detail is not None
        assert cls._shopping_list is not None
        return cls._recipes, cls._recipe_detail, cls._shopping_list

    def log_message(self, format: str, *args) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    def _send_lambda_response(self, result: dict) -> None:
        status = int(result.get("statusCode", 500))
        self.send_response(status)
        for key, val in (result.get("headers") or {}).items():
            self.send_header(key, val)
        self.end_headers()
        body = result.get("body", "")
        if isinstance(body, str):
            self.wfile.write(body.encode("utf-8"))
        else:
            self.wfile.write(body)

    def _handle_api(self, path_only: str, query: str, body: str | None) -> bool:
        method = self.command.upper()
        recipes, recipe_detail, shopping_list = self._handlers()

        if path_only == "/api/recipes":
            event = _build_event(method, path_only, query, body)
            self._send_lambda_response(recipes.handler(event, {}))
            return True

        if path_only.startswith("/api/recipe-detail/"):
            event = _build_event(method, path_only, query, body)
            self._send_lambda_response(recipe_detail.handler(event, {}))
            return True

        if path_only == "/api/shopping-list":
            event = _build_event(method, path_only, query, body)
            self._send_lambda_response(shopping_list.handler(event, {}))
            return True

        self.send_error(404, "API route not found")
        return True

    def _safe_public_path(self, rel: str) -> Path | None:
        if rel == "" or rel == "/":
            return PUBLIC / "index.html"
        candidate = (PUBLIC / rel.lstrip("/")).resolve()
        try:
            candidate.relative_to(PUBLIC.resolve())
        except ValueError:
            return None
        return candidate

    def _serve_static(self) -> None:
        parsed = urlparse(self.path)
        path_only = parsed.path
        if path_only.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else None
            self._handle_api(path_only, parsed.query, body)
            return

        target = self._safe_public_path(path_only)
        if target is None:
            self.send_error(403)
            return

        if self.command.upper() != "GET":
            self.send_error(405)
            return

        if target.is_file():
            self._send_file(target)
            return

        index = PUBLIC / "index.html"
        if index.is_file():
            self._send_file(index)
            return

        self.send_error(404)

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        ctype, _ = mimetypes.guess_type(str(path))
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        self._serve_static()

    def do_POST(self) -> None:
        self._serve_static()

    def do_PUT(self) -> None:
        self._serve_static()

    def do_DELETE(self) -> None:
        self._serve_static()

    def do_OPTIONS(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            recipes, _, _ = self._handlers()
            event = _build_event("OPTIONS", parsed.path, parsed.query, None)
            self._send_lambda_response(recipes.handler(event, {}))
            return
        self.send_response(204)
        self.end_headers()


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Croustillant local dev (static + API).")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8888, help="Port (default: 8888)")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DevHandler)
    print(f"Croustillant local dev: http://localhost:{args.port}/")
    print("  (static + API Python; DATABASE_URL required in .env)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
