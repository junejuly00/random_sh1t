@echo off
setlocal enabledelayedexpansion
echo Quick build for Cloooock - High Precision Desktop Clock...
echo.

REM Initialize variables
set ICON_PARAM=
set ICON_FOUND=0
set ICON_FILE=

REM Look for icon files directly (simpler approach)
echo Looking for custom icon files...

if exist "cloooock_icon.ico" (
    echo Found: cloooock_icon.ico
    set ICON_FILE=cloooock_icon.ico
    set ICON_FOUND=1
    goto icon_found
)

if exist "clock_icon.ico" (
    echo Found: clock_icon.ico
    set ICON_FILE=clock_icon.ico
    set ICON_FOUND=1
    goto icon_found
)

if exist "icon.ico" (
    echo Found: icon.ico
    set ICON_FILE=icon.ico
    set ICON_FOUND=1
    goto icon_found
)

if exist "app_icon.ico" (
    echo Found: app_icon.ico
    set ICON_FILE=app_icon.ico
    set ICON_FOUND=1
    goto icon_found
)

REM Try to create icon if none found
if exist "create_icon.py" (
    echo No icon found. Attempting to create one...
    python create_icon.py
    if exist "cloooock_icon.ico" (
        echo Successfully created custom icon
        set ICON_FILE=cloooock_icon.ico
        set ICON_FOUND=1
        goto icon_found
    )
)

echo No valid icon found - building without custom icon
echo.
echo To add a custom icon:
echo   1. Get a proper .ico file
echo   2. Name it: cloooock_icon.ico
echo   3. Place it in this directory
echo.
goto build_start

:icon_found
echo Using custom icon: !ICON_FILE!
set ICON_PARAM=--icon=!ICON_FILE!
echo.

:build_start
REM Check Python
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check PyInstaller
echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check ntplib
echo Checking ntplib...
python -c "import ntplib" >nul 2>&1
if errorlevel 1 (
    echo Installing ntplib...
    pip install ntplib
    if errorlevel 1 (
        echo Failed to install ntplib
        pause
        exit /b 1
    )
)

REM Verify source file
if not exist "Cloooock.py" (
    echo Source file Cloooock.py not found
    echo Please ensure Cloooock.py is in the current directory
    pause
    exit /b 1
)

REM Clean previous build
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "Cloooock.spec" del "Cloooock.spec" 2>nul

echo.
echo Building Configuration:
echo =======================
echo Source: Cloooock.py
echo Output: dist\Cloooock.exe
if !ICON_FOUND! equ 1 (
    echo Icon: !ICON_FILE!
) else (
    echo Icon: Default Windows icon
)
echo Mode: Windowed
echo Type: Single file executable
echo.

echo Starting PyInstaller build...
echo.

REM Build with or without icon
if !ICON_FOUND! equ 1 (
    echo Building with custom icon...
    python -m PyInstaller --onefile --windowed --name=Cloooock !ICON_PARAM! --distpath=dist --workpath=build --clean Cloooock.py
) else (
    echo Building with default icon...
    python -m PyInstaller --onefile --windowed --name=Cloooock --distpath=dist --workpath=build --clean Cloooock.py
)

REM Check build results
echo.
echo Build Results:
echo ==============
if exist "dist\Cloooock.exe" (
    echo Build successful!
    echo Location: dist\Cloooock.exe
    
    for %%I in ("dist\Cloooock.exe") do (
        echo Size: %%~zI bytes
    )
    
    if !ICON_FOUND! equ 1 (
        echo Custom icon applied
    ) else (
        echo Using default Windows icon
    )
    
    echo.
    echo Ready to run: dist\Cloooock.exe
    echo.
    
    REM Ask to test run
    set /p test_run=Test run the executable now? (y/n): 
    if /i "!test_run!"=="y" (
        start "" "dist\Cloooock.exe"
        echo Started Cloooock.exe
    )
    
) else (
    echo Build failed!
    echo Check for error messages above
    echo.
    echo Troubleshooting:
    echo 1. Verify Cloooock.py runs: python Cloooock.py
    echo 2. Try building from shorter path
    echo 3. Check antivirus settings
    echo 4. Try without custom icon
)

echo.
pause
