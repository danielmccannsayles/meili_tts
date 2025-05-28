#!/bin/bash
set -e

APP_NAME="MeiLiTTs"
APP_DIR="./$APP_NAME"
PYTHON_DIR="$APP_DIR/python"
VENV_DIR="$APP_DIR/.venv"
ZIP_NAME="MeiLiTTs.zip"

# Print size helper
print_size() {
    du -sh "$1" 2>/dev/null | awk '{print $1}'
}

echo "📁 App Directory: $APP_DIR"

# Size before cleanup
python_size_before=$(print_size "$PYTHON_DIR")
app_size_before=$(print_size "$APP_DIR")

echo "📦 Python size before cleanup: $python_size_before"
echo "📦 App size before cleanup:    $app_size_before"

# 🧹 Clean up Python
echo "🧹 Cleaning up bundled Python..."

find "$PYTHON_DIR" -name "__pycache__" -exec rm -rf {} +
rm -rf "$PYTHON_DIR/include"
rm -rf "$PYTHON_DIR/lib/pkgconfig"
rm -rf "$PYTHON_DIR/lib/python3.12/test"
rm -rf "$PYTHON_DIR/lib/python3.12/lib2to3"
rm -rf "$PYTHON_DIR/lib/python3.12/idlelib"
rm -rf "$PYTHON_DIR/lib/python3.12/tkinter"
rm -rf "$PYTHON_DIR/share"
rm -rf "$PYTHON_DIR/pip-selfcheck.json"
rm -rf "$PYTHON_DIR/Tools"
rm -rf "$PYTHON_DIR/ssl"
rm -f  "$PYTHON_DIR/bin/2to3"*
rm -f  "$PYTHON_DIR/bin/idle"*
rm -f  "$PYTHON_DIR/bin/pydoc"*

echo "✅ Python cleaned."

# 🔥 Remove .venv
echo "🗑️ Removing existing virtual environment: $VENV_DIR"
rm -rf "$VENV_DIR"

# Size after cleanup
python_size_after=$(print_size "$PYTHON_DIR")
app_size_after=$(print_size "$APP_DIR")

echo "📉 Python size after cleanup:  $python_size_after"
echo "📉 App size after cleanup:     $app_size_after"

# Remove previous zip if exists
rm -f "$ZIP_NAME"

# Create zip
echo "📦 Zipping folder to $ZIP_NAME..."
zip -qr "$ZIP_NAME" "$APP_NAME" -x "*.DS_Store"

zip_size=$(print_size "$ZIP_NAME")

echo "✅ Done!"
echo "🗜️  Final zip size: $zip_size"
