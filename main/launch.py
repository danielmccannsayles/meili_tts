import os
import socket
import subprocess
import time
import webbrowser
from pathlib import Path

APP_DIR = (
    Path(__file__).resolve().parent.parent
)  # Meili.app/Contents/MacOS → up to Contents
RES_DIR = APP_DIR / "Resources"

# Set env vars for espeak-ng
os.environ["PATH"] = str(RES_DIR / "bin") + ":" + os.environ.get("PATH", "")
os.environ["DYLD_LIBRARY_PATH"] = str(RES_DIR / "lib")
os.environ["ESPEAK_DATA_PATH"] = str(RES_DIR / "share" / "espeak-ng-data")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Run server.py from Resources
server_script = RES_DIR / "server.py"
server_proc = subprocess.Popen(
    ["python3", str(server_script)],
    cwd=RES_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


# Wait until ready
def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


for _ in range(40):
    if is_port_open("127.0.0.1", 8000):
        break
    time.sleep(0.2)

webbrowser.open("http://localhost:8000")

try:
    server_proc.wait()
except KeyboardInterrupt:
    server_proc.terminate()
