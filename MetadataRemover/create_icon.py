#!/usr/bin/env python3
"""
Create icon for MetadataManager application
This script generates a custom .ico file for use with PyInstaller
"""

import os
from PIL import Image, ImageDraw

def create_icon():
    """Create a custom icon file for the application"""
    try:
        # Create icon image with multiple sizes for better quality
        icon_sizes = [16, 24, 32, 48, 64, 128, 256]
        icon_images = []
        
        for size in icon_sizes:
            icon_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_img)
            
            # Scale dimensions based on icon size
            scale = size / 32.0
            
            # Draw a camera-like icon
            # Camera body (rectangle)
            body_coords = [int(4*scale), int(10*scale), int(28*scale), int(26*scale)]
            draw.rectangle(body_coords, fill='#6c5ce7', outline='#2d3436', width=max(1, int(2*scale)))
            
            # Camera lens (circle)
            lens_outer = [int(10*scale), int(14*scale), int(22*scale), int(22*scale)]
            lens_inner = [int(12*scale), int(16*scale), int(20*scale), int(20*scale)]
            draw.ellipse(lens_outer, fill='#2d3436', outline='#ffffff', width=max(1, int(1*scale)))
            draw.ellipse(lens_inner, fill='#74b9ff')
            
            # Flash (small rectangle)
            flash_coords = [int(6*scale), int(6*scale), int(10*scale), int(10*scale)]
            draw.rectangle(flash_coords, fill='#fdcb6e', outline='#2d3436', width=max(1, int(1*scale)))
            
            # Viewfinder (small rectangle on top)
            viewfinder_coords = [int(14*scale), int(6*scale), int(18*scale), int(9*scale)]
            draw.rectangle(viewfinder_coords, fill='#2d3436')
            
            # Add a small lens reflection for better detail on larger sizes
            if size >= 32:
                reflection_coords = [int(13*scale), int(17*scale), int(16*scale), int(19*scale)]
                draw.ellipse(reflection_coords, fill='#ffffff', outline=None)
            
            icon_images.append(icon_img)
        
        # Save as ICO file in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'metadatamanager_icon.ico')
        
        # Convert to ICO format with multiple sizes
        icon_images[0].save(icon_path, format='ICO', sizes=[(size, size) for size in icon_sizes])
        
        print(f"✅ Icon created successfully: {icon_path}")
        return icon_path
        
    except Exception as e:
        print(f"❌ Error creating icon: {str(e)}")
        return None

if __name__ == "__main__":
    create_icon()
