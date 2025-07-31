# KeyStalker - Keyboard Monitoring Application

## Overview
KeyStalker is a GUI application that runs in the background with system tray functionality. Monitor your keyboard usage with real-time statistics, funny messages, and visual heatmaps.

## Features

### 🖥️ GUI Interface
- **Main Window**: Control monitoring, view live statistics, and read activity logs
- **System Tray**: Minimize to system tray for background operation
- **Real-time Updates**: Live statistics updated every 5 seconds
- **Activity Log**: Funny messages and roasts displayed with timestamps

### 📊 Statistics & Visualization
- **Live Stats**: Top 10 most pressed keys with counts and percentages
- **Heatmap**: Visual bar chart of all key presses
- **Total Count**: Overall keyboard activity tracking

### 🎭 Entertainment
- **Funny Messages**: Humorous comments about your typing habits
- **Roasts**: Special messages for overused keys (Backspace, Enter, etc.)
- **Idle Detection**: Messages when you're not typing

## Getting Started

### Step 1: Create the Executable
1. **Double-click** `build_exe.bat` 
   - This will automatically create KeyStalker.exe
   - Wait 2-3 minutes for the build process to complete
   - The .exe file will appear in the same folder

2. **Alternative**: Use `quick_build.bat` for faster builds

### Step 2: Run KeyStalker
- **Double-click** `KeyStalker.exe` to start the application
- No additional software or installation required!

## Usage

### GUI Controls
- **Start Monitoring**: Begin tracking keyboard input
- **Stop Monitoring**: Pause tracking
- **Show Heatmap**: Display visual chart of key usage
- **Clear Data**: Reset all statistics

### Background Operation
1. Close the main window (click X) - application continues in system tray
2. Right-click tray icon for quick access to functions
3. Use "Show" from tray menu to restore main window
4. Use "Exit" from tray menu to completely close application

### System Tray Menu
- **Show**: Restore main window
- **Start/Stop Monitoring**: Toggle keyboard tracking
- **Show Heatmap**: Display statistics chart
- **Exit**: Close application completely

## Security & Privacy
- **Local Only**: All data stays on your computer
- **No Network**: No internet connection required or used
- **Temporary**: Data is cleared when application closes
- **Standalone**: No Python installation or dependencies needed

## Controls
- **Alt+F4**: Close main window (minimizes to tray)
- **System tray right-click**: Access all functions

## Troubleshooting

### Common Issues
1. **Permission Errors**: Right-click KeyStalker.exe → "Run as administrator"
2. **System Tray Not Visible**: Check system tray settings in Windows
3. **Antivirus Warning**: Add KeyStalker.exe to antivirus exceptions (common with PyInstaller executables)

## File Structure
- `build_exe.bat` - Creates the executable (run this first)
- `quick_build.bat` - Alternative build method
- `KeyStalker.exe` - The main application (appears after building)
- `KeyStalker.py` - Source code (for reference only)

## Tips
- Keep KeyStalker.exe running in the background for continuous monitoring
- Check the activity log for entertaining messages about your typing habits
- Use the heatmap feature to visualize your most used keys
- Clear data periodically to start fresh statistics
- The executable is portable - you can copy it to any Windows computer and run it
