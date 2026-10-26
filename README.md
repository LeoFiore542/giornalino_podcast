# Voci dal corridoio — Giornalino & Podcast

Sito Flask per il giornalino e il podcast della scuola Antonio Labriola.

## Struttura

```
app.py                 # route Flask (sviluppo / hosting dinamico)
build_static.py        # export statico per GitHub Pages
storage.py             # lettura archivio media da disco
wsgi.py                # entrypoint PythonAnywhere
media/
  giornalino/<slug>/   # meta.json + issue.pdf + cover.jpg
  podcast/<slug>/      # meta.json + audio.mp3 + cover.jpg
static/                # css, js, favicon
templates/
.github/workflows/     # deploy automatico su GitHub Pages
```

## GitHub Pages

Il sito pubblico è un **export statico** (Pages non esegue Python).

1. In GitHub: **Settings → Pages → Source: GitHub Actions**
2. Il workflow `.github/workflows/pages.yml` builda e pubblica a ogni push su `main`
3. URL tipico: `https://leofiore542.github.io/giornalino_podcast/`

**Nota:** con un account gratuito Pages funziona su repo **pubbliche**. Se il repo è privato serve un piano a pagamento, oppure rendilo pubblico.

Build locale dell’export:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BASE_PATH=/giornalino_podcast python build_static.py
```

L’output è in `site/` (non va in git). Su Pages l’area Storage/admin **non c’è**: per caricare PDF/MP3 usa Flask in locale o PythonAnywhere, poi committa i `meta.json` (e i media se non sono ignorati).

## Storage file

Ogni numero/episodio è una cartella con `meta.json` e i file binari.

Esempio giornalino (`media/giornalino/vol-03/`):

```json
{
  "volume": 3,
  "title": "Primavera in aula",
  "description": "...",
  "date": "2026-03-15",
  "cover_class": "cover-spring",
  "file": "issue.pdf",
  "cover": "cover.jpg"
}
```

Esempio podcast (`media/podcast/ep-01/`): stessi campi con `episode`, `duration`, `file: "audio.mp3"`.

- I PDF/MP3/immagini **non** sono in git (restano sul server o arrivano da Drive).
- Se manca il file, la scheda resta visibile con “PDF/Audio in arrivo”.
- I file pubblicati sono serviti da `/media/...`.

## Area Storage (admin, solo Flask)

Nella nav desktop c’è un’icona lucchetto; solo con password si entra nella dashboard.

Password di default (solo sviluppo): `vocidalcorridoio`

Su PythonAnywhere impostala così (Bash, poi Reload):

```bash
echo 'export STORAGE_PASSWORD="tua-password-sicura"' >> ~/.bashrc
echo 'export SECRET_KEY="una-chiave-segreta-lunga"' >> ~/.bashrc
```

## Route

| URL | Pagina |
|-----|--------|
| `/` | Landing |
| `/giornalino` | Archivio giornalino |
| `/podcast` | Archivio podcast |
| `/chi-siamo` | Redazione |
| `/media/...` | File PDF / MP3 / copertine |
| `/privacy` `/accessibilita` `/note-legali` | Pagine legali |

## Setup locale (Flask)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Apri [http://127.0.0.1:5001](http://127.0.0.1:5001) (porta 5001 per evitare il conflitto macOS/AirPlay sulla 5000).

## Deploy su PythonAnywhere

1. Carica/clona il progetto.
2. Virtualenv + `pip install -r requirements.txt`.
3. Web app Manual configuration: source code, virtualenv, WSGI.
4. (Consigliato) Static files: `/static/` → `.../static`.
5. I media restano in `media/` sul server (upload Files o sync).
6. Reload.

WSGI tipico:

```python
import sys
path = "/home/<utente>/giornalino_podcast"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```
