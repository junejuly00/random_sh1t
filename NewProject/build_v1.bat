@echo off
echo Building NewProject v1.0...
echo ========================

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

echo Building executable with PyInstaller...
python -m PyInstaller --onefile --windowed --name=NewProject %ICON_PARAM% --distpath=dist --workpath=build --specpath=. newproject.py

if exist "dist\NewProject.exe" (
    echo.
    echo Build successful!
    echo Executable created at: dist\NewProject.exe
    echo.
    echo Creating release package...
    
    REM Create release directory
    if not exist "NewProject_v1.0.0" mkdir "NewProject_v1.0.0"
    
    REM Copy files to release directory
    copy "dist\NewProject.exe" "NewProject_v1.0.0\"
    copy "README.md" "NewProject_v1.0.0\"
    copy "LICENSE.txt" "NewProject_v1.0.0\"
    copy "CHANGELOG.md" "NewProject_v1.0.0\"
    
    echo Release package created in: NewProject_v1.0.0\
) else (
    echo Build failed! Check for errors above.
)

pause
