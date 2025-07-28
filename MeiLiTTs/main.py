# Launches the server & sets things up

import os
import shutil
import threading
import time
import uuid
import webbrowser

import rumps
from flask import Flask, jsonify, request, send_from_directory
from process import process_pdf_cancellable

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

# --- Job tracking ---
active_jobs = {}
job_lock = threading.Lock()


def get_unique_filename(base_name):
    """Generate unique filename, adding -1, -2, etc. if needed"""
    if not os.path.exists(OUTPUT_DIR):
        return base_name

    # Check if name conflicts with existing processed files
    processed_names = {
        name
        for name in os.listdir(OUTPUT_DIR)
        if os.path.isdir(os.path.join(OUTPUT_DIR, name))
    }

    # Check if name conflicts with currently processing jobs
    with job_lock:
        processing_names = {job["name"] for job in active_jobs.values()}

    all_names = processed_names | processing_names

    if base_name not in all_names:
        return base_name

    counter = 1
    while f"{base_name}-{counter}" in all_names:
        counter += 1

    return f"{base_name}-{counter}"


def process_pdf_with_tracking(file_path, output_dir, job_id, original_name):
    """Process PDF with job tracking and cancellation support"""
    try:
        with job_lock:
            active_jobs[job_id]["status"] = "processing"
            active_jobs[job_id]["progress"] = 0

        process_pdf_cancellable(file_path, output_dir, job_id, active_jobs, job_lock)

        with job_lock:
            if not active_jobs[job_id]["cancelled"]:
                active_jobs[job_id]["status"] = "completed"
                active_jobs[job_id]["progress"] = 100
    except Exception as e:
        with job_lock:
            active_jobs[job_id]["status"] = "error"
            active_jobs[job_id]["error"] = str(e)
    finally:
        # Clean up job after 5 minutes
        def cleanup():
            time.sleep(300)
            with job_lock:
                if job_id in active_jobs:
                    del active_jobs[job_id]

        threading.Thread(target=cleanup, daemon=True).start()


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

    # Generate unique filename
    base_name = os.path.splitext(file.filename)[0]
    unique_name = get_unique_filename(base_name)

    # Create job
    job_id = str(uuid.uuid4())

    with job_lock:
        active_jobs[job_id] = {
            "name": unique_name,
            "filename": file.filename,
            "status": "starting",
            "progress": 0,
            "cancelled": False,
            "start_time": time.time(),
        }

    # Create output directory and save PDF as original.pdf
    output_dir = os.path.join(OUTPUT_DIR, unique_name)
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "original.pdf")
    file.save(save_path)

    # Start processing in background thread
    thread = threading.Thread(
        target=process_pdf_with_tracking,
        args=(save_path, output_dir, job_id, unique_name),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id, "name": unique_name})


@app.route("/job_status/<job_id>")
def job_status(job_id):
    with job_lock:
        if job_id not in active_jobs:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(active_jobs[job_id])


@app.route("/cancel_job/<job_id>", methods=["POST"])
def cancel_job(job_id):
    with job_lock:
        if job_id not in active_jobs:
            return jsonify({"error": "Job not found"}), 404

        active_jobs[job_id]["cancelled"] = True
        active_jobs[job_id]["status"] = "cancelled"
        return jsonify({"message": "Job cancelled"})


@app.route("/list_jobs")
def list_jobs():
    with job_lock:
        # Include job_id in the response
        jobs_with_ids = []
        for job_id, job_data in active_jobs.items():
            job_with_id = job_data.copy()
            job_with_id["job_id"] = job_id
            jobs_with_ids.append(job_with_id)
        return jsonify(jobs_with_ids)


def is_processing_complete(folder_path):
    """Check if a processed folder has all required files"""
    required_files = ["chunks.json", "full.wav", "original.pdf"]
    return all(os.path.exists(os.path.join(folder_path, file)) for file in required_files)


@app.route("/list_processed")
def list_processed():
    if not os.path.exists(OUTPUT_DIR):
        return jsonify([])
    
    processed_items = []
    for name in os.listdir(OUTPUT_DIR):
        folder_path = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(folder_path):
            is_complete = is_processing_complete(folder_path)
            processed_items.append({
                "name": name,
                "complete": is_complete
            })
    
    return jsonify(processed_items)


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
        super().__init__("MeiLiTTs")
        self.menu = ["Open App"]
        start()

    @rumps.clicked("Open App")
    def open_app(self, _):
        webbrowser.open("http://localhost:8080")


if __name__ == "__main__":
    TrayApp().run()
