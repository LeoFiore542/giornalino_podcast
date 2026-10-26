#!/usr/bin/env python3
"""Build a static export of the public site for GitHub Pages.

GitHub Pages cannot run Flask. This script renders the public templates and
copies static/ + media/ into ./site ready to publish.

Environment:
  BASE_PATH   URL prefix for project pages (default: /giornalino_podcast).
              Use empty string for a custom domain at the site root.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "site"
DEFAULT_BASE = "/giornalino_podcast"

# Must be set before importing the Flask app.
os.environ["STATIC_EXPORT"] = "1"
BASE_PATH = os.environ.get("BASE_PATH", DEFAULT_BASE).rstrip("/")
os.environ["BASE_PATH"] = BASE_PATH

from app import app  # noqa: E402

PAGES: list[tuple[str, str]] = [
    ("/", "index.html"),
    ("/giornalino", "giornalino/index.html"),
    ("/podcast", "podcast/index.html"),
    ("/chi-siamo", "chi-siamo/index.html"),
    ("/redazione", "redazione/index.html"),  # alias storico
    ("/privacy", "privacy/index.html"),
    ("/accessibilita", "accessibilita/index.html"),
    ("/note-legali", "note-legali/index.html"),
]


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.is_dir():
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(".gitignore", ".DS_Store", "._*", "__pycache__"),
    )


def build() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    environ = {"SCRIPT_NAME": BASE_PATH} if BASE_PATH else {}

    with app.test_client() as client:
        for url, relpath in PAGES:
            response = client.get(url, environ_overrides=environ)
            if response.status_code != 200:
                print(
                    f"ERROR: {url} -> HTTP {response.status_code}",
                    file=sys.stderr,
                )
                return 1
            _write(DEST / relpath, response.data)
            print(f"OK  {url} -> {relpath}")

    _copy_tree(ROOT / "static", DEST / "static")
    _copy_tree(ROOT / "media", DEST / "media")
    (DEST / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Built static site in {DEST} (BASE_PATH={BASE_PATH!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
