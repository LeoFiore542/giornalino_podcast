"""Redazione members loaded from media/redazione/members.json."""

from __future__ import annotations

import json
from pathlib import Path

MEDIA_ROOT = Path(__file__).resolve().parent / "media"
REDAZIONE_ROOT = MEDIA_ROOT / "redazione"
MEMBERS_FILE = REDAZIONE_ROOT / "members.json"
ALLOWED_ROLES = {"studente", "docente"}
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _safe_photo(name: str | None) -> str | None:
    if not name:
        return None
    name = Path(name).name
    if name in {".", ".."} or "/" in name or "\\" in name:
        return None
    if Path(name).suffix.lower() not in PHOTO_EXTENSIONS:
        return None
    return name


def list_redazione() -> list[dict]:
    REDAZIONE_ROOT.mkdir(parents=True, exist_ok=True)
    if not MEMBERS_FILE.is_file():
        return []

    try:
        data = json.loads(MEMBERS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    members: list[dict] = []
    for raw in data:
        if not isinstance(raw, dict):
            continue
        nome = str(raw.get("nome") or "").strip()
        cognome = str(raw.get("cognome") or "").strip()
        if not nome and not cognome:
            continue

        ruolo = str(raw.get("ruolo") or "studente").strip().lower()
        if ruolo not in ALLOWED_ROLES:
            ruolo = "studente"

        foto_name = _safe_photo(raw.get("foto"))
        foto_url = None
        if foto_name and (REDAZIONE_ROOT / foto_name).is_file():
            try:
                from flask import has_request_context, url_for

                if has_request_context():
                    foto_url = url_for("media_redazione", filename=foto_name)
                else:
                    foto_url = f"/media/redazione/{foto_name}"
            except Exception:
                foto_url = f"/media/redazione/{foto_name}"

        initials = "".join(part[0].upper() for part in (nome, cognome) if part)[:2] or "?"

        members.append(
            {
                "nome": nome,
                "cognome": cognome,
                "full_name": f"{nome} {cognome}".strip(),
                "email": str(raw.get("email") or "").strip(),
                "ruolo": ruolo,
                "ruolo_label": "Studente" if ruolo == "studente" else "Docente",
                "compito": str(raw.get("compito") or "").strip(),
                "foto_url": foto_url,
                "initials": initials,
            }
        )

    members.sort(key=lambda m: (m["cognome"].lower(), m["nome"].lower()))
    return members


def resolve_redazione_photo(filename: str) -> Path | None:
    safe = _safe_photo(filename)
    if not safe:
        return None
    path = (REDAZIONE_ROOT / safe).resolve()
    root = REDAZIONE_ROOT.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path
