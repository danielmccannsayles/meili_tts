import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent
venv = base / ".venv"
venv_python = venv / "bin" / "python"
venv_cfg = venv / "pyvenv.cfg"
embedded_python = base / "python" / "bin" / "python3"
expected_home = str(base / "python" / "bin")


def needs_rebuild():
    if not venv_python.exists() or not venv_cfg.exists():
        return True
    # Check if pyvenv.cfg points to the wrong location
    text = venv_cfg.read_text()
    for line in text.splitlines():
        if line.startswith("home = ") and expected_home not in line:
            return True
    return False


if needs_rebuild():
    print("⚠️ Detected broken or moved .venv. Rebuilding...")
    if venv.exists():
        subprocess.run(["rm", "-rf", str(venv)], check=True)
    subprocess.run([str(embedded_python), "-m", "venv", str(venv)], check=True)
    subprocess.run(
        [str(venv / "bin" / "pip"), "install", "-r", str(base / "requirements.txt")],
        check=True,
    )

print("🚀 Launching app...")
subprocess.run([str(venv_python), str(base / "main.py")])
