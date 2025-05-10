import os
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

if hasattr(sys, "_MEIPASS"):
    RES_DIR = Path(sys._MEIPASS) / "Resources"
else:
    RES_DIR = Path(__file__).resolve().parent / "Resources"

# Set env vars for espeak-ng
os.environ["PATH"] = str(RES_DIR / "bin") + ":" + os.environ.get("PATH", "")
os.environ["DYLD_LIBRARY_PATH"] = str(RES_DIR / "lib")
os.environ["ESPEAK_DATA_PATH"] = str(RES_DIR / "share" / "espeak-ng-data")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


log_path = Path(tempfile.gettempdir()) / "meili_server.log"
print(f"Logging to: {log_path}")

# Run server.py from Resources
log_file = open("/tmp/meili_server.log", "w")
server_script = RES_DIR / "server.py"
server_proc = subprocess.Popen(
    ["python3", str(server_script)],
    cwd=RES_DIR,
    stdout=log_file,
    stderr=log_file,
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
