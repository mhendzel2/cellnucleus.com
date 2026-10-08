#!/usr/bin/env python3
"""Local-only public preview; no PHP execution, private directories or listing.

python preview_candidate.py --root cellnucleus-candidate --port 8765
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ALLOWED_DIRS = {"assets", "nuclear_biology_reviews", "hypothesis_reviews", "Reviews_useredit"}
ALLOWED_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".mp4", ".webm", ".pdf", ".docx"}
BLOCKED_PARTS = {".git", ".agents", ".codex", ".aws", ".venv", ".secrets", "admin", "output", "inbox", "skills", "docs", "reports", "node_modules", "config", "scripts", "backup", "backups"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = args.root.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *params, **kwargs):
            super().__init__(*params, directory=str(root), **kwargs)

        def is_public(self):
            target = (root / unquote(urlsplit(self.path).path).lstrip("/")).resolve()
            try:
                rel = target.relative_to(root)
            except ValueError:
                return False
            if any(part.startswith(".") or part in BLOCKED_PARTS for part in rel.parts):
                return False
            if any("genspark" in part.lower() for part in rel.parts) or (rel.parts and rel.parts[0].lower().startswith("nuclear speckles_")):
                return False
            if target.is_dir():
                target = target / "index.html"
                rel = target.relative_to(root)
            if len(rel.parts) == 1:
                return target.suffix.lower() == ".html" or rel.name in {"robots.txt", "sitemap.xml"}
            return rel.parts[0] in ALLOWED_DIRS and target.suffix.lower() in ALLOWED_SUFFIXES

        def do_GET(self):
            if not self.is_public():
                self.send_error(404)
                return
            super().do_GET()

        def do_HEAD(self):
            if not self.is_public():
                self.send_error(404)
                return
            super().do_HEAD()

        def list_directory(self, path):
            self.send_error(404)
            return None

    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"Public candidate preview: http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
