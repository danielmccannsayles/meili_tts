# launch.py
import os
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

import rumps

# Server mode
IS_SERVER = "--server" in sys.argv

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
if IS_SERVER:
    # We're in server mode — run the Flask app directly
    from server import app

    app.run(port=8000, debug=False, use_reloader=False)
    sys.exit(0)

# Otherwise, start the server by launching this script again in --server mode
server_proc = subprocess.Popen(
    [sys.executable, "--server"],
    stdout=log_file,
    stderr=log_file,
)


# Wait until ready
def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


# Wait 20 seconds to open window... often times takes a long time :/
for _ in range(100):
    if is_port_open("127.0.0.1", 8000):
        break
    time.sleep(0.2)

webbrowser.open("http://localhost:8000")


# Create a little rumps window to tell Mac this app is still running
# and allow user to quit


class MeiliApp(rumps.App):
    def __init__(self):
        super(MeiliApp, self).__init__("MeiliTTs", quit_button=None)
        self.menu = ["Quit MeiliTTs"]

    @rumps.clicked("Quit MeiliTTs")
    def quit_app(self, _):
        print("Shutting down MeiliTTs...")
        server_proc.terminate()
        rumps.quit_application()


MeiliApp().run()
