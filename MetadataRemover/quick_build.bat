@echo off
echo Quick build for MetadataRemover...

REM Create custom icon
echo Creating custom application icon...
python create_icon.py
if exist "metadatamanager_icon.ico" (
    echo Custom icon created successfully.
    set ICON_PARAM=--icon=metadatamanager_icon.ico
) else (
    echo Warning: Icon file not found. Using default.
    set ICON_PARAM=
)

python -m PyInstaller --onefile --windowed --name=MetadataRemover %ICON_PARAM% metadataremover.py
if exist "dist\MetadataRemover.exe" (
    echo Build successful! Executable created at: dist\MetadataRemover.exe
) else (
    echo Build failed! Check for errors above.
)
pause
