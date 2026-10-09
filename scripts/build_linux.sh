#!/bin/bash

# Build script for Linux standalone executables (including Steam Deck)
# Usage: ./build_linux.sh

set -e

echo "Building Steam Beautifier for Linux..."
echo "======================================"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build
rm -rf src/*.spec

# Build main executable
echo "Building steam_beautifier..."
pyinstaller --onefile --name "steam_beautifier" \
  --add-data "config_schema.json:." \
  --hidden-import "cryptography" \
  --hidden-import "dropbox" \
  --hidden-import "PIL" \
  --hidden-import "requests" \
  --hidden-import "rich" \
  --hidden-import "vdf" \
  src/main.py

# Build config executable
echo "Building steam_beautifier_config..."
pyinstaller --onefile --name "steam_beautifier_config" \
  --add-data "config_schema.json:." \
  --hidden-import "cryptography" \
  --hidden-import "dropbox" \
  --hidden-import "PIL" \
  --hidden-import "requests" \
  --hidden-import "rich" \
  --hidden-import "vdf" \
  --hidden-import "tkinter" \
  src/configure.py

# Create release directory
RELEASE_DIR="release/linux"
mkdir -p "$RELEASE_DIR"

# Copy executables
echo "Copying executables to $RELEASE_DIR..."
cp dist/steam_beautifier "$RELEASE_DIR/"
cp dist/steam_beautifier_config "$RELEASE_DIR/"

# Move back to project root
cd "$PROJECT_DIR"

echo ""
echo "Build complete!"
echo "======================================"
echo "Executables ready in: $RELEASE_DIR/"
echo "  - steam_beautifier"
echo "  - steam_beautifier_config"
echo ""
echo "To make them executable on Steam Deck:"
echo "  chmod +x release/linux/steam_beautifier*"
echo ""
