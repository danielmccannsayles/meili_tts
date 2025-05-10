import socket
import subprocess
import time
import webbrowser

# Launch the server
server_proc = subprocess.Popen(
    ["python3", "server.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)


# Wait until server is ready
def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


print("Waiting for server...")
for _ in range(40):  # Wait up to ~8 seconds
    if is_port_open("127.0.0.1", 8000):
        break
    time.sleep(0.2)

# Open browser
print("Opening viewer...")
webbrowser.open("http://localhost:8000")

# Optional: keep script alive while server runs (for double-click context)
try:
    server_proc.wait()
except KeyboardInterrupt:
    server_proc.terminate()
