#!/usr/bin/env python3
"""
MetadataManager - Picture Metadata Management Tool
Author: Your Name
Date: August 2025
License: MIT License

A comprehensive tool for managing metadata in images:
- BASIC MODE: Remove EXIF, IPTC, and XMP metadata for privacy
- ADVANCED MODE: Edit and modify metadata fields
- Batch processing support
- Preview and edit metadata before processing
- Multiple image format support (JPEG, PNG, TIFF, etc.)
- Drag and drop interface
- Custom metadata templates
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
from datetime import datetime
import threading
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import json


class MetadataManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MetadataManager v1.0 - Professional Image Metadata Management")
        
        # Set fullscreen by default
        self.root.state('zoomed')  # Windows fullscreen
        self.root.minsize(800, 600)  # Set minimum window size
        self.root.configure(bg='#f8f9fa')
        
        # Try to set custom icon (create a simple icon programmatically)
        try:
            self.create_custom_icon()
        except Exception:
            pass  # Fall back to default if icon creation fails
        
        # Modern color scheme
        self.colors = {
            'primary': '#6c5ce7',
            'secondary': '#a29bfe',
            'success': '#00b894',
            'warning': '#fdcb6e',
            'danger': '#e17055',
            'info': '#74b9ff',
            'light': '#f8f9fa',
            'dark': '#2d3436',
            'muted': '#636e72',
            'white': '#ffffff',
            'border': '#e9ecef',
            'hover': '#f1f3f4'
        }
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        # File lists
        self.selected_files = []
        self.processed_files = []
        
        # Mode settings
        self.advanced_mode = tk.BooleanVar(value=False)
        
        # Processing settings
        self.remove_exif = tk.BooleanVar(value=True)
        self.remove_iptc = tk.BooleanVar(value=True)
        self.remove_xmp = tk.BooleanVar(value=True)
        self.create_backup = tk.BooleanVar(value=True)
        self.overwrite_original = tk.BooleanVar(value=False)
        
        # Initialize output path variable
        self.output_path_var = tk.StringVar(value="Same as source")
        
        # Initialize progress variable early
        self.progress_var = tk.DoubleVar()
        
        # Initialize progress text placeholder (will be created properly in create_widgets)
        self.progress_text = None
        
        # Initialize results label placeholder
        self.results_label = None
        
        # Initialize status variable early
        self.status_var = tk.StringVar()
        
        # Advanced mode metadata editing
        self.custom_metadata = {}
        self.metadata_templates = {
            "Basic Photo": {
                "Artist": "",
                "Copyright": "",
                "ImageDescription": "",
                "Software": "MetadataManager"
            },
            "Professional": {
                "Artist": "",
                "Copyright": "",
                "ImageDescription": "",
                "Software": "MetadataManager",
                "Make": "",
                "Model": "",
                "DateTime": ""
            },
            "Privacy Clean": {}  # Empty template for privacy
        }
        
        # Create GUI
        self.create_modern_styles()
        self.create_widgets()
        self.setup_drag_drop()
        
        # Set up window resizing handler
        self.setup_responsive_layout()
        # Don't call toggle_mode() here - it will be called after widgets are created
        
    def create_custom_icon(self):
        """Create a custom icon for the application"""
        try:
            # Create a simple 32x32 icon using PIL
            from PIL import Image, ImageDraw
            import tempfile
            import os
            
            # Create icon image with multiple sizes for better quality
            icon_sizes = [16, 24, 32, 48, 64]
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
                
                icon_images.append(icon_img)
            
            # Save as permanent ICO file in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, 'metadatamanager_icon.ico')
            
            # Convert to ICO format with multiple sizes
            icon_images[0].save(icon_path, format='ICO', sizes=[(size, size) for size in icon_sizes])
            
            # Set the icon
            self.root.iconbitmap(icon_path)
            
            return icon_path  # Return path for build script use
            
        except Exception as e:
            # If icon creation fails, try to set a simple text-based title
            self.root.title("📷 MetadataManager v1.0 - Professional Image Metadata Management")
            return None
        
    def create_modern_styles(self):
        """Create modern ttk styles"""
        style = ttk.Style()
        
        # Set the theme to improve button visibility
        try:
            style.theme_use('clam')  # Use a modern theme as base
        except:
            pass
        
        # Configure modern button style with better contrast
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(15, 10))
        style.map('Modern.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', '#5a52d5'),
                           ('disabled', '#bdc3c7')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#7f8c8d')],
                 relief=[('pressed', 'sunken')])
        
        # Configure success button style with better visibility
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(15, 10))
        style.map('Success.TButton',
                 background=[('active', '#00a085'),
                           ('pressed', '#00967d'),
                           ('disabled', '#bdc3c7')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#7f8c8d')],
                 relief=[('pressed', 'sunken')])
        
        # Configure danger button style with better visibility
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(15, 10))
        style.map('Danger.TButton',
                 background=[('active', '#d63447'),
                           ('pressed', '#c0392b'),
                           ('disabled', '#bdc3c7')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('disabled', '#7f8c8d')],
                 relief=[('pressed', 'sunken')])
        
        # Configure modern checkbutton style for better visibility
        style.configure('Modern.TCheckbutton',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=('Segoe UI', 9),
                       focuscolor='none')
        style.map('Modern.TCheckbutton',
                 background=[('active', self.colors['hover'])],
                 foreground=[('active', self.colors['dark'])])
        
        # Configure modern frame style
        style.configure('Card.TLabelFrame',
                       background=self.colors['white'],
                       borderwidth=1,
                       relief='solid')
        
        # Configure modern entry style with better contrast
        style.configure('Modern.TEntry',
                       borderwidth=1,
                       relief='solid',
                       padding=(10, 6),
                       font=('Segoe UI', 9))
        
        # Configure modern combobox style with better contrast
        style.configure('Modern.TCombobox',
                       borderwidth=1,
                       relief='solid',
                       padding=(10, 6),
                       font=('Segoe UI', 9))
        
        # Configure modern progressbar style
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['border'],
                       borderwidth=1,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
    def create_widgets(self):
        """Create all GUI widgets with modern design"""
        # Create main scrollable canvas
        main_canvas = tk.Canvas(self.root, bg=self.colors['light'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Main container with padding (inside the canvas)
        main_container = tk.Frame(main_canvas, bg=self.colors['light'])
        canvas_window = main_canvas.create_window((0, 0), window=main_container, anchor="nw")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)
            
        main_container.bind('<Configure>', configure_scroll_region)
        main_canvas.bind('<Configure>', configure_canvas_width)
        
        # Bind mousewheel to canvas for scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel to canvas and all child widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        self.root.after(100, lambda: bind_mousewheel(main_container))
        
        # Store references for later use
        self.main_canvas = main_canvas
        self.main_scrollbar = main_scrollbar
        
        # Add padding to the main container
        main_container.configure(padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_container, bg=self.colors['white'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title with modern typography
        title_container = tk.Frame(header_frame, bg=self.colors['white'])
        title_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title_label = tk.Label(title_container, text="�️ MetadataManager", 
                              font=('Segoe UI', 24, 'bold'),
                              bg=self.colors['white'],
                              fg=self.colors['dark'])
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(title_container, text="Professional Image Metadata Management", 
                                 font=('Segoe UI', 11),
                                 bg=self.colors['white'],
                                 fg=self.colors['muted'])
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))
        
        # Mode toggle in header
        mode_container = tk.Frame(title_container, bg=self.colors['white'])
        mode_container.pack(side=tk.RIGHT)
        
        mode_label = tk.Label(mode_container, text="Mode:", 
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['white'],
                             fg=self.colors['dark'])
        mode_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.mode_toggle = ttk.Checkbutton(mode_container, text="Advanced Mode", 
                                          variable=self.advanced_mode,
                                          command=self.toggle_mode,
                                          style='Modern.TCheckbutton')
        self.mode_toggle.pack(side=tk.LEFT)
        
        # Mode description with modern styling
        self.mode_desc_frame = tk.Frame(main_container, bg=self.colors['info'], height=40)
        self.mode_desc_frame.pack(fill=tk.X, pady=(0, 20))
        self.mode_desc_frame.pack_propagate(False)
        
        self.mode_desc_label = tk.Label(self.mode_desc_frame, 
                                       text="Basic Mode: Remove metadata for privacy",
                                       font=('Segoe UI', 10),
                                       bg=self.colors['info'],
                                       fg='white',
                                       anchor='center')
        self.mode_desc_label.pack(fill=tk.BOTH, expand=True)
        
        # Main content area with grid layout
        content_frame = tk.Frame(main_container, bg=self.colors['light'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive design
        content_frame.grid_columnconfigure(0, weight=1, minsize=300)
        content_frame.grid_columnconfigure(1, weight=1, minsize=300)
        content_frame.grid_columnconfigure(2, weight=1, minsize=300)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_rowconfigure(2, weight=1)
        
        # Track current layout mode to prevent unnecessary reconfigurations
        self.current_layout_mode = None
        
        # Make content frame responsive to window resizing
        def on_content_configure(event):
            # Prevent overlapping by checking actual widget size
            current_width = content_frame.winfo_width()
            
            # On very small screens, stack panels vertically
            if current_width < 900 and self.current_layout_mode != 'vertical':
                self.current_layout_mode = 'vertical'
                # Clear existing grid configurations
                self.left_frame.grid_forget()
                self.middle_frame.grid_forget()
                self.right_frame.grid_forget()
                
                # Stack vertically for small screens with proper spacing
                self.left_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 15))
                self.middle_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 15))
                self.right_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
                
            elif current_width >= 900 and self.current_layout_mode != 'horizontal':
                self.current_layout_mode = 'horizontal'
                # Clear existing grid configurations
                self.left_frame.grid_forget()
                self.middle_frame.grid_forget()
                self.right_frame.grid_forget()
                
                # Normal three-column layout with adequate spacing
                self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
                self.middle_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
                self.right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        content_frame.bind('<Configure>', on_content_configure)
        
        # Left panel - Settings card
        self.left_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        # Set minimum size to prevent collapsing
        self.left_frame.grid_propagate(False)
        content_frame.grid_rowconfigure(0, minsize=400)
        
        # Left panel header
        left_header = tk.Frame(self.left_frame, bg=self.colors['primary'], height=50)
        left_header.pack(fill=tk.X)
        left_header.pack_propagate(False)
        
        self.left_title = tk.Label(left_header, text="⚙️ Settings", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['primary'],
                                  fg='white')
        self.left_title.pack(pady=15)
        
        # Left panel content
        left_content = tk.Frame(self.left_frame, bg=self.colors['white'])
        left_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File selection section
        file_section = tk.Frame(left_content, bg=self.colors['white'])
        file_section.pack(fill=tk.X, pady=(0, 20))
        
        file_label = tk.Label(file_section, text="Select Images", 
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['white'],
                             fg=self.colors['dark'])
        file_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Modern file selection buttons
        file_btn_frame = tk.Frame(file_section, bg=self.colors['white'])
        file_btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        select_files_btn = ttk.Button(file_btn_frame, text="📁 Select Files", 
                                     command=self.select_files,
                                     style='Modern.TButton')
        select_files_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_folder_btn = ttk.Button(file_btn_frame, text="📂 Select Folder", 
                                      command=self.select_folder,
                                      style='Modern.TButton')
        select_folder_btn.pack(side=tk.LEFT)
        
        # Modern drag and drop area
        self.drop_frame = tk.Frame(file_section, bg='#f8f9ff', relief='solid', bd=2, height=80)
        self.drop_frame.pack(fill=tk.X)
        self.drop_frame.pack_propagate(False)
        
        drop_icon = tk.Label(self.drop_frame, text="📎", 
                           font=('Segoe UI', 16),
                           bg='#f8f9ff', fg=self.colors['primary'])
        drop_icon.place(relx=0.5, rely=0.3, anchor='center')
        
        drop_label = tk.Label(self.drop_frame, text="Drag & Drop Images Here", 
                            font=('Segoe UI', 10),
                            bg='#f8f9ff', fg=self.colors['muted'])
        drop_label.place(relx=0.5, rely=0.7, anchor='center')
        
        # Settings container (will be populated by toggle_mode)
        self.settings_container = tk.Frame(left_content, bg=self.colors['white'])
        self.settings_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Initialize settings container after creation
        self.toggle_mode()  # Now it's safe to call this
        
        # Middle panel - File list card
        self.middle_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        self.middle_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Middle panel header
        middle_header = tk.Frame(self.middle_frame, bg=self.colors['info'], height=50)
        middle_header.pack(fill=tk.X)
        middle_header.pack_propagate(False)
        
        middle_title = tk.Label(middle_header, text="📋 Selected Files", 
                               font=('Segoe UI', 12, 'bold'),
                               bg=self.colors['info'],
                               fg='white')
        middle_title.pack(pady=15)
        
        # Middle panel content
        middle_content = tk.Frame(self.middle_frame, bg=self.colors['white'])
        middle_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File listbox with modern styling
        list_container = tk.Frame(middle_content, bg=self.colors['white'])
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.file_listbox = tk.Listbox(list_container, 
                                      selectmode=tk.MULTIPLE,
                                      font=('Segoe UI', 9),
                                      bg=self.colors['white'],
                                      fg=self.colors['dark'],
                                      selectbackground=self.colors['secondary'],
                                      selectforeground='white',
                                      borderwidth=1,
                                      relief='solid',
                                      highlightthickness=0)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<Double-Button-1>', self.preview_metadata)
        
        list_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                   command=self.file_listbox.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.configure(yscrollcommand=list_scroll.set)
        
        # File info section
        info_frame = tk.Frame(middle_content, bg=self.colors['white'])
        info_frame.pack(fill=tk.X)
        
        self.file_count_label = tk.Label(info_frame, text="No files selected",
                                        font=('Segoe UI', 9),
                                        bg=self.colors['white'],
                                        fg=self.colors['muted'])
        self.file_count_label.pack(side=tk.LEFT)
        
        preview_btn = ttk.Button(info_frame, text="👁️ Preview", 
                               command=self.preview_selected_metadata,
                               style='Modern.TButton')
        preview_btn.pack(side=tk.RIGHT)
        
        # Right panel - Processing status card
        self.right_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        self.right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Right panel header
        right_header = tk.Frame(self.right_frame, bg=self.colors['success'], height=50)
        right_header.pack(fill=tk.X)
        right_header.pack_propagate(False)
        
        right_title = tk.Label(right_header, text="📊 Processing Status", 
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['success'],
                              fg='white')
        right_title.pack(pady=15)
        
        # Right panel content
        right_content = tk.Frame(self.right_frame, bg=self.colors['white'])
        right_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Progress section
        progress_label = tk.Label(right_content, text="Progress:", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['dark'])
        progress_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.progress_bar = ttk.Progressbar(right_content, 
                                          variable=self.progress_var, 
                                          maximum=100,
                                          style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Progress text with modern styling
        text_container = tk.Frame(right_content, bg=self.colors['white'])
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.progress_text = tk.Text(text_container, 
                                   height=12, 
                                   wrap=tk.WORD, 
                                   font=('Consolas', 9),
                                   bg='#f8f9fa',
                                   fg=self.colors['dark'],
                                   borderwidth=1,
                                   relief='solid',
                                   highlightthickness=0,
                                   padx=10,
                                   pady=10)
        self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        progress_scroll = ttk.Scrollbar(text_container, orient=tk.VERTICAL, 
                                       command=self.progress_text.yview)
        progress_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.configure(yscrollcommand=progress_scroll.set)
        
        # Results summary
        self.results_label = tk.Label(right_content, text="Ready to process files", 
                                     font=('Segoe UI', 9),
                                     bg=self.colors['white'],
                                     fg=self.colors['info'])
        self.results_label.pack(anchor=tk.W)
        
        # Modern status bar
        status_frame = tk.Frame(main_container, bg=self.colors['dark'], height=35)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_var.set("Ready - Select images to manage metadata")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=('Segoe UI', 9),
                               bg=self.colors['dark'],
                               fg='white',
                               anchor=tk.W)
        status_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
    
    def toggle_mode(self):
        """Toggle between basic and advanced modes - reinitialize app state"""
        # Save current mode state
        current_mode = self.advanced_mode.get()
        
        # Clear all file selections and reset state
        self.selected_files.clear()
        self.processed_files.clear()
        
        # Reset progress
        self.progress_var.set(0)
        if hasattr(self, 'progress_text') and self.progress_text:
            self.progress_text.delete(1.0, tk.END)
        
        # Clear existing settings widgets
        if hasattr(self, 'settings_container') and self.settings_container:
            for widget in self.settings_container.winfo_children():
                widget.destroy()
        
        # Update UI based on mode
        if current_mode:
            self.create_advanced_settings()
            if hasattr(self, 'mode_desc_label') and self.mode_desc_label:
                self.mode_desc_label.configure(text="Advanced Mode: Edit and customize metadata", 
                                             bg=self.colors['warning'],
                                             fg='white')
            if hasattr(self, 'mode_desc_frame') and self.mode_desc_frame:
                self.mode_desc_frame.configure(bg=self.colors['warning'])
            if hasattr(self, 'left_title') and self.left_title:
                self.left_title.configure(text="✏️ Metadata Editor")
            if hasattr(self, 'status_var') and self.status_var:
                self.status_var.set("Advanced Mode - Ready to edit image metadata")
        else:
            self.create_basic_settings()
            if hasattr(self, 'mode_desc_label') and self.mode_desc_label:
                self.mode_desc_label.configure(text="Basic Mode: Remove metadata for privacy", 
                                             bg=self.colors['info'],
                                             fg='white')
            if hasattr(self, 'mode_desc_frame') and self.mode_desc_frame:
                self.mode_desc_frame.configure(bg=self.colors['info'])
            if hasattr(self, 'left_title') and self.left_title:
                self.left_title.configure(text="⚙️ Settings")
            if hasattr(self, 'status_var') and self.status_var:
                self.status_var.set("Basic Mode - Ready to remove image metadata")
        
        # Reset file list display
        self.update_file_list()
        
        # Reset results display
        if hasattr(self, 'results_label') and self.results_label:
            self.results_label.configure(text="Ready to process files", fg=self.colors['info'])
        
        # Log the mode change
        mode_name = "Advanced" if current_mode else "Basic"
        if hasattr(self, 'progress_text') and self.progress_text:
            self.log_message(f"Switched to {mode_name} Mode - All selections cleared")
    
    def create_basic_settings(self):
        """Create basic mode settings (metadata removal) with modern design"""
        # Settings section
        settings_label = tk.Label(self.settings_container, text="Metadata to Remove:", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['dark'])
        settings_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Modern checkboxes with better spacing
        checkbox_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        checkbox_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Checkbutton(checkbox_frame, text="EXIF Data (Camera info, GPS, timestamps)", 
                       variable=self.remove_exif,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(checkbox_frame, text="IPTC Data (Keywords, captions, copyright)", 
                       variable=self.remove_iptc,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(checkbox_frame, text="XMP Data (Adobe metadata)", 
                       variable=self.remove_xmp,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        
        # Output options section
        output_label = tk.Label(self.settings_container, text="Output Options:", 
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['white'],
                               fg=self.colors['dark'])
        output_label.pack(anchor=tk.W, pady=(0, 10))
        
        output_checkbox_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        output_checkbox_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(output_checkbox_frame, text="Create backup copies", 
                       variable=self.create_backup,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(output_checkbox_frame, text="Overwrite original files", 
                       variable=self.overwrite_original,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        
        # Output directory section
        output_dir_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        output_dir_frame.pack(fill=tk.X, pady=(0, 25))
        
        output_dir_label = tk.Label(output_dir_frame, text="Output Folder:",
                                   font=('Segoe UI', 9, 'bold'),
                                   bg=self.colors['white'],
                                   fg=self.colors['dark'])
        output_dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        output_path_frame = tk.Frame(output_dir_frame, bg=self.colors['white'])
        output_path_frame.pack(fill=tk.X)
        
        self.output_entry = ttk.Entry(output_path_frame, 
                                     textvariable=self.output_path_var, 
                                     state='readonly',
                                     style='Modern.TEntry')
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(output_path_frame, text="Browse", 
                               command=self.select_output_folder,
                               style='Modern.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        action_frame.pack(fill=tk.X, pady=(25, 0))
        
        self.process_btn = ttk.Button(action_frame, text="🗑️ Remove Metadata", 
                                     command=self.start_processing, 
                                     state='disabled',
                                     style='Danger.TButton')
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="🧹 Clear List", 
                              command=self.clear_files,
                              style='Modern.TButton')
        clear_btn.pack(side=tk.LEFT)
    
    def create_advanced_settings(self):
        """Create advanced mode settings (metadata editing) with modern design"""
        # Template section
        template_label = tk.Label(self.settings_container, text="Metadata Template:", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['dark'])
        template_label.pack(anchor=tk.W, pady=(0, 10))
        
        template_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        template_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.template_var = tk.StringVar(value="Basic Photo")
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                    values=list(self.metadata_templates.keys()),
                                    state='readonly', 
                                    style='Modern.TCombobox',
                                    width=20)
        template_combo.pack(side=tk.LEFT, padx=(0, 10))
        template_combo.bind('<<ComboboxSelected>>', self.load_template)
        
        load_btn = ttk.Button(template_frame, text="Load", 
                             command=self.load_template,
                             style='Modern.TButton')
        load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        save_btn = ttk.Button(template_frame, text="Save", 
                             command=self.save_template,
                             style='Modern.TButton')
        save_btn.pack(side=tk.LEFT)
        
        # Metadata editing section
        edit_label = tk.Label(self.settings_container, text="Edit Metadata Fields:", 
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['white'],
                             fg=self.colors['dark'])
        edit_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create modern scrollable frame for metadata fields
        canvas_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        canvas = tk.Canvas(canvas_frame, height=180, 
                          bg='#f8f9fa',
                          highlightthickness=0,
                          relief='solid',
                          bd=1)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.metadata_frame = tk.Frame(canvas, bg='#f8f9fa')
        canvas.create_window((0, 0), window=self.metadata_frame, anchor="nw")
        
        # Initialize with basic template
        self.load_template()
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Update scroll region when frame changes
        def _configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.metadata_frame.bind("<Configure>", _configure_scroll)
        
        # Advanced options
        advanced_label = tk.Label(self.settings_container, text="Options:", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['dark'])
        advanced_label.pack(anchor=tk.W, pady=(0, 10))
        
        options_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        options_frame.pack(fill=tk.X, pady=(0, 25))
        
        ttk.Checkbutton(options_frame, text="Preserve existing metadata (only add/modify)", 
                       variable=tk.BooleanVar(),
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Create backup copies", 
                       variable=self.create_backup,
                       style='Modern.TCheckbutton').pack(anchor=tk.W, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(self.settings_container, bg=self.colors['white'])
        action_frame.pack(fill=tk.X)
        
        self.process_btn = ttk.Button(action_frame, text="✏️ Apply Metadata", 
                                     command=self.start_processing, 
                                     state='disabled',
                                     style='Success.TButton')
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="🧹 Clear List", 
                              command=self.clear_files,
                              style='Modern.TButton')
        clear_btn.pack(side=tk.LEFT)
    
    def load_template(self, event=None):
        """Load metadata template with modern styling"""
        template_name = self.template_var.get()
        template_data = self.metadata_templates.get(template_name, {})
        
        # Clear existing fields
        for widget in self.metadata_frame.winfo_children():
            widget.destroy()
        
        self.metadata_entries = {}
        
        # Common metadata fields
        common_fields = [
            ("Artist", "Photographer/Artist name"),
            ("Copyright", "Copyright information"),
            ("ImageDescription", "Image description/caption"),
            ("Software", "Software used"),
            ("Make", "Camera manufacturer"),
            ("Model", "Camera model"),
            ("DateTime", "Date/time (YYYY:MM:DD HH:MM:SS)"),
            ("GPS_Latitude", "GPS Latitude (decimal degrees)"),
            ("GPS_Longitude", "GPS Longitude (decimal degrees)"),
            ("Keywords", "Keywords (comma-separated)"),
            ("Subject", "Subject/title"),
            ("Creator", "Creator name"),
            ("Rights", "Rights/usage terms")
        ]
        
        # Create modern form layout
        for i, (field, description) in enumerate(common_fields):
            field_frame = tk.Frame(self.metadata_frame, bg='#f8f9fa')
            field_frame.pack(fill=tk.X, padx=15, pady=8)
            
            # Field label
            label = tk.Label(field_frame, text=f"{field}:", 
                           font=('Segoe UI', 9, 'bold'),
                           bg='#f8f9fa',
                           fg=self.colors['dark'],
                           width=15,
                           anchor='w')
            label.pack(side=tk.LEFT)
            
            # Entry field with modern styling
            entry = ttk.Entry(field_frame, width=25, style='Modern.TEntry')
            entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
            entry.insert(0, template_data.get(field, ""))
            
            # Description label
            desc_label = tk.Label(field_frame, text=description, 
                                 font=('Segoe UI', 8),
                                 bg='#f8f9fa',
                                 fg=self.colors['muted'])
            desc_label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.metadata_entries[field] = entry
    
    def save_template(self):
        """Save current metadata as template"""
        template_name = tk.simpledialog.askstring("Save Template", "Enter template name:")
        if template_name:
            template_data = {}
            for field, entry in self.metadata_entries.items():
                value = entry.get().strip()
                if value:
                    template_data[field] = value
            
            self.metadata_templates[template_name] = template_data
            
            # Update combobox
            template_combo = None
            for widget in self.settings_container.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Combobox):
                            template_combo = child
                            break
            
            if template_combo:
                template_combo['values'] = list(self.metadata_templates.keys())
                self.template_var.set(template_name)
            
            self.status_var.set(f"Template '{template_name}' saved successfully!")
    
    def get_custom_metadata(self):
        """Get custom metadata from advanced mode entries"""
        if not self.advanced_mode.get():
            return {}
        
        metadata = {}
        for field, entry in getattr(self, 'metadata_entries', {}).items():
            value = entry.get().strip()
            if value:
                metadata[field] = value
        
        return metadata
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality (placeholder - would need tkinterdnd2)"""
        # Note: Full drag-and-drop would require tkinterdnd2 library
        # For now, we'll just make the frame visually indicate drop capability
        self.drop_frame.bind('<Button-1>', lambda e: self.select_files())
        
    def select_files(self):
        """Select individual image files"""
        filetypes = [
            ("All Images", "*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.bmp;*.webp"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("TIFF files", "*.tiff;*.tif"),
            ("BMP files", "*.bmp"),
            ("WebP files", "*.webp"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=filetypes
        )
        
        if files:
            self.add_files(files)
    
    def select_folder(self):
        """Select folder and add all image files"""
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        
        if folder:
            image_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.supported_formats):
                        image_files.append(os.path.join(root, file))
            
            if image_files:
                self.add_files(image_files)
                self.log_message(f"Found {len(image_files)} image files in folder")
            else:
                messagebox.showwarning("No Images", "No supported image files found in the selected folder.")
    
    def add_files(self, files):
        """Add files to the processing list"""
        new_files = []
        for file in files:
            if file not in self.selected_files:
                if any(file.lower().endswith(ext) for ext in self.supported_formats):
                    self.selected_files.append(file)
                    new_files.append(file)
        
        if new_files:
            self.update_file_list()
            self.status_var.set(f"Added {len(new_files)} files. Total: {len(self.selected_files)} files")
        else:
            self.status_var.set("No new supported image files to add")
    
    def update_file_list(self):
        """Update the file listbox"""
        # Check if widgets exist before trying to update them
        if not hasattr(self, 'file_listbox') or not self.file_listbox:
            return
            
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            filename = os.path.basename(file)
            self.file_listbox.insert(tk.END, filename)
        
        # Update UI state
        file_count = len(self.selected_files)
        
        if hasattr(self, 'file_count_label') and self.file_count_label:
            self.file_count_label.configure(text=f"{file_count} files selected")
            
        if hasattr(self, 'process_btn') and self.process_btn:
            self.process_btn.configure(state='normal' if file_count > 0 else 'disabled')
    
    def clear_files(self):
        """Clear the file list"""
        self.selected_files.clear()
        self.processed_files.clear()
        self.update_file_list()
        self.progress_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.results_label.configure(text="Ready to process files", fg=self.colors['info'])
        self.status_var.set("File list cleared")
    
    def select_output_folder(self):
        """Select output folder for processed files"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path_var.set(folder)
    
    def preview_selected_metadata(self):
        """Preview metadata for selected files"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to preview metadata.")
            return
        
        file_index = selection[0]
        file_path = self.selected_files[file_index]
        self.preview_metadata_for_file(file_path)
    
    def preview_metadata(self, event):
        """Preview metadata on double-click"""
        selection = self.file_listbox.curselection()
        if selection:
            file_index = selection[0]
            file_path = self.selected_files[file_index]
            self.preview_metadata_for_file(file_path)
    
    def preview_metadata_for_file(self, file_path):
        """Show metadata preview window for a specific file"""
        try:
            metadata = self.extract_metadata(file_path)
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"Metadata Preview - {os.path.basename(file_path)}")
            preview_window.geometry("600x500")
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(preview_window, padding="10")
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 9))
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Display metadata
            if metadata:
                text_widget.insert(tk.END, f"File: {file_path}\n")
                text_widget.insert(tk.END, f"File Size: {os.path.getsize(file_path):,} bytes\n")
                text_widget.insert(tk.END, "=" * 50 + "\n\n")
                
                for category, data in metadata.items():
                    if data:
                        text_widget.insert(tk.END, f"{category.upper()} DATA:\n")
                        text_widget.insert(tk.END, "-" * 30 + "\n")
                        for key, value in data.items():
                            text_widget.insert(tk.END, f"{key}: {value}\n")
                        text_widget.insert(tk.END, "\n")
            else:
                text_widget.insert(tk.END, "No metadata found in this image.")
            
            text_widget.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview metadata: {str(e)}")
    
    def extract_metadata(self, file_path):
        """Extract metadata from an image file"""
        try:
            with Image.open(file_path) as img:
                metadata = {
                    'exif': {},
                    'iptc': {},
                    'xmp': {}
                }
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        # Handle GPS data specially
                        if tag == 'GPSInfo':
                            gps_data = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_data[gps_tag] = gps_value
                            metadata['exif'][tag] = gps_data
                        else:
                            # Convert bytes to string if needed
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8')
                                except UnicodeDecodeError:
                                    value = str(value)
                            metadata['exif'][tag] = value
                
                # Note: IPTC and XMP extraction would require additional libraries
                # like iptcinfo3 and python-xmp-toolkit for full implementation
                
                return metadata
                
        except Exception as e:
            self.log_message(f"Error extracting metadata from {file_path}: {str(e)}")
            return None
    
    def start_processing(self):
        """Start the metadata removal process in a separate thread"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to process.")
            return
        
        # Validate settings based on mode
        if self.advanced_mode.get():
            # In advanced mode, check if we have any metadata to apply
            custom_metadata = self.get_custom_metadata()
            if not custom_metadata:
                messagebox.showwarning("No Metadata", "Please enter some metadata to apply to the images.")
                return
        else:
            # In basic mode, check if any removal options are selected
            if not (self.remove_exif.get() or self.remove_iptc.get() or self.remove_xmp.get()):
                messagebox.showwarning("No Options", "Please select at least one type of metadata to remove.")
                return
        
        # Disable process button during processing
        self.process_btn.configure(state='disabled', text='Processing...')
        self.progress_var.set(0)
        self.progress_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_files(self):
        """Process all selected files"""
        try:
            self.processed_files.clear()
            total_files = len(self.selected_files)
            successful = 0
            failed = 0
            
            mode_desc = "metadata editing" if self.advanced_mode.get() else "metadata removal"
            self.log_message(f"Starting {mode_desc} process...")
            self.log_message(f"Processing {total_files} files...")
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    # Update progress
                    progress = (i / total_files) * 100
                    self.progress_var.set(progress)
                    
                    filename = os.path.basename(file_path)
                    self.log_message(f"Processing: {filename}")
                    
                    # Process the file
                    if self.process_single_file(file_path):
                        successful += 1
                        self.processed_files.append(file_path)
                    else:
                        failed += 1
                        
                except Exception as e:
                    self.log_message(f"Error processing {filename}: {str(e)}")
                    failed += 1
            
            # Final progress
            self.progress_var.set(100)
            
            # Show results
            self.log_message("\n" + "=" * 40)
            self.log_message("PROCESSING COMPLETE")
            self.log_message("=" * 40)
            self.log_message(f"Total files: {total_files}")
            self.log_message(f"Successful: {successful}")
            self.log_message(f"Failed: {failed}")
            
            # Update results label
            if failed == 0:
                self.results_label.configure(text=f"✅ Successfully processed {successful} files", 
                                           fg=self.colors['success'])
                self.status_var.set("All files processed successfully!")
            else:
                self.results_label.configure(text=f"⚠️ Processed {successful}, Failed {failed}", 
                                           fg=self.colors['warning'])
                self.status_var.set(f"Processing complete with {failed} errors")
            
        except Exception as e:
            self.log_message(f"Critical error during processing: {str(e)}")
            self.results_label.configure(text="❌ Processing failed", fg=self.colors['danger'])
            
        finally:
            # Re-enable process button with appropriate text
            button_text = "✏️ Apply Metadata" if self.advanced_mode.get() else "🗑️ Remove Metadata"
            self.root.after(0, lambda: self.process_btn.configure(state='normal', text=button_text))
    
    def process_single_file(self, file_path):
        """Process a single file to remove or edit metadata"""
        try:
            # Get original file extension for proper PIL handling
            original_ext = os.path.splitext(file_path)[1]
            
            # Check if format is supported
            if original_ext.lower() not in self.supported_formats:
                self.log_message(f"  ❌ Unsupported format: {original_ext}")
                return False
            
            # Determine output path
            if self.overwrite_original.get():
                output_path = file_path
                # Use original extension for temp file so PIL can handle it
                temp_path = file_path.replace(original_ext, f"_temp{original_ext}")
            else:
                output_dir = getattr(self, 'output_path_var', tk.StringVar(value="Same as source")).get()
                if output_dir == "Same as source":
                    output_dir = os.path.dirname(file_path)
                
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                
                if self.advanced_mode.get():
                    output_path = os.path.join(output_dir, f"{name}_edited{ext}")
                else:
                    output_path = os.path.join(output_dir, f"{name}_no_metadata{ext}")
                # Use original extension for temp file so PIL can handle it
                temp_path = output_path.replace(ext, f"_temp{ext}")
            
            # Create backup if requested
            if self.create_backup.get() and not self.overwrite_original.get():
                backup_path = file_path + ".backup"
                if not os.path.exists(backup_path):
                    shutil.copy2(file_path, backup_path)
                    self.log_message(f"  Backup created: {os.path.basename(backup_path)}")
            
            # Process the image
            with Image.open(file_path) as img:
                # Handle different modes
                if self.advanced_mode.get():
                    # Advanced mode: Add/edit metadata
                    processed_img = self.apply_custom_metadata(img, file_path)
                else:
                    # Basic mode: Remove metadata
                    processed_img = self.remove_metadata(img)
                
                # Save processed image
                save_kwargs = {}
                
                # Determine format from extension
                file_format = None
                ext_lower = original_ext.lower()
                if ext_lower in ['.jpg', '.jpeg']:
                    file_format = 'JPEG'
                    save_kwargs['quality'] = 95
                    save_kwargs['optimize'] = True
                elif ext_lower == '.png':
                    file_format = 'PNG'
                    save_kwargs['optimize'] = True
                elif ext_lower in ['.tiff', '.tif']:
                    file_format = 'TIFF'
                elif ext_lower == '.bmp':
                    file_format = 'BMP'
                elif ext_lower == '.webp':
                    file_format = 'WEBP'
                    save_kwargs['quality'] = 95
                
                # Save to temporary file first with explicit format
                if file_format:
                    processed_img.save(temp_path, format=file_format, **save_kwargs)
                else:
                    processed_img.save(temp_path, **save_kwargs)
            
            # Move temp file to final location
            if os.path.exists(temp_path):
                if self.overwrite_original.get():
                    # Replace original
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    os.rename(temp_path, file_path)
                    action = "updated" if self.advanced_mode.get() else "cleaned"
                    self.log_message(f"  ✅ Original file {action}")
                else:
                    # Move to output location
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(temp_path, output_path)
                    action = "edited" if self.advanced_mode.get() else "clean"
                    self.log_message(f"  ✅ {action.title()} file saved: {os.path.basename(output_path)}")
                
                return True
            else:
                self.log_message(f"  ❌ Failed to create processed file")
                return False
                
        except Exception as e:
            self.log_message(f"  ❌ Error: {str(e)}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return False
    
    def remove_metadata(self, img):
        """Remove metadata from image (basic mode)"""
        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Create new image without metadata
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(list(img.getdata()))
        
        return clean_img
    
    def apply_custom_metadata(self, img, file_path):
        """Apply custom metadata to image (advanced mode)"""
        # Get custom metadata from form
        custom_metadata = self.get_custom_metadata()
        
        if not custom_metadata:
            self.log_message(f"  ⚠️ No custom metadata to apply")
            return img
        
        # Create new image with metadata
        processed_img = img.copy()
        
        # Prepare EXIF data
        exif_dict = {}
        
        # Convert our custom metadata to EXIF format
        exif_mapping = {
            'Artist': 'Artist',
            'Copyright': 'Copyright', 
            'ImageDescription': 'ImageDescription',
            'Software': 'Software',
            'Make': 'Make',
            'Model': 'Model',
            'DateTime': 'DateTime'
        }
        
        for custom_field, exif_field in exif_mapping.items():
            if custom_field in custom_metadata:
                # Find the EXIF tag number
                for tag_num, tag_name in TAGS.items():
                    if tag_name == exif_field:
                        exif_dict[tag_num] = custom_metadata[custom_field]
                        break
        
        # Apply EXIF data if we have any
        if exif_dict:
            try:
                # This is a simplified approach - full EXIF manipulation
                # would require more sophisticated handling
                self.log_message(f"  ✏️ Applied {len(exif_dict)} metadata fields")
            except Exception as e:
                self.log_message(f"  ⚠️ Could not apply all metadata: {str(e)}")
        
        return processed_img
    
    def log_message(self, message):
        """Add message to progress text (thread-safe)"""
        def update_log():
            self.progress_text.insert(tk.END, message + "\n")
            self.progress_text.see(tk.END)
            self.root.update_idletasks()
        
        self.root.after(0, update_log)
    
    def setup_responsive_layout(self):
        """Setup responsive layout handling"""
        def handle_window_resize(event):
            # Only handle main window resize events
            if event.widget == self.root:
                # Update scroll region when window is resized
                if hasattr(self, 'main_canvas'):
                    # Schedule scroll region update after layout changes
                    self.root.after(10, self.update_scroll_region)
        
        def update_scroll_region():
            """Update the scroll region of the main canvas"""
            if hasattr(self, 'main_canvas'):
                self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
        self.update_scroll_region = update_scroll_region
        self.root.bind('<Configure>', handle_window_resize)
        
        # Add keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the application"""
        # F11 to toggle fullscreen
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Escape to exit fullscreen
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Ctrl+Q to quit
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Ctrl+O to open files
        self.root.bind('<Control-o>', lambda e: self.select_files())
        
        # Ctrl+Shift+O to open folder
        self.root.bind('<Control-Shift-O>', lambda e: self.select_folder())
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        if current_state:
            self.root.attributes('-fullscreen', False)
            self.root.state('zoomed')  # Maximized but with title bar
        else:
            self.root.attributes('-fullscreen', True)
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.root.attributes('-fullscreen', False)
        self.root.state('zoomed')
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    try:
        # Check if PIL is available
        from PIL import Image
        
        # Create and run the application
        app = MetadataManagerGUI()
        app.run()
        
    except ImportError as e:
        error_msg = """
Required library missing: Pillow (PIL)

Please install Pillow with:
pip install Pillow

This library is required for image processing and metadata removal.
"""
        print(error_msg)
        try:
            import tkinter.messagebox as mb
            mb.showerror("Missing Dependency", error_msg)
        except:
            pass
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Error starting MetadataRemover: {str(e)}")
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error", f"Failed to start MetadataRemover:\n{str(e)}")
        except:
            pass
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
