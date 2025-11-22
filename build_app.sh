#!/bin/bash

# Ensure script stops on error
set -e

echo "--- Building RBV Downloader App ---"

# 1. Install Dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 2. Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# 3. Run PyInstaller
# --onefile: Create a single executable file
# --windowed: No terminal window (for GUI)
# --name: Name of the executable
# --add-data: Not strictly needed here unless we have icons or extra assets, 
#             but good to know. 'downloads' folder will be created at runtime.

echo "Compiling with PyInstaller..."
pyinstaller --noconfirm --onefile --windowed --name "RBV_Downloader" --add-data "assets:assets" gui.py

echo "-----------------------------------"
echo "Build Complete!"
echo "Executable location:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS often puts it in a .app bundle if using --windowed, 
    # but with --onefile and --windowed it might just be a binary inside dist.
    # Let's check.
    echo "  dist/RBV_Downloader.app (or dist/RBV_Downloader)"
else
    echo "  dist/RBV_Downloader"
fi
echo "-----------------------------------"
