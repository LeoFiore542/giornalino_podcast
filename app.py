import os
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from redazione import list_redazione, resolve_redazione_photo
from storage import (
    delete_cover_file,
    delete_item,
    delete_main_file,
    list_episodi,
    list_giornalini,
    next_episode_number,
    next_volume_number,
    publish_item,
    resolve_media_file,
    save_uploaded_cover,
    save_uploaded_main,
    today_iso,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "voci-dal-corridoio-dev-change-me")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB

STORAGE_PASSWORD = os.environ.get("STORAGE_PASSWORD", "vocidalcorridoio")


def storage_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("storage_auth"):
            return redirect(url_for("index", storage_login=1))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/giornalino")
def giornalino():
    return render_template("giornalino.html", items=list_giornalini())


@app.route("/podcast")
def podcast():
    return render_template("podcast.html", items=list_episodi())


@app.route("/chi-siamo")
@app.route("/redazione")
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


@app.route("/media/<kind>/<slug>/<path:filename>")
def media_file(kind, slug, filename):
    path = resolve_media_file(kind, slug, filename)
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


@app.route("/storage", methods=["GET"])
def storage_entry():
    if session.get("storage_auth"):
        return redirect(url_for("storage_dashboard"))
    return redirect(url_for("index", storage_login=1))


@app.route("/storage/auth", methods=["POST"])
def storage_auth():
    password = request.form.get("password", "")
    if password == STORAGE_PASSWORD:
        session["storage_auth"] = True
        session.permanent = True
        return {"ok": True, "redirect": url_for("storage_dashboard")}
    return {"ok": False, "error": "Password non corretta."}, 401


@app.route("/storage/logout", methods=["POST"])
def storage_logout():
    session.pop("storage_auth", None)
    flash("Sei uscito dall’area Storage.", "info")
    return redirect(url_for("index"))


@app.route("/storage/dashboard")
@storage_login_required
def storage_dashboard():
    return render_template(
        "storage_dashboard.html",
        giornalini=list_giornalini(),
        episodi=list_episodi(),
        next_volume=next_volume_number(),
        next_episode=next_episode_number(),
        today_label=_today_label(),
    )


def _today_label():
    from storage import date_label_it

    return date_label_it(today_iso())


@app.route("/storage/publish", methods=["POST"])
@storage_login_required
def storage_publish():
    kind = request.form.get("kind", "")
    try:
        slug = publish_item(
            kind=kind,
            number=int(request.form.get("number") or 0),
            title=request.form.get("title", ""),
            description=request.form.get("description", ""),
            main_upload=request.files.get("main_file"),
            cover_upload=request.files.get("cover_file"),
            duration=request.form.get("duration", ""),
        )
        label = "giornalino" if kind == "giornalino" else "podcast"
        flash(f"Pubblicato {label} ({slug}) con data di oggi.", "ok")
    except (ValueError, TypeError) as exc:
        flash(str(exc), "error")
    return redirect(url_for("storage_dashboard"))


@app.route("/storage/upload", methods=["POST"])
@storage_login_required
def storage_upload():
    kind = request.form.get("kind", "")
    slug = request.form.get("slug", "")
    file_type = request.form.get("file_type", "main")
    upload = request.files.get("file")

    try:
        if not upload or not upload.filename:
            raise ValueError("Seleziona un file.")
        if file_type == "cover":
            name = save_uploaded_cover(kind, slug, upload)
            flash(f"Copertina caricata: {name}", "ok")
        else:
            name = save_uploaded_main(kind, slug, upload)
            flash(f"File caricato: {name}", "ok")
    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(url_for("storage_dashboard"))


@app.route("/storage/delete-file", methods=["POST"])
@storage_login_required
def storage_delete_file():
    kind = request.form.get("kind", "")
    slug = request.form.get("slug", "")
    file_type = request.form.get("file_type", "main")

    try:
        if file_type == "cover":
            delete_cover_file(kind, slug)
            flash("Copertina eliminata.", "ok")
        else:
            delete_main_file(kind, slug)
            label = "PDF" if kind == "giornalino" else "MP3"
            flash(f"{label} eliminato.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(url_for("storage_dashboard"))


@app.route("/storage/delete-item", methods=["POST"])
@storage_login_required
def storage_delete_item():
    kind = request.form.get("kind", "")
    slug = request.form.get("slug", "")
    try:
        delete_item(kind, slug)
        flash(f"Eliminata la voce {slug}.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("storage_dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
