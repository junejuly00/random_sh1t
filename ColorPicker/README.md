# ColorPicker - Advanced Color Picker & Palette Generator

A powerful and user-friendly GUI application for color picking, palette generation, and color management. Perfect for designers, developers, and anyone working with colors.

## 🎨 Features

### Color Picking & Formats
- **Interactive Color Picker**: Built-in color chooser dialog
- **Multiple Format Support**: HEX, RGB, HSV, HSL color formats
- **Real-time Preview**: Large color canvas showing current selection
- **Format Conversion**: Automatic conversion between all supported formats
- **Manual Input**: Enter colors directly in any supported format

### Palette Generation
- **Complementary Colors**: Generate perfect color complements
- **Analogous Palettes**: Create harmonious color schemes
- **Triadic Colors**: Generate balanced three-color palettes
- **Monochromatic Schemes**: Create single-hue variations
- **Random Palettes**: Generate inspiring random color combinations
- **Interactive Swatches**: Click any palette color to select it

### Color Management
- **Color History**: Automatically tracks your recent colors (up to 20)
- **Quick Selection**: Double-click history items to reselect
- **Palette Saving**: Save your favorite palettes as JSON files
- **Palette Loading**: Load previously saved palettes
- **History Export**: Export your color history for backup

### Productivity Tools
- **Clipboard Integration**: Copy colors in HEX or RGB format
- **Random Color Generator**: Generate random colors instantly
- **Color Inversion**: Quickly invert any color
- **Status Updates**: Real-time feedback on all operations

## 🚀 Getting Started

### System Requirements
- **Operating System**: Windows 7 or later
- **Memory**: 50MB RAM minimum
- **Storage**: 20MB free disk space
- **Display**: Any resolution (optimized for 800x600 and above)

### Installation & Usage
1. **Download**: Get the latest `ColorPicker.exe` from the releases
2. **Run**: Double-click the executable - no installation required!
3. **Start Picking**: Use the "🎨 Pick Color" button or enter color values manually

### First Time Setup
- No configuration required - the app works out of the box
- All features are immediately available
- Your color history will be automatically saved during the session

## 📖 How to Use

### Basic Color Picking
1. Click **"🎨 Pick Color"** to open the color chooser
2. Select your desired color and click OK
3. View the color in all supported formats (HEX, RGB, HSV, HSL)
4. Use **"Copy HEX"** or **"Copy RGB"** to copy to clipboard

### Creating Color Palettes
1. Select a base color using the color picker
2. Choose a palette generation method:
   - **🌈 Complementary**: Creates the opposite color
   - **🎨 Analogous**: Creates similar hues
   - **🔄 Triadic**: Creates three balanced colors
   - **✨ Random Palette**: Creates five random colors
   - **🎯 Monochromatic**: Creates brightness variations
3. Click any palette color to select it as your current color

### Working with History
- All selected colors are automatically added to your history
- **Double-click** any history item to reselect that color
- Use **"🗑️ Clear History"** to start fresh
- Use **"💾 Export History"** to save your colors

### Saving & Loading Palettes
- **Save**: Click "💾 Save Palette" to save current palette as JSON
- **Load**: Click "📁 Load Palette" to load a previously saved palette
- **Clear**: Click "🗑️ Clear" to remove current palette

### Quick Tools
- **🎲 Random Color**: Generate a completely random color
- **🔄 Invert Color**: Create the inverse of current color
- **Manual Input**: Type colors directly in the format fields

## 🎯 Use Cases

### For Designers
- Create cohesive color schemes for projects
- Explore color relationships and harmonies
- Maintain consistent brand colors
- Generate inspiration palettes

### For Developers
- Pick exact colors for UI elements
- Convert between color formats (HEX ↔ RGB)
- Create CSS color variables
- Test color accessibility combinations

### For Artists
- Explore color theory in practice
- Create reference palettes for artwork
- Study color relationships
- Generate mood-based color schemes

## 🔧 Technical Features

### Color Formats Supported
- **HEX**: `#FF5733` (web standard)
- **RGB**: `rgb(255, 87, 51)` (red, green, blue values)
- **HSV**: `hsv(9, 80%, 100%)` (hue, saturation, value)
- **HSL**: `hsl(9, 100%, 60%)` (hue, saturation, lightness)

### Palette Algorithms
- **Complementary**: 180° hue rotation
- **Analogous**: ±30° and ±60° hue variations
- **Triadic**: 120° hue intervals
- **Monochromatic**: Brightness variations (30%, 50%, 70%, 100%)
- **Random**: Full spectrum random generation

### File Formats
- **Palette Files**: JSON format with metadata
- **History Export**: JSON format with timestamps
- **Cross-Platform**: Compatible JSON structure

## 🛠️ Troubleshooting

### Common Issues

**"Failed to copy to clipboard"**
- Ensure no other application is blocking clipboard access
- Try selecting the color text and using Ctrl+C manually
- Restart the application if clipboard issues persist

**"Invalid color format"**
- Ensure HEX colors start with # (e.g., #FF0000)
- Check that RGB values are between 0-255
- Verify HSV/HSL percentages are properly formatted

**"Cannot save/load palette"**
- Check file permissions in the selected directory
- Ensure the file extension is .json for palette files
- Verify the file isn't corrupted if loading fails

**Performance Issues**
- Close other resource-intensive applications
- Restart ColorPicker if it becomes unresponsive
- Check available system memory

### Getting Help
- Check the status bar for operation feedback
- Use the built-in error messages for guidance
- Verify your color formats match the expected patterns

## 🔒 Privacy & Security

### Data Collection
- **No Data Collection**: ColorPicker doesn't collect or transmit any personal data
- **Local Storage Only**: All colors and palettes are stored locally
- **No Internet Required**: Fully offline application

### File Security
- **Safe File Operations**: Only reads/writes user-selected files
- **No System Changes**: Doesn't modify system settings or registry
- **Portable**: Can run from any location without installation

## 💡 Tips & Tricks

### Productivity Tips
- **Double-click history items** for quick color switching
- **Use keyboard shortcuts** in color input fields (Enter to apply)
- **Save frequently used palettes** for future projects
- **Export history** before clearing for backup

### Color Theory Tips
- **Complementary colors** create high contrast and attention
- **Analogous colors** create harmony and calmness
- **Monochromatic schemes** provide subtle sophistication
- **Triadic colors** offer vibrant yet balanced combinations

### Workflow Integration
- Copy HEX codes directly into CSS/HTML
- Use RGB values for design software
- Save project-specific palettes for consistency
- Export history to share with team members

## 📋 Version Information

- **Version**: 1.0.0
- **Release Date**: August 2025
- **Compatibility**: Windows 7/8/10/11
- **Size**: ~15MB (standalone executable)

## 🏗️ Technical Specifications

### Built With
- **Python 3.x**: Core application framework
- **Tkinter**: Native GUI framework
- **Colorsys**: Color space conversions
- **PyInstaller**: Executable packaging
- **JSON**: Data storage format

### Dependencies (Included)
- Python Standard Library (tkinter, colorsys, json, os, datetime)
- PyperClip (for clipboard functionality)
- Threading (for responsive UI)

---

**ColorPicker** - Making color selection simple, powerful, and enjoyable! 🎨

*Created with ❤️ for designers, developers, and color enthusiasts everywhere.*
