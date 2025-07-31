#!/usr/bin/env python3
"""
Test script to verify the GUI components work properly
"""

try:
    import tkinter as tk
    print("✓ tkinter imported successfully")
except ImportError as e:
    print(f"✗ tkinter import failed: {e}")

try:
    import pystray
    print("✓ pystray imported successfully")
except ImportError as e:
    print(f"✗ pystray import failed: {e}")

try:
    from PIL import Image, ImageDraw
    print("✓ PIL imported successfully")
except ImportError as e:
    print(f"✗ PIL import failed: {e}")

try:
    from pynput import keyboard
    print("✓ pynput imported successfully")
except ImportError as e:
    print(f"✗ pynput import failed: {e}")

try:
    import matplotlib.pyplot as plt
    print("✓ matplotlib imported successfully")
except ImportError as e:
    print(f"✗ matplotlib import failed: {e}")

print("\nAll imports tested. If all show ✓, the main application should work.")
