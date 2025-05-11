# process.py
import json
import os

import fitz  # PyMuPDF
import numpy as np
import soundfile as sf
from kokoro import KPipeline

# Enable CPU fallback for Kokoro (https://github.com/hexgrad/kokoro?tab=readme-ov-file)
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Set up env to point to espeak-ng
base = os.path.dirname(__file__)
os.environ["PATH"] = os.path.join(base, "bin") + ":" + os.environ.get("PATH", "")
os.environ["DYLD_LIBRARY_PATH"] = os.path.join(base, "lib")
os.environ["ESPEAK_DATA_PATH"] = os.path.join(base, "share", "espeak-ng-data")


def process_pdf(file_path, output_dir):
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
