#!/bin/bash
set -e

TARGET_DIR="./MeiLiTTs/python"
SOURCE_PYENV_ROOT=$(dirname $(dirname $(pyenv which python3)))

echo "📦 Copying Python from $SOURCE_PYENV_ROOT"
echo "📁 Target: $TARGET_DIR"

# Clean existing target
rm -rf "$TARGET_DIR"

# Copy and resolve symlinks
rsync -aL "$SOURCE_PYENV_ROOT/" "$TARGET_DIR/"

echo "✅ Python copied with symlinks resolved."

# Check key binaries
echo "📄 Verifying..."
file "$TARGET_DIR/bin/python3"
file "$TARGET_DIR/bin/python"
