#!/usr/bin/env python3
"""
NewProject - Main Application

Description: A brief description of what this application does.

Author: Your Name
License: MIT
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Main application entry point."""
    print("NewProject v1.0.0")
    print("=================")
    print()
    print("Application starting...")
    
    # TODO: Add your main application logic here
    print("Hello, World!")
    
    print("Application finished.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
