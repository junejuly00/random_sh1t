@echo off
echo Quick build for ColorPicker...
python -m PyInstaller --onefile --windowed --name=ColorPicker colorpicker.py
if exist "dist\ColorPicker.exe" (
    echo Build successful! Executable created at: dist\ColorPicker.exe
) else (
    echo Build failed! Check for errors above.
)
pause
