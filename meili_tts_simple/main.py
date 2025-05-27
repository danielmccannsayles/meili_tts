# Launches the server & sets things up

import os
import shutil
import threading
import webbrowser

import rumps
from flask import Flask, jsonify, request, send_from_directory
from process import process_pdf

# --- Environment setup for espeak-ng ---
base_dir = os.path.abspath(os.path.dirname(__file__))
bin_dir = os.path.join(base_dir, "bin")
os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"
os.environ["DYLD_LIBRARY_PATH"] = bin_dir
os.environ["ESPEAK_DATA_PATH"] = os.path.join(bin_dir, "espeak-ng-data")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# --- Flask app ---
app = Flask(__name__, static_folder="static")
OUTPUT_DIR = "processed"


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/reader.html/<name>")
def reader(name):
    return send_from_directory("static", "reader.html")


@app.route("/processed/<path:filename>")
def serve_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/process", methods=["POST"])
def process():
    file = request.files.get("pdf")
    if not file:
        return "No file", 400
    name = os.path.splitext(file.filename)[0]
    save_path = os.path.join(OUTPUT_DIR, name + ".pdf")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file.save(save_path)
    process_pdf(save_path, os.path.join(OUTPUT_DIR, name))
    return jsonify({"name": name})


@app.route("/list_processed")
def list_processed():
    if not os.path.exists(OUTPUT_DIR):
        return jsonify([])
    return jsonify(
        [
            name
            for name in os.listdir(OUTPUT_DIR)
            if os.path.isdir(os.path.join(OUTPUT_DIR, name))
        ]
    )


@app.route("/delete/<name>", methods=["DELETE"])
def delete(name):
    path = os.path.join(OUTPUT_DIR, name)
    if os.path.isdir(path):
        shutil.rmtree(path)
        return "", 204
    return "Not found", 404


# --- Server launching ---
def run_server():
    app.run(port=8080, debug=False)


def start():
    threading.Thread(target=run_server, daemon=True).start()
    webbrowser.open("http://localhost:8080")


# --- Rumps tray app ---
class TrayApp(rumps.App):
    def __init__(self):
        super().__init__("MeiLiTTS")
        self.menu = ["Open App"]
        start()

    @rumps.clicked("Open App")
    def open_app(self, _):
        webbrowser.open("http://localhost:8080")


if __name__ == "__main__":
    TrayApp().run()
