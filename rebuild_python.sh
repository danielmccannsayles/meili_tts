#!/bin/bash
set -e

APP_FOLDER="./MeiLiTTs"
TARGET="$APP_FOLDER/python"

# Get real path to current pyenv Python install
PYTHON_BIN=$(pyenv which python3)
SOURCE=$(realpath "$(dirname "$(dirname "$PYTHON_BIN")")")
DEST=$(realpath "$TARGET")

echo "📦 Copying pyenv Python from: $SOURCE"
echo "📁 Target directory: $DEST"

# Clean existing target
rm -rf "$DEST"
mkdir -p "$DEST"

# Use tar to copy and resolve symlinks
cd "$SOURCE"
echo "📂 Flattening and copying..."
tar -chf - . | (cd "$DEST" && tar -xpf -)

echo "✅ Python copied with resolved symlinks."

# Check for remaining symlinks
SYMLINK_COUNT=$(find "$DEST" -type l | wc -l)
echo "🔍 Symlinks remaining: $SYMLINK_COUNT"
if [ "$SYMLINK_COUNT" -gt 0 ]; then
    echo "⚠️  Note: Some internal symlinks may remain."
fi

echo "✅ Done. Your portable python/ folder is ready."
