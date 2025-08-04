@echo off
echo Quick build for NewProject...

REM Create custom icon (if icon creation script exists)
if exist "create_icon.py" (
    echo Creating custom application icon...
    python create_icon.py
    if exist "newproject_icon.ico" (
        echo Custom icon created successfully.
        set ICON_PARAM=--icon=newproject_icon.ico
    ) else (
        echo Warning: Icon file not found. Using default.
        set ICON_PARAM=
    )
) else (
    echo No icon creation script found. Using default icon.
    set ICON_PARAM=
)

echo Building executable...
python -m PyInstaller --onefile --windowed --name=NewProject %ICON_PARAM% newproject.py

if exist "dist\NewProject.exe" (
    echo Build successful! Executable created at: dist\NewProject.exe
) else (
    echo Build failed! Check for errors above.
)

pause
