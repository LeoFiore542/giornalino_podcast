from flask import Flask, render_template

app = Flask(__name__)

GIORNALINI = [
    {
        "volume": 3,
        "title": "Primavera in aula",
        "description": "Editoriale, sport e creatività: il terzo numero della redazione.",
        "date": "2026-03-15",
        "date_label": "15 marzo 2026",
        "cover_class": "cover-spring",
    },
    {
        "volume": 2,
        "title": "Luci d’inverno",
        "description": "Reportage natalizi, interviste e i migliori momenti del semestre.",
        "date": "2025-12-10",
        "date_label": "10 dicembre 2025",
        "cover_class": "cover-winter",
    },
    {
        "volume": 1,
        "title": "Nuovo anno",
        "description": "Presentazione della redazione e i primi articoli dell’anno scolastico.",
        "date": "2025-09-20",
        "date_label": "20 settembre 2025",
        "cover_class": "cover-autumn",
    },
]

EPISODI = [
    {
        "episode": 3,
        "title": "Dietro le quinte del musical",
        "description": "Interviste al cast e al corpo docenti, tra prove e première.",
        "date": "2026-03-10",
        "date_label": "10 marzo 2026",
        "duration": "24:18",
        "cover_class": "cover-mic",
    },
    {
        "episode": 2,
        "title": "Orientamento: dove andiamo?",
        "description": "Esperienze di ex studenti e consigli pratici sul dopo-diploma.",
        "date": "2026-02-12",
        "date_label": "12 febbraio 2026",
        "duration": "18:42",
        "cover_class": "cover-path",
    },
    {
        "episode": 1,
        "title": "Benvenuti a Voce di Scuola",
        "description": "La redazione si presenta e racconta com’è nato il podcast.",
        "date": "2026-01-15",
        "date_label": "15 gennaio 2026",
        "duration": "12:05",
        "cover_class": "cover-wave",
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/giornalino")
def giornalino():
    return render_template("giornalino.html", items=GIORNALINI)


@app.route("/podcast")
def podcast():
    return render_template("podcast.html", items=EPISODI)


if __name__ == "__main__":
    app.run(debug=True)
