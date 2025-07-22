# process.py
import json
import os
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
import soundfile as sf
from kokoro import KPipeline

# Enable CPU fallback for Kokoro (https://github.com/hexgrad/kokoro?tab=readme-ov-file)
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# bin subdir
base_dir = os.path.abspath(os.path.dirname(__file__))
bin_dir = os.path.join(base_dir, "bin")

os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"
os.environ["DYLD_LIBRARY_PATH"] = bin_dir  # macOS shared libs (libespeak.dylib)
os.environ["ESPEAK_DATA_PATH"] = os.path.join(bin_dir, "espeak-ng-data")


def process_pdf(file_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    text = ""
    for page in fitz.open(file_path):
        text += page.get_text("text")

    clean_text = " ".join(text.splitlines())
    assert clean_text, f"No text found in file {file_path}"

    # Stitch together audio, chunks
    total_length = len(clean_text)
    current_length = 0
    start_time = 0
    sample_rate = 24000

    all_audio = []
    chunks = []

    # Setup Kokoro
    pipeline = KPipeline(lang_code="a")
    generator = pipeline(clean_text, voice="af_heart")
    print("Processing..")
    for i, (gs, ps, audio) in enumerate(generator):
        duration = len(audio) / sample_rate
        chunks.append({"text": gs, "start": start_time})
        start_time += duration
        current_length += len(gs)
        print(f"Processed ({(current_length * 100) / total_length:.1f}%)")
        all_audio.append(audio)

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)

    full_audio = np.concatenate(all_audio)
    sf.write(output_dir / "full.wav", full_audio, sample_rate)


def process_pdf_cancellable(file_path, output_dir, job_id, active_jobs, job_lock):
    """Process PDF with cancellation support and progress tracking"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check for cancellation
    with job_lock:
        if active_jobs[job_id]["cancelled"]:
            return

    text = ""
    for page in fitz.open(file_path):
        text += page.get_text("text")
        # Check for cancellation during text extraction
        with job_lock:
            if active_jobs[job_id]["cancelled"]:
                return

    clean_text = " ".join(text.splitlines())
    assert clean_text, f"No text found in file {file_path}"

    # Stitch together audio, chunks
    total_length = len(clean_text)
    current_length = 0
    start_time = 0
    sample_rate = 24000

    all_audio = []
    chunks = []

    # Setup Kokoro
    pipeline = KPipeline(lang_code="a")
    generator = pipeline(clean_text, voice="af_heart")

    with job_lock:
        active_jobs[job_id]["status"] = "generating_audio"

    for i, (gs, ps, audio) in enumerate(generator):
        # Check for cancellation before processing each chunk
        with job_lock:
            if active_jobs[job_id]["cancelled"]:
                return

        duration = len(audio) / sample_rate
        chunks.append({"text": gs, "start": start_time})
        start_time += duration
        current_length += len(gs)

        # Update progress
        progress = int((current_length * 100) / total_length)
        with job_lock:
            active_jobs[job_id]["progress"] = progress

        print(f"Processed ({progress}%)")
        all_audio.append(audio)

    # Check for cancellation before final file writes
    with job_lock:
        if active_jobs[job_id]["cancelled"]:
            return

    # Final file writing
    with job_lock:
        active_jobs[job_id]["status"] = "writing_files"

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)

    full_audio = np.concatenate(all_audio)
    sf.write(output_dir / "full.wav", full_audio, sample_rate)
