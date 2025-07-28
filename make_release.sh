#!/bin/bash
set -e

APP_NAME="MeiLiTTs"
APP_DIR="./$APP_NAME"
VENV_DIR="$APP_DIR/.venv"
ZIP_NAME="MeiLiTTs.zip"

# Print size helper
print_size() {
    du -sh "$1" 2>/dev/null | awk '{print $1}'
}

echo "📁 App Directory: $APP_DIR"

# Size before cleanup
app_size_before=$(print_size "$APP_DIR")
echo "📦 App size before cleanup: $app_size_before"

# 🔥 Remove .venv (will be rebuilt by bootstrap.py)
echo "🗑️ Removing existing virtual environment: $VENV_DIR"
rm -rf "$VENV_DIR"

# 🧹 Remove processed files
PROCESSED_DIR="$APP_DIR/processed"
echo "🗑️ Removing processed files: $PROCESSED_DIR"
rm -rf "$PROCESSED_DIR"

# 🧹 Remove Python cache files
echo "🗑️ Removing Python cache files"
rm -rf "$APP_DIR"/__pycache__

# Size after cleanup
app_size_after=$(print_size "$APP_DIR")
echo "📉 App size after cleanup:  $app_size_after"

# Remove previous zip if exists
rm -f "$ZIP_NAME"

# Create zip
echo "📦 Zipping folder to $ZIP_NAME..."
zip -qr "$ZIP_NAME" "$APP_NAME" -x "*.DS_Store"

zip_size=$(print_size "$ZIP_NAME")

echo "✅ Done!"
echo "🗜️  Final zip size: $zip_size"
