@echo off
title KeyStalker - Quick Build
echo Building KeyStalker.exe...

C:/Users/123/AppData/Local/Programs/Python/Python310/python.exe -m PyInstaller --onefile --windowed --name="KeyStalker" --clean KeyStalker.py

if exist dist\KeyStalker.exe (
    echo.
    echo SUCCESS! Moving KeyStalker.exe to current folder...
    move dist\KeyStalker.exe .
    echo Cleaning up...
    rmdir /s /q dist
    rmdir /s /q build
    del KeyStalker.spec
    echo.
    echo KeyStalker.exe is ready to use!
) else (
    echo.
    echo ERROR: Build failed!
)

pause
