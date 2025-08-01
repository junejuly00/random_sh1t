# 🖼️ Random Image Viewer

A modern, user-friendly desktop application that fetches and displays random images from the internet. Built with Python and Tkinter, packaged as a standalone executable.

## ✨ Features

### 🎯 Core Functionality
- **Random Image Fetching** - Downloads high-quality images from reliable sources
- **Category Selection** - Choose from 20+ categories (nature, animals, art, etc.)
- **Multiple Image Sources** - Automatic fallback system for reliability
- **Auto-Save** - All images automatically saved to local folder

### 🖥️ User Interface
- **Modern GUI** - Clean, intuitive interface with progress indicators
- **Image Viewer** - Built-in viewer with scrollbars for large images
- **Real-time Status** - Live updates during image fetching
- **Responsive Design** - Adapts to different window sizes

### 💾 File Management
- **Smart Saving** - Organized filenames with timestamps and categories
- **Custom Save** - Save images with custom names and locations
- **Folder Access** - Quick access to downloaded images folder
- **Multiple Formats** - Support for JPEG, PNG, and other image formats

## 🚀 Getting Started

### Quick Start
1. **Download** the `RandomImageViewer.exe` file
2. **Double-click** to run (no installation required!)
3. **Click "Get Random Image"** to start fetching images
4. **Use "Change Category"** to switch between image types

### System Requirements
- **OS**: Windows 7/8/10/11 (64-bit)
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 50MB free space (plus space for downloaded images)
- **Internet**: Active connection required for image fetching

## 🎛️ How to Use

### Basic Operations
1. **🖼️ Get Random Image** - Fetches a new random image
2. **🎲 Change Category** - Switches to a different image category
3. **💾 Save Image** - Saves current image with custom filename
4. **📋 Copy Info** - Copies image details to clipboard
5. **📁 Open Folder** - Opens the downloaded images folder

### Available Categories
- **Nature**: landscape, mountains, forest, ocean, flowers
- **Urban**: city, architecture, travel, photography
- **Creative**: art, abstract, minimal, patterns, texture
- **Tech**: technology, space
- **Lifestyle**: food, animals

### Image Specifications
- **Sizes**: Various resolutions from 400x300 to 1024x768
- **Format**: JPEG (for compatibility and smaller file sizes)
- **Quality**: High-quality images from curated sources
- **Sources**: Lorem Picsum, Placeholder services with fallback support

## 📁 File Structure

```
RandomImageViewer.exe          # Main executable
downloaded_images/             # Auto-created folder for saved images
├── 20250801_120000_nature_800x600.jpg
├── 20250801_120030_animals_640x480.jpg
└── ...
```

## 🔧 Troubleshooting

### Common Issues

**"Failed to fetch image" Error**
- Check your internet connection
- Try changing categories
- The app uses multiple fallback sources automatically

**Images not saving**
- Ensure write permissions in the application folder
- Check available disk space
- The app creates a `downloaded_images` folder automatically

**Application won't start**
- Run as administrator if needed
- Check Windows Defender/antivirus settings
- Ensure Windows is up to date

**Slow image loading**
- This is normal for larger images or slower connections
- The progress bar shows loading status
- Try smaller image categories

### Performance Tips
- **Close other applications** if experiencing slow performance
- **Clear downloaded_images folder** periodically to save disk space
- **Use wired connection** for faster image downloads
- **Change categories** if one source is slow

## 🔒 Privacy & Security

### Data Collection
- **No personal data collected** - The app only fetches public images
- **No tracking** - No analytics or user behavior monitoring
- **Local storage only** - All images saved locally on your computer

### Internet Usage
- **HTTPS connections** - Secure connections to image sources
- **Minimal data** - Only downloads requested images
- **No uploads** - App never sends your data anywhere

### Permissions
- **Network access** - Required for downloading images
- **File system** - Creates and writes to downloaded_images folder
- **No admin rights** - Runs with standard user permissions

## 🆘 Support

### Getting Help
- **Check this README** for common solutions
- **Review error messages** for specific issues
- **Try different categories** if one isn't working
- **Restart the application** for persistent issues

### Known Limitations
- Requires active internet connection
- Image availability depends on external sources
- Some corporate networks may block image sources
- Very large images may take longer to load

## 📋 Version Information

- **Version**: 1.0.0
- **Build Date**: August 2025
- **Python Version**: 3.x compatible
- **GUI Framework**: Tkinter (built into Windows Python)
- **Image Library**: Pillow (PIL)
- **HTTP Library**: Requests

## 🔄 Updates

This is a standalone executable that doesn't auto-update. For newer versions:
1. Download the latest `RandomImageViewer.exe`
2. Replace the old file
3. Your downloaded images will be preserved

---

**Enjoy exploring random images from around the internet! 🌍📸**
