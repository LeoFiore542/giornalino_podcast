# Voce Labriola — Giornalino & Podcast

Sito Flask per il giornalino e il podcast della scuola Antonio Labriola. Scheletro con landing e pagine placeholder, pronto per PythonAnywhere.

## Struttura

```
app.py              # applicativo Flask e route
wsgi.py             # entrypoint WSGI (PythonAnywhere)
requirements.txt
static/css|js       # asset
templates/          # Jinja2
```

## Route

| URL | Pagina |
|-----|--------|
| `/` | Landing |
| `/giornalino` | Giornalino (placeholder) |
| `/podcast` | Podcast (placeholder) |

## Setup locale

```bash
cd giornalino_podcast
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Apri [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Deploy su PythonAnywhere

1. Carica il progetto (es. `/home/<utente>/giornalino_podcast`).
2. Crea un virtualenv e installa le dipendenze: `pip install -r requirements.txt`.
3. Nel tab **Web**, crea una web app **Manual configuration** (Python 3.x) e punta:
   - **Source code** / working directory al percorso del progetto
   - **WSGI configuration file** a `wsgi.py` del progetto (o copia il contenuto di `wsgi.py` nel file WSGI di PA)
   - **Virtualenv** al path del venv creato
4. Ricarica la web app.

Su PythonAnywhere il file WSGI di default spesso va aggiornato così (adatta i path):

```python
import sys
path = "/home/<utente>/giornalino_podcast"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```
