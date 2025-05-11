# -*- mode: python ; coding: utf-8 -*-


import os
import glob
from PyInstaller.utils.hooks import collect_data_files

# Helper: package data dir collection
def find_data(package, relative_path=""):
    import importlib.util
    spec = importlib.util.find_spec(package)
    if not spec or not spec.submodule_search_locations:
        return []
    base = spec.submodule_search_locations[0]
    full_path = os.path.join(base, relative_path)
    if not os.path.isdir(full_path):
        return []
    return [(os.path.join(full_path, f), os.path.join(package, relative_path)) 
        for f in os.listdir(full_path) if not f.endswith('.py')]


# Manually include .json files for language_tags, etc.
extra_datas = []
extra_datas += find_data("language_tags", "data/json")
extra_datas += find_data("segments", "data")
extra_datas += find_data("phonemizer", "backends/espeak")
extra_datas += collect_data_files("kokoro", include_py_files=False)  # In case Kokoro bundles anything

# Existing Resources/ folder
extra_datas += [('Resources', 'Resources')]

# espeak bandaid
extra_datas += [('Resources/share/espeak-ng-data', 'espeakng_loader/espeak-ng-data')]

# en_core_web_sm bandaid
extra_datas += [
    ('/Users/dmccanns/Desktop/coding/meili_tts/.venv/lib/python3.12/site-packages/en_core_web_sm', 'en_core_web_sm')
]

a = Analysis(
    ['launch.py'],
    pathex=[],
    binaries=[],
    datas=extra_datas,
    hiddenimports=['flask', 'fitz', 'numpy', 'soundfile', 'kokoro', 'rumps', 'server', 'process'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='launch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
