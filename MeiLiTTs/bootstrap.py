#!/usr/bin/env python3
"""
Bootstrap script for MeiLiTTs - Downloads and sets up Python 3.12.5 environment

This script can run on older Python versions (3.6+) to bootstrap the target environment,
but the actual application requires exactly Python 3.12.5.
"""

import sys

# Early version check - ensure we can run this bootstrap script
if sys.version_info < (3, 6):
    print("❌ Error: This bootstrap script requires Python 3.6 or newer")
    print(f"   Your Python version: {sys.version}")
    print("   Please upgrade Python to continue")
    sys.exit(1)

import os
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
    # First check for exact version match
    for python_cmd in ["python3", "python"]:
        try:
            result = subprocess.run(
                ["which", python_cmd], capture_output=True, text=True
            )
            if result.returncode == 0:
                python_path = result.stdout.strip()
                version = get_python_version(python_path)
                if version == target_python_version:
                    return python_path, version
        except:
            continue

    # If no exact match, look for pyenv versions
    try:
        result = subprocess.run(
            ["pyenv", "versions", "--bare"], capture_output=True, text=True
        )
        if result.returncode == 0:
            for version in result.stdout.strip().splitlines():
                if version.strip() == target_python_version:
                    pyenv_python = f"{os.path.expanduser('~')}/.pyenv/versions/{version}/bin/python3"
                    if os.path.exists(pyenv_python):
                        return pyenv_python, version
    except:
        pass

    # Fallback to any Python 3.x
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


def get_cpu_count():
    """Get CPU count, works on both Linux and macOS"""
    try:
        # Try nproc first (Linux)
        result = subprocess.run(["nproc"], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass

    try:
        # Try sysctl for macOS
        result = subprocess.run(
            ["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass

    # Fallback to Python's os.cpu_count()
    return os.cpu_count() or 4


def check_build_requirements():
    """Check if system has required build tools"""
    missing_tools = []

    # Check for essential build tools
    for tool in ["make", "gcc", "clang"]:
        try:
            result = subprocess.run(["which", tool], capture_output=True, text=True)
            if result.returncode == 0:
                break  # Found at least one compiler
        except:
            continue
    else:
        missing_tools.append("compiler (gcc or clang)")

    # Check for make
    try:
        subprocess.run(["which", "make"], capture_output=True, text=True, check=True)
    except:
        missing_tools.append("make")

    if missing_tools:
        print("❌ Error: Missing required build tools:")
        for tool in missing_tools:
            print(f"   - {tool}")
        print("\n💡 To install build tools:")
        if platform.system().lower() == "darwin":
            print("   Run: xcode-select --install")
        else:
            print("   Run: sudo apt-get install build-essential (Ubuntu/Debian)")
            print("   Or:  sudo yum groupinstall 'Development Tools' (RHEL/CentOS)")
        return False

    return True


def check_disk_space(required_gb=1):
    """Check if we have enough disk space (in GB)"""
    try:
        stat = shutil.disk_usage(base)
        free_gb = stat.free / (1024**3)
        if free_gb < required_gb:
            print(f"❌ Error: Insufficient disk space")
            print(f"   Required: {required_gb}GB")
            print(f"   Available: {free_gb:.1f}GB")
            return False
        return True
    except:
        print("⚠️  Warning: Could not check disk space")
        return True  # Continue anyway


def test_network_connectivity():
    """Test if we can reach python.org"""
    try:
        import urllib.request

        urllib.request.urlopen("https://www.python.org", timeout=10)
        return True
    except:
        print("❌ Error: Cannot reach python.org")
        print("   Please check your internet connection")
        return False


def download_with_retry(url, filepath, max_retries=3):
    """Download with retry logic"""
    for attempt in range(max_retries):
        try:
            print(
                f"⬇️ Downloading Python {target_python_version}... (attempt {attempt + 1}/{max_retries})"
            )
            urllib.request.urlretrieve(url, filepath)
            return True
        except Exception as e:
            print(f"   Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("   Retrying...")
            else:
                print("❌ Download failed after all retries")
                return False
    return False


def download_python_3_12_5():
    # Pre-flight checks
    if not test_network_connectivity():
        return None

    if not check_disk_space():
        return None

    if not check_build_requirements():
        return None

    print(f"\n🔧 Building Python {target_python_version} from source...")
    print("   This may take several minutes...")

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

    if not download_with_retry(url, download_path):
        return None

    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(base)

    # Configure and build
    print(f"🔨 Compiling Python {target_python_version}...")
    build_commands = [
        (
            ["./configure", f"--prefix={python_dir}", "--enable-optimizations"],
            "Configuring build...",
        ),
        (["make", "-j", str(get_cpu_count())], "Compiling (this takes the longest)..."),
        (["make", "install"], "Installing..."),
    ]

    try:
        for cmd, description in build_commands:
            print(f"   {description}")
            result = subprocess.run(
                cmd, cwd=extract_path, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"❌ Build failed during: {description}")
                print(f"   Command: {' '.join(cmd)}")
                print(f"   Error: {result.stderr[:500]}...")
                return None
    except Exception as e:
        print(f"❌ Build process failed: {e}")
        return None

    # Clean up
    download_path.unlink()
    shutil.rmtree(extract_path)

    print(f"✅ Python {target_python_version} installed successfully!")
    return str(downloaded_python)


def get_correct_python():
    """Get Python 3.12.5 - either existing or by building from source"""

    print(f"🔍 Looking for Python {target_python_version}...")

    # First, check if we already have the correct version downloaded
    if downloaded_python.exists():
        version = get_python_version(downloaded_python)
        if version == target_python_version:
            print(f"✅ Found existing Python {version} (pre-built)")
            return str(downloaded_python)

    # Check system Python
    system_python, system_version = get_system_python()
    if system_python and system_version == target_python_version:
        print(f"✅ Found system Python {system_version}")
        return system_python

    # Need to build from source
    bootstrap_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    print(f"⚠️  Python {target_python_version} not found")
    if system_python:
        print(f"   System Python is {system_version} (need {target_python_version})")
    else:
        print("   No suitable system Python found")
    print(f"   Using Python {bootstrap_version} to bootstrap {target_python_version}")

    result = download_python_3_12_5()
    if result is None:
        print(f"\n❌ Failed to build Python {target_python_version}")
        print("   Cannot continue without the correct Python version")
        sys.exit(1)

    return result


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


def main():
    """Main bootstrap process"""
    print("🚀 MeiLiTTs Bootstrap")
    print("=" * 50)

    # Get the correct Python executable
    python_executable = get_correct_python()

    # Check/rebuild virtual environment
    if needs_rebuild(python_executable):
        print("\n🔧 Setting up virtual environment...")
        if venv.exists():
            print("   Removing old .venv...")
            subprocess.run(["rm", "-rf", str(venv)], check=True)

        print("   Creating new .venv...")
        subprocess.run([python_executable, "-m", "venv", str(venv)], check=True)

        print("   Installing dependencies...")
        result = subprocess.run(
            [
                str(venv / "bin" / "pip"),
                "install",
                "-r",
                str(base / "requirements.txt"),
            ],
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            print("❌ Failed to install dependencies")
            print(f"   Error: {result.stderr}")
            sys.exit(1)
        print("✅ Environment ready!")
    else:
        print("✅ Virtual environment is up to date")

    print("\n🚀 Launching MeiLiTTs...")
    print("=" * 50)
    subprocess.run([str(venv_python), str(base / "main.py")])


if __name__ == "__main__":
    main()
