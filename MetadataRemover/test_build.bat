@echo off
echo Simple MetadataManager v1.0 build test...
echo.

REM Check if Python works
echo Testing Python...
python --version
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

REM Test icon creation
echo.
echo Testing icon creation...
python create_icon.py
if errorlevel 1 (
    echo Icon creation failed
) else (
    echo Icon creation succeeded
)

REM List files
echo.
echo Current files:
dir /b *.py *.ico *.spec

REM Simple build test
echo.
echo Testing simple build...
python -m PyInstaller --version
if errorlevel 1 (
    echo PyInstaller not available, installing...
    pip install pyinstaller
)

echo.
echo Attempting build...
python -m PyInstaller --onefile --name=MetadataManager_Test metadataremover.py

echo.
echo Build test completed.
pause
