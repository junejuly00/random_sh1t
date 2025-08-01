@echo off
echo ========================================
echo   Random Image Viewer - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Python found. Checking for PyInstaller...

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
) else (
    echo PyInstaller is already installed.
)

echo.
echo Installing required dependencies...
pip install requests pillow

echo.
echo Building executable...
echo This may take a few minutes...

REM Build the executable with PyInstaller
pyinstaller --onefile --windowed --name "RandomImageViewer" --icon=none randompic.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo           BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your executable has been created in the 'dist' folder:
echo   dist\RandomImageViewer.exe
echo.
echo You can now run the executable without Python installed!
echo.

REM Open the dist folder
if exist "dist" (
    echo Opening dist folder...
    start "" "dist"
)

pause
