# Release Guide

This project uses **GitHub Actions** to automatically build standalone executables for **Windows**, **macOS**, and **Linux**.

## How to Build and Release

The build process is fully automated. You do not need to manually compile the code on different machines.

### 1. Push Your Code
Simply push your latest changes to the `main` branch. This will trigger a "test build" to ensure the code compiles correctly on all platforms.

```bash
git add .
git commit -m "Your changes"
git push origin main
```

### 2. Create a Release
To generate the actual downloadable files (artifacts) and publish them to the Releases page, you need to push a **version tag**.

The tag **must** start with `v` (e.g., `v1.0.0`, `v1.1.0`, `v2.0-beta`).

```bash
# Tag the current commit
git tag v1.0.0

# Push the tag to GitHub
git push origin v1.0.0
```

### 3. Download the App
Once the workflow completes (usually takes 2-5 minutes):

1.  Go to your repository on GitHub.
2.  Click on **Releases** in the sidebar.
3.  You will see your new version (e.g., `v1.0.0`).
4.  Expand the "Assets" section to download the executable for your system:
    *   **Windows**: `RBV_Downloader_Windows.exe`
    *   **macOS**: `RBV_Downloader_macos-latest` (or `.zip`)
    *   **Linux**: `RBV_Downloader_ubuntu-latest`

## Manual Local Build (Optional)

If you want to build locally for your own machine's OS:

### macOS / Linux
```bash
./build_app.sh
```

### Windows
Run this in PowerShell:
```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name "RBV_Downloader_Windows" --add-data "assets;assets" gui.py
```
