@echo off
echo Quick Build - Random Image Viewer
echo ==================================

REM Quick build without dependency checks
echo Building executable...
pyinstaller --onefile --windowed --name "RandomImageViewer" randompic.py

if errorlevel 1 (
    echo Build failed! Try running build_exe.bat for full setup.
    pause
    exit /b 1
)

echo.
echo Build complete! Executable created in dist folder.
start "" "dist"
pause
