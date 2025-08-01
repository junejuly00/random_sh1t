#!/usr/bin/env python3
"""
ColorPicker - A GUI Color Picker and Palette Generator
Author: Your Name
Date: August 2025
License: MIT License

A simple yet powerful color picker application with:
- Interactive color selection
- Multiple color format support (HEX, RGB, HSV, HSL)
- Color palette generation
- Color history
- Copy to clipboard functionality
- Save palettes to file
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import colorsys
import random
import json
import os
from datetime import datetime
import threading
import pyperclip


class ColorPickerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ColorPicker - Color Picker & Palette Generator")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Color history and palettes
        self.color_history = []
        self.current_palette = []
        self.current_color = "#FF0000"  # Default red
        
        # Create GUI
        self.create_widgets()
        self.update_color_display()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎨 ColorPicker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Color picker and info
        left_frame = ttk.LabelFrame(main_frame, text="Color Picker", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Color display canvas
        self.color_canvas = tk.Canvas(left_frame, width=200, height=200, 
                                    bg=self.current_color, relief='raised', bd=2)
        self.color_canvas.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Pick color button
        pick_btn = ttk.Button(left_frame, text="🎨 Pick Color", 
                             command=self.pick_color)
        pick_btn.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Color format labels and entries
        formats = [
            ("HEX:", "hex_entry"),
            ("RGB:", "rgb_entry"),
            ("HSV:", "hsv_entry"),
            ("HSL:", "hsl_entry")
        ]
        
        self.format_entries = {}
        for i, (label, entry_name) in enumerate(formats):
            ttk.Label(left_frame, text=label).grid(row=2+i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(left_frame, width=20)
            entry.grid(row=2+i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
            entry.bind('<Return>', lambda e, name=entry_name: self.update_from_entry(name))
            self.format_entries[entry_name] = entry
        
        # Copy buttons
        copy_frame = ttk.Frame(left_frame)
        copy_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(copy_frame, text="Copy HEX", 
                  command=lambda: self.copy_to_clipboard("hex")).grid(row=0, column=0, padx=2)
        ttk.Button(copy_frame, text="Copy RGB", 
                  command=lambda: self.copy_to_clipboard("rgb")).grid(row=0, column=1, padx=2)
        
        # Middle panel - Palette generator
        middle_frame = ttk.LabelFrame(main_frame, text="Palette Generator", padding="10")
        middle_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        middle_frame.columnconfigure(0, weight=1)
        
        # Palette generation buttons
        palette_buttons = [
            ("🌈 Complementary", self.generate_complementary),
            ("🎨 Analogous", self.generate_analogous),
            ("🔄 Triadic", self.generate_triadic),
            ("✨ Random Palette", self.generate_random_palette),
            ("🎯 Monochromatic", self.generate_monochromatic)
        ]
        
        for i, (text, command) in enumerate(palette_buttons):
            btn = ttk.Button(middle_frame, text=text, command=command)
            btn.grid(row=i, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Palette display frame
        self.palette_frame = ttk.Frame(middle_frame)
        self.palette_frame.grid(row=len(palette_buttons), column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Palette action buttons
        action_frame = ttk.Frame(middle_frame)
        action_frame.grid(row=len(palette_buttons)+1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="💾 Save Palette", 
                  command=self.save_palette).grid(row=0, column=0, padx=2)
        ttk.Button(action_frame, text="📁 Load Palette", 
                  command=self.load_palette).grid(row=0, column=1, padx=2)
        ttk.Button(action_frame, text="🗑️ Clear", 
                  command=self.clear_palette).grid(row=0, column=2, padx=2)
        
        # Right panel - History and tools
        right_frame = ttk.LabelFrame(main_frame, text="Color History & Tools", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        
        # History listbox
        ttk.Label(right_frame, text="Recent Colors:").grid(row=0, column=0, sticky=tk.W)
        
        history_frame = ttk.Frame(right_frame)
        history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        self.history_listbox = tk.Listbox(history_frame, height=8)
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_listbox.bind('<Double-Button-1>', self.select_from_history)
        
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                     command=self.history_listbox.yview)
        history_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_listbox.configure(yscrollcommand=history_scroll.set)
        
        # History buttons
        hist_btn_frame = ttk.Frame(right_frame)
        hist_btn_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(hist_btn_frame, text="🗑️ Clear History", 
                  command=self.clear_history).grid(row=0, column=0, padx=2)
        ttk.Button(hist_btn_frame, text="💾 Export History", 
                  command=self.export_history).grid(row=0, column=1, padx=2)
        
        # Random color generator
        ttk.Separator(right_frame, orient='horizontal').grid(row=3, column=0, 
                                                           sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(right_frame, text="Quick Tools:").grid(row=4, column=0, sticky=tk.W)
        
        ttk.Button(right_frame, text="🎲 Random Color", 
                  command=self.generate_random_color).grid(row=5, column=0, pady=2, sticky=(tk.W, tk.E))
        
        ttk.Button(right_frame, text="🔄 Invert Color", 
                  command=self.invert_color).grid(row=6, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Pick a color to get started!")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def pick_color(self):
        """Open color picker dialog"""
        color = colorchooser.askcolor(color=self.current_color, title="Pick a Color")
        if color[1]:  # If a color was selected
            self.current_color = color[1]
            self.update_color_display()
            self.add_to_history(self.current_color)
            self.status_var.set(f"Color selected: {self.current_color}")
    
    def update_color_display(self):
        """Update all color format displays"""
        try:
            # Update canvas
            self.color_canvas.configure(bg=self.current_color)
            
            # Convert hex to RGB
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Convert to different formats
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            h_hsl, l, s_hsl = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
            
            # Update entries
            self.format_entries['hex_entry'].delete(0, tk.END)
            self.format_entries['hex_entry'].insert(0, self.current_color.upper())
            
            self.format_entries['rgb_entry'].delete(0, tk.END)
            self.format_entries['rgb_entry'].insert(0, f"rgb({r}, {g}, {b})")
            
            self.format_entries['hsv_entry'].delete(0, tk.END)
            self.format_entries['hsv_entry'].insert(0, f"hsv({int(h*360)}, {int(s*100)}%, {int(v*100)}%)")
            
            self.format_entries['hsl_entry'].delete(0, tk.END)
            self.format_entries['hsl_entry'].insert(0, f"hsl({int(h_hsl*360)}, {int(s_hsl*100)}%, {int(l*100)}%)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating color display: {str(e)}")
    
    def update_from_entry(self, entry_name):
        """Update color from entry field"""
        try:
            value = self.format_entries[entry_name].get().strip()
            
            if entry_name == 'hex_entry':
                if not value.startswith('#'):
                    value = '#' + value
                # Validate hex color
                int(value[1:], 16)
                self.current_color = value
                
            # Add more format parsing here if needed
            
            self.update_color_display()
            self.add_to_history(self.current_color)
            
        except Exception as e:
            messagebox.showerror("Invalid Color", f"Invalid color format: {str(e)}")
    
    def copy_to_clipboard(self, format_type):
        """Copy color value to clipboard"""
        try:
            if format_type == "hex":
                value = self.current_color
            elif format_type == "rgb":
                value = self.format_entries['rgb_entry'].get()
            
            pyperclip.copy(value)
            self.status_var.set(f"Copied {value} to clipboard!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
    
    def generate_complementary(self):
        """Generate complementary color palette"""
        try:
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Complementary color
            comp_r, comp_g, comp_b = 255-r, 255-g, 255-b
            comp_color = f"#{comp_r:02x}{comp_g:02x}{comp_b:02x}"
            
            self.current_palette = [self.current_color, comp_color]
            self.display_palette()
            self.status_var.set("Generated complementary palette")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate palette: {str(e)}")
    
    def generate_analogous(self):
        """Generate analogous color palette"""
        try:
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            palette = []
            for offset in [-60, -30, 0, 30, 60]:  # Hue offsets in degrees
                new_h = (h + offset/360) % 1
                new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
                color = f"#{int(new_r*255):02x}{int(new_g*255):02x}{int(new_b*255):02x}"
                palette.append(color)
            
            self.current_palette = palette
            self.display_palette()
            self.status_var.set("Generated analogous palette")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate palette: {str(e)}")
    
    def generate_triadic(self):
        """Generate triadic color palette"""
        try:
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            palette = []
            for offset in [0, 120, 240]:  # 120-degree intervals
                new_h = (h + offset/360) % 1
                new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
                color = f"#{int(new_r*255):02x}{int(new_g*255):02x}{int(new_b*255):02x}"
                palette.append(color)
            
            self.current_palette = palette
            self.display_palette()
            self.status_var.set("Generated triadic palette")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate palette: {str(e)}")
    
    def generate_monochromatic(self):
        """Generate monochromatic color palette"""
        try:
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            palette = []
            for brightness in [0.3, 0.5, 0.7, 1.0]:  # Different brightness levels
                new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, v * brightness)
                color = f"#{int(new_r*255):02x}{int(new_g*255):02x}{int(new_b*255):02x}"
                palette.append(color)
            
            self.current_palette = palette
            self.display_palette()
            self.status_var.set("Generated monochromatic palette")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate palette: {str(e)}")
    
    def generate_random_palette(self):
        """Generate random color palette"""
        try:
            palette = []
            for _ in range(5):
                color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
                palette.append(color)
            
            self.current_palette = palette
            self.display_palette()
            self.status_var.set("Generated random palette")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate palette: {str(e)}")
    
    def display_palette(self):
        """Display current palette"""
        # Clear existing palette display
        for widget in self.palette_frame.winfo_children():
            widget.destroy()
        
        if not self.current_palette:
            return
        
        # Create color swatches
        for i, color in enumerate(self.current_palette):
            swatch = tk.Canvas(self.palette_frame, width=40, height=40, 
                             bg=color, relief='raised', bd=1)
            swatch.grid(row=0, column=i, padx=2, pady=2)
            swatch.bind('<Button-1>', lambda e, c=color: self.select_palette_color(c))
            
            # Add color label
            label = ttk.Label(self.palette_frame, text=color, font=('Arial', 8))
            label.grid(row=1, column=i, padx=2)
    
    def select_palette_color(self, color):
        """Select color from palette"""
        self.current_color = color
        self.update_color_display()
        self.add_to_history(color)
        self.status_var.set(f"Selected color from palette: {color}")
    
    def generate_random_color(self):
        """Generate a random color"""
        self.current_color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        self.update_color_display()
        self.add_to_history(self.current_color)
        self.status_var.set(f"Generated random color: {self.current_color}")
    
    def invert_color(self):
        """Invert the current color"""
        try:
            hex_color = self.current_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            inv_r, inv_g, inv_b = 255-r, 255-g, 255-b
            self.current_color = f"#{inv_r:02x}{inv_g:02x}{inv_b:02x}"
            self.update_color_display()
            self.add_to_history(self.current_color)
            self.status_var.set(f"Inverted color: {self.current_color}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to invert color: {str(e)}")
    
    def add_to_history(self, color):
        """Add color to history"""
        if color not in self.color_history:
            self.color_history.insert(0, color)
            if len(self.color_history) > 20:  # Keep only last 20 colors
                self.color_history = self.color_history[:20]
            self.update_history_display()
    
    def update_history_display(self):
        """Update history listbox"""
        self.history_listbox.delete(0, tk.END)
        for color in self.color_history:
            self.history_listbox.insert(tk.END, color)
    
    def select_from_history(self, event):
        """Select color from history"""
        selection = self.history_listbox.curselection()
        if selection:
            color = self.color_history[selection[0]]
            self.current_color = color
            self.update_color_display()
            self.status_var.set(f"Selected from history: {color}")
    
    def clear_history(self):
        """Clear color history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the color history?"):
            self.color_history.clear()
            self.update_history_display()
            self.status_var.set("Color history cleared")
    
    def clear_palette(self):
        """Clear current palette"""
        self.current_palette.clear()
        self.display_palette()
        self.status_var.set("Palette cleared")
    
    def save_palette(self):
        """Save current palette to file"""
        if not self.current_palette:
            messagebox.showwarning("No Palette", "No palette to save!")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Palette"
            )
            
            if filename:
                palette_data = {
                    "palette": self.current_palette,
                    "created": datetime.now().isoformat(),
                    "name": os.path.basename(filename).split('.')[0]
                }
                
                with open(filename, 'w') as f:
                    json.dump(palette_data, f, indent=2)
                
                self.status_var.set(f"Palette saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save palette: {str(e)}")
    
    def load_palette(self):
        """Load palette from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Load Palette"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    palette_data = json.load(f)
                
                if 'palette' in palette_data:
                    self.current_palette = palette_data['palette']
                else:
                    self.current_palette = palette_data  # Assume it's just a list
                
                self.display_palette()
                self.status_var.set(f"Palette loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load palette: {str(e)}")
    
    def export_history(self):
        """Export color history to file"""
        if not self.color_history:
            messagebox.showwarning("No History", "No color history to export!")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Export History"
            )
            
            if filename:
                history_data = {
                    "history": self.color_history,
                    "exported": datetime.now().isoformat(),
                    "count": len(self.color_history)
                }
                
                with open(filename, 'w') as f:
                    json.dump(history_data, f, indent=2)
                
                self.status_var.set(f"History exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    try:
        # Check if pyperclip is available
        import pyperclip
        
        # Create and run the application
        app = ColorPickerGUI()
        app.run()
        
    except ImportError:
        print("Warning: pyperclip not found. Install it with: pip install pyperclip")
        print("Clipboard functionality will be limited.")
        
        # Run without clipboard support
        app = ColorPickerGUI()
        app.run()
        
    except Exception as e:
        print(f"Error starting ColorPicker: {str(e)}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
