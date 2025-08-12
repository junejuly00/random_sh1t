@echo off
echo Installing dependencies for Cloooock...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing required packages...
echo.

REM Install ntplib
pip install ntplib==0.4.0

if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo You can now run: python Cloooock.py
echo.
pause