import os

from flask import Flask, abort, render_template, send_file

from redazione import list_redazione, resolve_redazione_photo
from storage import list_giornalini, list_podcast_sections, resolve_media_file

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "voci-dal-corridoio-dev-change-me")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/giornalino")
def giornalino():
    return render_template("giornalino.html", items=list_giornalini())


@app.route("/podcast")
def podcast():
    sections = list_podcast_sections()
    total = sum(len(section["episodes"]) for section in sections)
    return render_template("podcast.html", sections=sections, total=total)


@app.route("/redazione")
@app.route("/chi-siamo")
def chi_siamo():
    members = list_redazione()
    docenti = [m for m in members if m["ruolo"] == "docente"]
    studenti = [m for m in members if m["ruolo"] == "studente"]
    return render_template(
        "redazione.html",
        docenti=docenti,
        studenti=studenti,
    )


@app.route("/media/redazione/<path:filename>")
def media_redazione(filename):
    path = resolve_redazione_photo(filename)
    if path is None:
        abort(404)
    return send_file(path)


@app.route("/media/<kind>/<path:relpath>")
def media_file(kind, relpath):
    path = resolve_media_file(kind, relpath)
    if path is None:
        abort(404)
    return send_file(path)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/accessibilita")
def accessibilita():
    return render_template("accessibilita.html")


@app.route("/note-legali")
def note_legali():
    return render_template("note_legali.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
