import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from process import process_pdf  # Reuse your logic
from werkzeug.utils import secure_filename

UPLOAD_DIR = Path("processed")
VIEWER_DIR = Path("viewer")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR


# main
@app.route("/")
def serve_index():
    return send_from_directory(VIEWER_DIR, "index.html")


# Not sure what this does
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(VIEWER_DIR, filename)


# Dunno what this does
@app.route("/processed/<pdf>/<filename>")
def serve_output(pdf, filename):
    return send_from_directory(UPLOAD_DIR / pdf, filename)


# Serve the reader.html page
@app.route("/reader.html/<pdfname>")
def serve_reader_html(pdfname):
    return send_from_directory(VIEWER_DIR, "reader.html")


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
    app.run(port=8000, debug=True)
