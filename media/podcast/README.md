# Podcast

## Episodi normali

Cartella diretta, es. `ep-01/` con:

- `meta.json` (obbligatorio)
- `audio.mp3`
- `cover.jpg` (opzionale)

## Sottocategorie

Es. **Speciale elezioni**:

```
speciale-elezioni/
  category.json
  lista-1/meta.json + audio.mp3
  lista-2/...
```

## Esempio meta.json

```json
{
  "episode": 1,
  "title": "Titolo",
  "description": "...",
  "date": "2026-01-15",
  "duration": "12:05",
  "cover_class": "cover-mic",
  "file": "audio.mp3",
  "cover": "cover.jpg"
}
```
