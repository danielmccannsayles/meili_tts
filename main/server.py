# server.py
import shutil
import sys
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory
from process import process_pdf
from werkzeug.utils import secure_filename

UPLOAD_DIR = Path.home() / "Library" / "Application Support" / "MeiliTTs" / "processed"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


if hasattr(sys, "_MEIPASS"):
    VIEWER_DIR = Path(sys._MEIPASS) / "Resources" / "viewer"
else:
    VIEWER_DIR = Path(__file__).resolve().parent / "Resources" / "viewer"

app = Flask(__name__, static_folder=str(VIEWER_DIR))
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR


# main
@app.route("/")
def serve_index():
    return send_from_directory(VIEWER_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(VIEWER_DIR, filename)


@app.route("/processed/<pdf>/<filename>")
def serve_output(pdf, filename):
    return send_from_directory(UPLOAD_DIR / pdf, filename)


# Serve the reader.html page
@app.route("/reader.html/<pdfname>")
def serve_reader_html(pdfname):
    return send_from_directory(VIEWER_DIR, "reader.html")


@app.route("/delete/<name>", methods=["DELETE"])
def delete_processed(name):
    folder = UPLOAD_DIR / secure_filename(name)
    if folder.exists() and folder.is_dir():
        shutil.rmtree(folder)
        return "", 204
    else:
        return abort(404, "Not found")


@app.route("/process", methods=["POST"])
def handle_upload():
    pdf = request.files["pdf"]
    name = secure_filename(pdf.filename.rsplit(".", 1)[0])
    outdir = UPLOAD_DIR / name
    outdir.mkdir(parents=True, exist_ok=True)
    input_path = outdir / "input.pdf"
    pdf.save(input_path)

    process_pdf(input_path, outdir)

    return jsonify(
        {
            "chunks": f"/processed/{name}/chunks.json",
            "audio": f"/processed/{name}/full.wav",
            "name": name,
        }
    )


@app.route("/list_processed")
def list_processed():
    folders = [
        f.name
        for f in UPLOAD_DIR.iterdir()
        if f.is_dir() and (f / "chunks.json").exists() and (f / "full.wav").exists()
    ]
    return jsonify(folders)


if __name__ == "__main__":
    app.run(port=8000, debug=False, use_reloader=False)  # Turned off for subprocess
