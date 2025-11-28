@echo off
echo --- Building RBV Downloader App (Windows) ---

:: 1. Install Dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

:: 2. Clean previous builds
echo Cleaning previous builds...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del *.spec

:: 3. Run PyInstaller
echo Compiling with PyInstaller...
pyinstaller --noconfirm --onefile --windowed --name "RBV_Downloader" --add-data "assets;assets" gui.py
if %errorlevel% neq 0 (
    echo PyInstaller failed!
    exit /b %errorlevel%
)

echo -----------------------------------
echo Build Complete!
echo Executable location:
echo   dist\RBV_Downloader.exe
echo -----------------------------------
pause
