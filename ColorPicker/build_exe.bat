@echo off
echo Building ColorPicker executable...
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
python -m pip install pyperclip
if errorlevel 1 (
    echo Warning: Failed to install pyperclip. Clipboard functionality may be limited.
)

REM Create build directory if it doesn't exist
if not exist "ColorPicker_dist_beta" mkdir "ColorPicker_dist_beta"

REM Build the executable
echo.
echo Building executable with PyInstaller...
python -m PyInstaller --onefile --windowed --name=ColorPicker --distpath=ColorPicker_dist_beta colorpicker.py

REM Check if build was successful
if exist "ColorPicker_dist_beta\ColorPicker.exe" (
    echo.
    echo ============================================
    echo SUCCESS: ColorPicker.exe has been created!
    echo ============================================
    echo.
    echo Location: ColorPicker_dist_beta\ColorPicker.exe
    echo.
    
    REM Copy additional files to distribution folder
    if exist "README.md" copy "README.md" "ColorPicker_dist_beta\"
    if exist "LICENSE.txt" copy "LICENSE.txt" "ColorPicker_dist_beta\"
    
    echo Additional files copied to distribution folder.
    echo.
    echo You can now distribute the ColorPicker_dist_beta folder.
) else (
    echo.
    echo ==========================================
    echo ERROR: Failed to create ColorPicker.exe
    echo ==========================================
    echo.
    echo Please check the output above for errors.
)

echo.
pause
