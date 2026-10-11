# Voci di corridoio — Giornalino & Podcast

Sito Flask per il giornalino e il podcast della scuola Antonio Labriola.

## Struttura

```
app.py                 # route Flask
storage.py             # lettura archivio media da disco
wsgi.py                # entrypoint PythonAnywhere
media/
  giornalino/<slug>/   # meta.json + issue.pdf + cover.jpg
  podcast/<slug>/      # meta.json + audio.mp3 + cover.jpg
static/                # css, js, favicon
templates/
```

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

In futuro la cartella `media/` può essere riempita da un sync Google Drive.

## Area Storage (admin)

Nella nav c’è **Storage**: apre un popup password; solo con password corretta si entra nella dashboard (PDF/MP3).

Password di default (solo sviluppo): `vocidicorridoio`  

Su PythonAnywhere impostala così (Bash, poi Reload):
```bash
# nel Virtualenv / file WSGI, oppure:
echo 'export STORAGE_PASSWORD="tua-password-sicura"' >> ~/.bashrc
echo 'export SECRET_KEY="una-chiave-segreta-lunga"' >> ~/.bashrc
```
Oppure aggiungi le variabili d’ambiente nel pannello Web di PA se disponibile.

## Route

| URL | Pagina |
|-----|--------|
| `/` | Landing |
| `/giornalino` | Archivio giornalino |
| `/podcast` | Archivio podcast |
| `/media/...` | File PDF / MP3 / copertine |
| `/privacy` `/accessibilita` `/note-legali` | Pagine legali |

## Setup locale

```bash
cd giornalino_podcast
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
