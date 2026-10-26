# Voci dal corridoio — Giornalino & Podcast

Sito Flask per il giornalino e il podcast della scuola Antonio Labriola.  
Su GitHub Pages viene pubblicato un **export statico**.

## Struttura

```
app.py                 # route Flask
build_static.py        # export statico per GitHub Pages
storage.py             # lettura archivio media da disco
wsgi.py                # entrypoint PythonAnywhere (opzionale)
media/
  giornalino/<slug>/   # meta.json + issue.pdf + cover.jpg
  podcast/<slug>/      # meta.json + audio.mp3 + cover.jpg
  redazione/           # members.json + foto
static/
templates/
.github/workflows/     # deploy automatico su GitHub Pages
```

## Caricare PDF e MP3 (via GitHub)

1. Crea una cartella sotto `media/giornalino/` o `media/podcast/` (es. `vol-01`, `ep-01`)
2. Aggiungi `meta.json` e i file (`issue.pdf` / `audio.mp3`, copertina opzionale)
3. Commit e push: il workflow aggiorna Pages

Istruzioni dettagliate stanno anche in `media/giornalino/README.md` e `media/podcast/README.md`.

## GitHub Pages

1. Source: **GitHub Actions**
2. URL: `https://leofiore542.github.io/giornalino_podcast/`

Build locale:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BASE_PATH=/giornalino_podcast python build_static.py
```

## Setup locale (Flask)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Apri [http://127.0.0.1:5001](http://127.0.0.1:5001).

## Route

| URL | Pagina |
|-----|--------|
| `/` | Landing |
| `/giornalino` | Archivio giornalino |
| `/podcast` | Archivio podcast |
| `/chi-siamo` | Redazione |
| `/media/...` | File PDF / MP3 / copertine |
| `/privacy` `/accessibilita` `/note-legali` | Pagine legali |
