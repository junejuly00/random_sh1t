@echo off
title KeyStalker - Build Executable
echo ===============================================
echo KeyStalker - Building Executable
echo ===============================================
echo.

echo Installing PyInstaller (if not already installed)...
C:/Users/123/AppData/Local/Programs/Python/Python310/python.exe -m pip install pyinstaller matplotlib numpy
echo.

echo Building KeyStalker.exe...
echo This may take a few minutes...
echo.

C:/Users/123/AppData/Local/Programs/Python/Python310/python.exe -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name="KeyStalker" ^
    --distpath="." ^
    --workpath="build" ^
    --specpath="build" ^
    --clean ^
    KeyStalker.py

echo.
if exist KeyStalker.exe (
    echo ===============================================
    echo SUCCESS! KeyStalker.exe has been created!
    echo ===============================================
    echo.
    echo You can now run KeyStalker.exe directly
    echo The executable is located in the current folder
    echo.
    echo Cleaning up temporary files...
    if exist build rmdir /s /q build
    if exist KeyStalker.spec del KeyStalker.spec
    echo.
    echo Build complete! You can delete this batch file if you want.
) else (
    echo ===============================================
    echo ERROR: Failed to create KeyStalker.exe
    echo ===============================================
    echo Check the error messages above for details.
)

echo.
pause
