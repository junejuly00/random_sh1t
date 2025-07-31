# KeyStalker - License Information

## Project License
**KeyStalker** - Original code created for this project
- **License**: MIT License (or your choice)
- **Author**: User-created project
- **Usage**: Free for personal and commercial use

---

## Third-Party Dependencies and Licenses

### 1. **pynput** - Keyboard and Mouse Input Monitoring
- **Version**: Latest stable
- **License**: LGPL v3 (GNU Lesser General Public License v3.0)
- **Author**: Moses Palmér
- **PyPI**: https://pypi.org/project/pynput/
- **GitHub**: https://github.com/moses-palmer/pynput
- **Usage**: Keyboard event listening and monitoring
- **License Details**: 
  - Free to use in both open source and proprietary applications
  - Must retain copyright notices
  - If you modify pynput itself, modifications must be released under LGPL
  - Your application code can remain proprietary

### 2. **matplotlib** - Plotting and Visualization
- **Version**: Latest stable
- **License**: PSF-based license (Python Software Foundation compatible)
- **License Type**: BSD-style license
- **Author**: Matplotlib Development Team
- **Website**: https://matplotlib.org/
- **GitHub**: https://github.com/matplotlib/matplotlib
- **Usage**: Creating keyboard heatmap visualizations
- **License Details**:
  - Free for commercial and non-commercial use
  - Very permissive license
  - Can be used in proprietary software

### 3. **numpy** - Numerical Computing
- **Version**: Latest stable
- **License**: BSD 3-Clause License
- **Author**: NumPy Developers
- **Website**: https://numpy.org/
- **GitHub**: https://github.com/numpy/numpy
- **Usage**: Mathematical operations for heatmap calculations
- **License Details**:
  - Free for commercial and non-commercial use
  - Very permissive license
  - Can be redistributed and modified

### 4. **Pillow (PIL)** - Image Processing
- **Version**: Latest stable
- **License**: HPND License (Historical Permission Notice and Disclaimer)
- **Author**: Pillow Contributors
- **Website**: https://pillow.readthedocs.io/
- **GitHub**: https://github.com/python-pillow/Pillow
- **Usage**: Creating system tray icons
- **License Details**:
  - Very permissive license
  - Free for commercial and non-commercial use
  - Allows modification and redistribution

### 5. **pystray** - System Tray Integration
- **Version**: Latest stable
- **License**: LGPL v3 (GNU Lesser General Public License v3.0)
- **Author**: Moses Palmér (same as pynput)
- **PyPI**: https://pypi.org/project/pystray/
- **GitHub**: https://github.com/moses-palmer/pystray
- **Usage**: System tray functionality and background operation
- **License Details**:
  - Same as pynput - LGPL v3
  - Free to use in proprietary applications
  - Must retain copyright notices

### 6. **tkinter** - GUI Framework
- **Version**: Built into Python
- **License**: Python Software Foundation License (PSF)
- **Author**: Python Software Foundation
- **Documentation**: https://docs.python.org/3/library/tkinter.html
- **Usage**: Main GUI interface, windows, buttons, text areas
- **License Details**:
  - Part of Python standard library
  - Very permissive license
  - Free for all uses

### 7. **Python Standard Libraries**
Used libraries that come with Python:
- **threading** - Multi-threading support
- **time** - Time operations and timestamps
- **collections.Counter** - Counting and statistics
- **random** - Random message selection
- **sys** - System operations
- **os** - Operating system interface

**License**: Python Software Foundation License (PSF)
- All standard library modules are free for commercial use

---

## License Compatibility Summary

### ✅ **Commercial Use**: ALLOWED
- All dependencies allow commercial use
- Can be distributed as proprietary software
- Can be sold or included in commercial products

### ✅ **Distribution**: ALLOWED
- Can distribute the executable (.exe) file
- Can share source code
- Can modify and redistribute

### ✅ **Modification**: ALLOWED
- Can modify all source code
- Can create derivative works
- Can rebrand and customize

### ⚠️ **Attribution Requirements**:
1. **pynput & pystray (LGPL v3)**:
   - Must retain copyright notices if distributing source
   - If you modify these libraries themselves, modifications must be open source
   - Your application code can remain proprietary

2. **Other libraries**: Minimal attribution requirements

---

## Recommended License Notice

If distributing KeyStalker, include this notice:

```
KeyStalker uses the following open source libraries:
- pynput (LGPL v3) - https://github.com/moses-palmer/pynput
- pystray (LGPL v3) - https://github.com/moses-palmer/pystray  
- matplotlib (BSD-style) - https://matplotlib.org/
- numpy (BSD 3-Clause) - https://numpy.org/
- Pillow (HPND) - https://pillow.readthedocs.io/

Full license texts available at respective project websites.
```

---

## For Executable Distribution

When distributing the `.exe` file:
- ✅ No source code disclosure required
- ✅ Can be used commercially
- ✅ Can be sold or included in products
- ℹ️ Consider including brief attribution in About dialog or documentation

---

## Summary for Your Project

**Your KeyStalker project is safe for**:
- Personal use ✅
- Commercial use ✅
- Distribution ✅
- Selling ✅
- Modification ✅
- Creating proprietary versions ✅

The licenses are all very permissive and commonly used in commercial software.
