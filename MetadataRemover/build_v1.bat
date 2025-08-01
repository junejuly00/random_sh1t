@echo off
echo Building MetadataManager v1.0...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    pause
    exit /b 1
)

REM Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install Pillow
echo Installing dependencies...
pip install Pillow >nul 2>&1

REM Create output folder
if not exist "MetadataManager_v1.0" mkdir "MetadataManager_v1.0"

REM Create icon
echo Creating icon...
python create_icon.py

REM Build with icon if available
if exist "metadatamanager_icon.ico" (
    echo Building with custom icon...
    python -m PyInstaller --onefile --windowed --name=MetadataManager --icon=metadatamanager_icon.ico --distpath=MetadataManager_v1.0 metadataremover.py
) else (
    echo Building without icon...
    python -m PyInstaller --onefile --windowed --name=MetadataManager --distpath=MetadataManager_v1.0 metadataremover.py
)

REM Copy files
if exist "MetadataManager_v1.0\MetadataManager.exe" (
    echo.
    echo SUCCESS! MetadataManager v1.0 created!
    echo.
    copy "README.md" "MetadataManager_v1.0\" >nul 2>&1
    copy "LICENSE.txt" "MetadataManager_v1.0\" >nul 2>&1
    copy "CHANGELOG.md" "MetadataManager_v1.0\" >nul 2>&1
    echo Documentation copied.
    echo.
    echo Ready for distribution: MetadataManager_v1.0\
    echo.
) else (
    echo Build failed!
)

pause
