# launch.py
import atexit
import os
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import rumps

# Global to hold server process
server_proc = None


# Check if we're already running by trying to connect to the port
def is_server_running():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex(("127.0.0.1", 8000)) == 0
    except Exception:
        # If there's any error, assume server isn't running
        return False


# Cleanup function to terminate server when app exits
def cleanup():
    global server_proc
    if server_proc:
        try:
            server_proc.terminate()
            print("Server process terminated")
        except Exception:
            pass


# Register cleanup to run on exit
atexit.register(cleanup)

# Server mode or URL handling mode
IS_SERVER = "--server" in sys.argv

# Setup resource paths
if hasattr(sys, "_MEIPASS"):
    RES_DIR = Path(sys._MEIPASS) / "Resources"

    # Add spaCy model path
    spacy_model_path = Path(sys._MEIPASS) / "en_core_web_sm"
    if spacy_model_path.exists():
        os.environ["SPACY_MODEL_PATH"] = str(spacy_model_path)
        print(f"Setting SPACY_MODEL_PATH to {spacy_model_path}")
else:
    RES_DIR = Path(__file__).resolve().parent / "Resources"

# Set env vars for espeak-ng and ML frameworks
os.environ["PATH"] = str(RES_DIR / "bin") + ":" + os.environ.get("PATH", "")
os.environ["DYLD_LIBRARY_PATH"] = str(RES_DIR / "lib")
os.environ["ESPEAK_DATA_PATH"] = str(RES_DIR / "share" / "espeak-ng-data")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# If we're in server mode, run the Flask app
if IS_SERVER:
    print("Starting server mode...")
    from server import app

    app.run(port=8000, debug=False, use_reloader=False)
    sys.exit(0)

# We're in normal launch mode - check if server is already running
if is_server_running():
    print("Server already running, just opening browser")
    webbrowser.open("http://localhost:8000")
else:
    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = Path(tempfile.gettempdir()) / f"meili_server_{timestamp}.log"
    print(f"Logging to: {log_path}")

    log_file = open(log_path, "w")
    print("Starting new server process...")
    server_proc = subprocess.Popen(
        [sys.executable, sys.argv[0], "--server"],
        stdout=log_file,
        stderr=log_file,
    )

    # Wait until ready
    start_time = time.time()
    max_wait_time = 30  # seconds

    while time.time() - start_time < max_wait_time:
        if is_server_running():
            print("Server started successfully")
            break
        time.sleep(0.2)
    else:
        print("Warning: Server didn't start within expected time")

    # Open browser even if server might not be ready yet
    webbrowser.open("http://localhost:8000")


# Create a rumps menu bar app
class MeiliApp(rumps.App):
    def __init__(self):
        super(MeiliApp, self).__init__("MeiliTTs", quit_button=None)
        self.menu = ["Open MeiliTTs", "Quit MeiliTTs"]

    @rumps.clicked("Open MeiliTTs")
    def open_app(self, _):
        webbrowser.open("http://localhost:8000")

    @rumps.clicked("Quit MeiliTTs")
    def quit_app(self, _):
        print("Shutting down MeiliTTs...")
        cleanup()
        rumps.quit_application()


# Start the menu bar app
MeiliApp().run()
