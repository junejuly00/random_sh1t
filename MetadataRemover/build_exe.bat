@echo off
echo Building MetadataManager v1.0 executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install required dependencies
echo Installing required dependencies...
python -m pip install Pillow >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install Pillow (PIL). This is required for image processing.
    echo Trying alternative installation method...
    pip install Pillow
    if errorlevel 1 (
        echo Still failed. Please install Pillow manually: pip install Pillow
        pause
        exit /b 1
    )
)

REM Create build directory if it doesn't exist
if not exist "MetadataManager_v1.0" mkdir "MetadataManager_v1.0"

REM Create custom icon
echo.
echo Creating custom application icon...
python create_icon.py
set ICON_CREATE_RESULT=%errorlevel%
if %ICON_CREATE_RESULT% neq 0 (
    echo Warning: Failed to create custom icon. Using default.
    set ICON_PARAM=
) else (
    if exist "metadatamanager_icon.ico" (
        echo Custom icon created successfully.
        set ICON_PARAM=--icon=metadatamanager_icon.ico
    ) else (
        echo Warning: Icon file not found. Using default.
        set ICON_PARAM=
    )
)

REM Build the executable
echo.
echo Building executable with PyInstaller...
echo Debug: ICON_PARAM = %ICON_PARAM%

if exist "MetadataRemover.spec" (
    echo Using spec file for advanced build configuration...
    python -m PyInstaller --distpath=MetadataManager_v1.0 MetadataRemover.spec
    set BUILD_RESULT=%errorlevel%
) else (
    echo Using command line parameters...
    if "%ICON_PARAM%"=="" (
        echo Building without custom icon...
        python -m PyInstaller --onefile --windowed --name=MetadataManager --distpath=MetadataManager_v1.0 metadataremover.py
    ) else (
        echo Building with custom icon...
        python -m PyInstaller --onefile --windowed --name=MetadataManager --distpath=MetadataManager_v1.0 %ICON_PARAM% metadataremover.py
    )
    set BUILD_RESULT=%errorlevel%
)

echo Build completed with result: %BUILD_RESULT%

REM Check if build was successful
if exist "MetadataManager_v1.0\MetadataManager.exe" (
    echo.
    echo ============================================
    echo SUCCESS: MetadataManager v1.0 has been created!
    echo ============================================
    echo.
    echo Location: MetadataManager_v1.0\MetadataManager.exe
    echo.
    
    REM Copy additional files to distribution folder
    if exist "README.md" copy "README.md" "MetadataManager_v1.0\"
    if exist "LICENSE.txt" copy "LICENSE.txt" "MetadataManager_v1.0\"
    if exist "CHANGELOG.md" copy "CHANGELOG.md" "MetadataManager_v1.0\"
    
    echo Additional documentation copied to distribution folder.
    echo.
    echo You can now distribute the MetadataManager_v1.0 folder.
    echo.
    echo ============================================
    echo MetadataManager v1.0 is ready for release!
    echo ============================================
) else (
    echo.
    echo ==========================================
    echo ERROR: Failed to create MetadataManager.exe
    echo ==========================================
    echo.
    echo Please check the output above for errors.
    echo Trying to find executable with alternate name...
    if exist "MetadataManager_v1.0\MetadataRemover.exe" (
        echo Found MetadataRemover.exe - renaming to MetadataManager.exe
        ren "MetadataManager_v1.0\MetadataRemover.exe" "MetadataManager.exe"
    )
)

echo.
pause
