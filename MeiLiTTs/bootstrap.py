import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

base = Path(__file__).resolve().parent
venv = base / ".venv"
venv_python = venv / "bin" / "python"
venv_cfg = venv / "pyvenv.cfg"
target_python_version = "3.12.5"
python_dir = base / "python"
downloaded_python = python_dir / "bin" / "python3"


def get_python_version(python_path):
    try:
        result = subprocess.run(
            [str(python_path), "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            version_line = result.stdout.strip()
            return version_line.split()[-1]  # Extract version number
    except:
        pass
    return None


def get_system_python():
    for python_cmd in ["python3", "python"]:
        try:
            result = subprocess.run(
                ["which", python_cmd], capture_output=True, text=True
            )
            if result.returncode == 0:
                python_path = result.stdout.strip()
                version = get_python_version(python_path)
                if version and version.startswith("3."):
                    return python_path, version
        except:
            continue
    return None, None


def download_python_3_12_5():
    print(f"⬇️ Downloading Python {target_python_version}...")

    # Determine the correct download URL based on platform
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine == "arm64":
            url = f"https://www.python.org/ftp/python/{target_python_version}/Python-{target_python_version}.tgz"
        else:
            url = f"https://www.python.org/ftp/python/{target_python_version}/Python-{target_python_version}.tgz"
    elif system == "linux":
        url = f"https://www.python.org/ftp/python/{target_python_version}/Python-{target_python_version}.tgz"
    else:
        raise Exception(f"Unsupported platform: {system}")

    # Download and extract
    download_path = base / f"Python-{target_python_version}.tgz"
    extract_path = base / f"Python-{target_python_version}"

    urllib.request.urlretrieve(url, download_path)

    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(base)

    # Configure and build
    print(f"🔨 Building Python {target_python_version}...")
    build_commands = [
        ["./configure", f"--prefix={python_dir}", "--enable-optimizations"],
        [
            "make",
            "-j",
            str(
                subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip()
                or "4"
            ),
        ],
        ["make", "install"],
    ]

    for cmd in build_commands:
        subprocess.run(cmd, cwd=extract_path, check=True)

    # Clean up
    download_path.unlink()
    shutil.rmtree(extract_path)

    print(f"✅ Python {target_python_version} installed successfully!")
    return str(downloaded_python)


def get_correct_python():
    # First, check if we already have the correct version downloaded
    if downloaded_python.exists():
        version = get_python_version(downloaded_python)
        if version == target_python_version:
            return str(downloaded_python)

    # Check system Python
    system_python, system_version = get_system_python()
    if system_python and system_version == target_python_version:
        print(f"✅ Using system Python {system_version}")
        return system_python

    # Download and build the correct version
    if system_python:
        print(f"⚠️ System Python is {system_version}, but need {target_python_version}")
    else:
        print("⚠️ No suitable system Python found")

    return download_python_3_12_5()


def needs_rebuild(python_path):
    if not venv_python.exists() or not venv_cfg.exists():
        return True
    # Check if pyvenv.cfg points to the correct Python
    text = venv_cfg.read_text()
    # Resolve the real path to handle pyenv shims
    python_home = str(Path(python_path).resolve().parent)
    for line in text.splitlines():
        if line.startswith("home = "):
            venv_home = line.split("home = ")[1].strip()
            # Compare resolved real paths
            if Path(venv_home).resolve() == Path(python_home).resolve():
                return False
            return True
    return False


# Get the correct Python executable
python_executable = get_correct_python()

if needs_rebuild(python_executable):
    print("⚠️ Detected broken or moved .venv. Rebuilding...")
    if venv.exists():
        subprocess.run(["rm", "-rf", str(venv)], check=True)
    subprocess.run([python_executable, "-m", "venv", str(venv)], check=True)
    subprocess.run(
        [str(venv / "bin" / "pip"), "install", "-r", str(base / "requirements.txt")],
        check=True,
    )

print("🚀 Launching app...")
subprocess.run([str(venv_python), str(base / "main.py")])
