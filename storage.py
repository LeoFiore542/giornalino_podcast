"""Local media storage for giornalino (PDF) and podcast (MP3).

Layout:
  media/giornalino/<slug>/meta.json  + issue.pdf  + cover.jpg (optional)
  media/podcast/<slug>/meta.json     + audio.mp3  + cover.jpg (optional)
  media/podcast/<categoria>/<slug>/  # sottocategorie (es. speciale-elezioni/lista-1)
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

MEDIA_ROOT = Path(__file__).resolve().parent / "media"
SLUG_PART = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".mp3",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
}

MAIN_FILE = {
    "giornalino": "issue.pdf",
    "podcast": "audio.mp3",
}

MAIN_EXTENSIONS = {
    "giornalino": {".pdf"},
    "podcast": {".mp3"},
}

COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

MONTHS_IT = (
    "",
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)


def date_label_it(iso_date: str) -> str:
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
    except ValueError:
        return iso_date
    return f"{dt.day} {MONTHS_IT[dt.month]} {dt.year}"


def _safe_name(name: str | None) -> str | None:
    if not name:
        return None
    name = Path(name).name
    if name in {".", ".."} or "/" in name or "\\" in name:
        return None
    if Path(name).suffix.lower() not in ALLOWED_EXTENSIONS:
        return None
    return name


def _safe_slug(slug: str) -> str | None:
    """Single path segment slug (giornalino / episodio top-level)."""
    slug = Path(slug).name.strip().lower()
    if not SLUG_PART.fullmatch(slug):
        return None
    return slug


def _safe_relpath(relpath: str) -> str | None:
    """Relative path under kind root, e.g. speciale-elezioni/lista-1."""
    raw = str(relpath or "").strip().replace("\\", "/").strip("/")
    if not raw or raw.startswith(".") or ".." in raw.split("/"):
        return None
    parts = [p for p in raw.split("/") if p]
    if not parts or not all(SLUG_PART.fullmatch(p) for p in parts):
        return None
    return "/".join(parts)


def _load_meta(folder: Path) -> dict | None:
    meta_path = folder / "meta.json"
    if not meta_path.is_file():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _write_meta(folder: Path, meta: dict) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _file_url(kind: str, rel_slug: str, filename: str | None) -> str | None:
    safe = _safe_name(filename)
    safe_rel = _safe_relpath(rel_slug)
    if not safe or not safe_rel:
        return None
    path = MEDIA_ROOT / kind / Path(*safe_rel.split("/")) / safe
    if not path.is_file():
        return None
    try:
        from flask import has_request_context, url_for

        if has_request_context():
            return url_for("media_file", kind=kind, relpath=f"{safe_rel}/{safe}")
    except Exception:
        pass
    return f"/media/{kind}/{safe_rel}/{safe}"


def _cover_style(cover_url: str | None, cover_class: str) -> str:
    classes = ["media-cover", cover_class or "cover-default"]
    if cover_url:
        classes.append("has-image")
    return " ".join(classes)


def _item_from_folder(kind: str, folder: Path, *, rel_slug: str | None = None) -> dict | None:
    meta = _load_meta(folder)
    if not meta:
        return None

    slug = rel_slug or folder.name
    safe_rel = _safe_relpath(slug)
    if not safe_rel:
        return None

    default_file = MAIN_FILE[kind]
    file_name = _safe_name(meta.get("file") or default_file) or default_file
    cover_name = _safe_name(meta.get("cover"))
    date = str(meta.get("date") or "")
    default_cover = "cover-spring" if kind == "giornalino" else "cover-mic"
    cover_class = str(meta.get("cover_class") or default_cover)
    file_url = _file_url(kind, safe_rel, file_name)
    cover_url = _file_url(kind, safe_rel, cover_name)

    item = {
        "slug": safe_rel,
        "kind": kind,
        "title": str(meta.get("title") or folder.name),
        "description": str(meta.get("description") or ""),
        "date": date,
        "date_label": date_label_it(date) if date else "",
        "cover_class": cover_class,
        "cover_url": cover_url,
        "cover_style": _cover_style(cover_url, cover_class),
        "file_name": file_name,
        "cover_name": cover_name,
        "file_url": file_url,
        "file_ready": file_url is not None,
        "cover_ready": cover_url is not None,
    }

    if kind == "giornalino":
        item["volume"] = int(meta.get("volume") or 0)
    else:
        item["episode"] = int(meta.get("episode") or 0)
        item["duration"] = str(meta.get("duration") or "")

    return item


def list_giornalini() -> list[dict]:
    root = MEDIA_ROOT / "giornalino"
    if not root.is_dir():
        return []

    items: list[dict] = []
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        item = _item_from_folder("giornalino", folder)
        if item:
            items.append(item)

    items.sort(key=lambda x: (x["date"], x["volume"]), reverse=True)
    return items


def _load_category(folder: Path) -> dict:
    meta_path = folder / "category.json"
    title = folder.name.replace("-", " ").strip().title()
    description = ""
    if meta_path.is_file():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                title = str(data.get("title") or title)
                description = str(data.get("description") or "")
        except (OSError, json.JSONDecodeError):
            pass
    return {"slug": folder.name, "title": title, "description": description}


def list_episodi() -> list[dict]:
    """Flat list of all podcast items (top-level + sottocategorie)."""
    sections = list_podcast_sections()
    items: list[dict] = []
    for section in sections:
        items.extend(section["items"])
    return items


def list_podcast_sections() -> list[dict]:
    """Podcast grouped by category. Top-level episodes use title 'Episodi'."""
    root = MEDIA_ROOT / "podcast"
    if not root.is_dir():
        return []

    general_items: list[dict] = []
    sections: list[dict] = []

    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue

        # Sottocategoria: cartella con figli che hanno meta.json
        child_items: list[dict] = []
        for child in sorted(folder.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            rel = f"{folder.name}/{child.name}"
            item = _item_from_folder("podcast", child, rel_slug=rel)
            if item:
                child_items.append(item)

        if child_items:
            child_items.sort(key=lambda x: (x["date"], x["episode"]))
            cat = _load_category(folder)
            sections.append(
                {
                    "slug": cat["slug"],
                    "title": cat["title"],
                    "description": cat["description"],
                    "items": child_items,
                }
            )
            continue

        item = _item_from_folder("podcast", folder)
        if item:
            general_items.append(item)

    general_items.sort(key=lambda x: (x["date"], x["episode"]), reverse=True)
    result: list[dict] = []
    if general_items:
        result.append(
            {
                "slug": "",
                "title": "Episodi",
                "description": "",
                "items": general_items,
            }
        )
    result.extend(sections)
    return result


def resolve_media_file(kind: str, relpath: str) -> Path | None:
    """Resolve media/<kind>/<relpath> where relpath includes folders + filename."""
    if kind not in {"giornalino", "podcast"}:
        return None
    safe_rel = _safe_relpath(relpath)
    if not safe_rel:
        return None
    parts = safe_rel.split("/")
    if len(parts) < 2:
        return None
    *dir_parts, filename = parts
    safe_file = _safe_name(filename)
    if not safe_file:
        return None
    folder = MEDIA_ROOT / kind / Path(*dir_parts)
    path = (folder / safe_file).resolve()
    root = (MEDIA_ROOT / kind).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def slug_for_volume(volume: int) -> str:
    return f"vol-{int(volume):02d}"


def slug_for_episode(episode: int) -> str:
    return f"ep-{int(episode):02d}"


def save_uploaded_main(kind: str, slug: str, upload) -> str:
    if kind not in MAIN_FILE:
        raise ValueError("Tipo non valido.")
    safe_slug = _safe_slug(slug)
    if not safe_slug:
        raise ValueError("Slug non valido.")

    folder = MEDIA_ROOT / kind / safe_slug
    meta = _load_meta(folder)
    if meta is None:
        raise ValueError("Voce non trovata.")

    original = _safe_name(upload.filename)
    if not original:
        raise ValueError("Nome file non valido.")
    ext = Path(original).suffix.lower()
    if ext not in MAIN_EXTENSIONS[kind]:
        expected = "PDF" if kind == "giornalino" else "MP3"
        raise ValueError(f"Per {kind} serve un file {expected}.")

    target_name = MAIN_FILE[kind]
    upload.save(folder / target_name)
    meta["file"] = target_name
    _write_meta(folder, meta)
    return target_name


def save_uploaded_cover(kind: str, slug: str, upload) -> str:
    if kind not in MAIN_FILE:
        raise ValueError("Tipo non valido.")
    safe_slug = _safe_slug(slug)
    if not safe_slug:
        raise ValueError("Slug non valido.")

    folder = MEDIA_ROOT / kind / safe_slug
    meta = _load_meta(folder)
    if meta is None:
        raise ValueError("Voce non trovata.")

    original = _safe_name(upload.filename)
    if not original:
        raise ValueError("Nome file non valido.")
    ext = Path(original).suffix.lower()
    if ext not in COVER_EXTENSIONS:
        raise ValueError("La copertina deve essere un'immagine (jpg, png, webp).")

    target_name = f"cover{ext}"
    old = _safe_name(meta.get("cover"))
    if old and old != target_name:
        old_path = folder / old
        if old_path.is_file():
            old_path.unlink()

    upload.save(folder / target_name)
    meta["cover"] = target_name
    _write_meta(folder, meta)
    return target_name


def delete_main_file(kind: str, slug: str) -> None:
    if kind not in MAIN_FILE:
        raise ValueError("Tipo non valido.")
    safe_slug = _safe_slug(slug)
    if not safe_slug:
        raise ValueError("Slug non valido.")

    folder = MEDIA_ROOT / kind / safe_slug
    meta = _load_meta(folder)
    if meta is None:
        raise ValueError("Voce non trovata.")

    file_name = _safe_name(meta.get("file") or MAIN_FILE[kind])
    if file_name:
        path = folder / file_name
        if path.is_file():
            path.unlink()


def delete_cover_file(kind: str, slug: str) -> None:
    if kind not in MAIN_FILE:
        raise ValueError("Tipo non valido.")
    safe_slug = _safe_slug(slug)
    if not safe_slug:
        raise ValueError("Slug non valido.")

    folder = MEDIA_ROOT / kind / safe_slug
    meta = _load_meta(folder)
    if meta is None:
        raise ValueError("Voce non trovata.")

    cover_name = _safe_name(meta.get("cover"))
    if cover_name:
        path = folder / cover_name
        if path.is_file():
            path.unlink()
        meta.pop("cover", None)
        _write_meta(folder, meta)


def create_giornalino(
    *,
    volume: int,
    title: str,
    description: str,
    date: str,
    cover_class: str = "cover-spring",
) -> str:
    volume = int(volume)
    if volume < 1:
        raise ValueError("Il volume deve essere almeno 1.")
    slug = slug_for_volume(volume)
    folder = MEDIA_ROOT / "giornalino" / slug
    if folder.exists() and (folder / "meta.json").is_file():
        raise ValueError(f"Esiste già {slug}.")

    meta = {
        "volume": volume,
        "title": title.strip() or f"Volume {volume}",
        "description": description.strip(),
        "date": date.strip(),
        "cover_class": cover_class.strip() or "cover-spring",
        "file": MAIN_FILE["giornalino"],
        "cover": "cover.jpg",
    }
    _write_meta(folder, meta)
    gitignore = folder / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!meta.json\n!.gitignore\n", encoding="utf-8")
    return slug


def create_episodio(
    *,
    episode: int,
    title: str,
    description: str,
    date: str,
    duration: str = "",
    cover_class: str = "cover-mic",
) -> str:
    episode = int(episode)
    if episode < 1:
        raise ValueError("L'episodio deve essere almeno 1.")
    slug = slug_for_episode(episode)
    folder = MEDIA_ROOT / "podcast" / slug
    if folder.exists() and (folder / "meta.json").is_file():
        raise ValueError(f"Esiste già {slug}.")

    meta = {
        "episode": episode,
        "title": title.strip() or f"Episodio {episode}",
        "description": description.strip(),
        "date": date.strip(),
        "duration": duration.strip(),
        "cover_class": cover_class.strip() or "cover-mic",
        "file": MAIN_FILE["podcast"],
        "cover": "cover.jpg",
    }
    _write_meta(folder, meta)
    gitignore = folder / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!meta.json\n!.gitignore\n", encoding="utf-8")
    return slug


def next_volume_number() -> int:
    items = list_giornalini()
    if not items:
        return 1
    return max(item["volume"] for item in items) + 1


def next_episode_number() -> int:
    items = list_episodi()
    if not items:
        return 1
    return max(item["episode"] for item in items) + 1


def today_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def publish_item(
    *,
    kind: str,
    number: int,
    title: str,
    description: str,
    main_upload,
    cover_upload=None,
    duration: str = "",
) -> str:
    """Create or update an item, set today's date, save main file and optional cover."""
    if kind not in MAIN_FILE:
        raise ValueError("Scegli Giornalino o Podcast.")
    number = int(number)
    if number < 1:
        raise ValueError("Il numero deve essere almeno 1.")
    if not main_upload or not main_upload.filename:
        raise ValueError("Carica il file del corpo (PDF o MP3).")

    date = today_iso()
    if kind == "giornalino":
        slug = slug_for_volume(number)
        folder = MEDIA_ROOT / "giornalino" / slug
        cover_class = "cover-spring"
        meta = {
            "volume": number,
            "title": title.strip() or f"Volume {number}",
            "description": description.strip(),
            "date": date,
            "cover_class": cover_class,
            "file": MAIN_FILE["giornalino"],
            "cover": "cover.jpg",
        }
    else:
        slug = slug_for_episode(number)
        folder = MEDIA_ROOT / "podcast" / slug
        cover_class = "cover-mic"
        meta = {
            "episode": number,
            "title": title.strip() or f"Episodio {number}",
            "description": description.strip(),
            "date": date,
            "duration": duration.strip(),
            "cover_class": cover_class,
            "file": MAIN_FILE["podcast"],
            "cover": "cover.jpg",
        }

    _write_meta(folder, meta)
    gitignore = folder / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!meta.json\n!.gitignore\n", encoding="utf-8")

    save_uploaded_main(kind, slug, main_upload)
    if cover_upload and cover_upload.filename:
        save_uploaded_cover(kind, slug, cover_upload)

    return slug


def delete_item(kind: str, slug: str) -> None:
    if kind not in MAIN_FILE:
        raise ValueError("Tipo non valido.")
    safe_slug = _safe_slug(slug)
    if not safe_slug:
        raise ValueError("Slug non valido.")
    folder = MEDIA_ROOT / kind / safe_slug
    if not folder.is_dir():
        raise ValueError("Voce non trovata.")
    for path in folder.iterdir():
        if path.is_file():
            path.unlink()
    folder.rmdir()
