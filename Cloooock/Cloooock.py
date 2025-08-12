#!/usr/bin/env python3
"""
DesktopClock - High Precision NTP Desktop Clock

Description: A desktop clock application that synchronizes with NTP servers
            and displays time accurate to 0.01 seconds (10ms precision).

Author: Your Name
License: MIT
Version: 1.0.0
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime, timezone
import ntplib
from typing import Optional

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

class ThemeManager:
    def __init__(self):
        self.dark_theme = {
            'bg': '#1e1e1e',
            'fg': '#d4d4d4',
            'accent': '#007acc',
            'time': '#4ec9b0',
            'date': '#569cd6',
            'status': '#9cdcfe',
            'precision': '#ce9178',
            'button_bg': '#2d2d30',
            'button_fg': '#cccccc',
            'button_hover': '#3e3e42',
            'entry_bg': '#3c3c3c',
            'entry_fg': '#d4d4d4',
            'close_bg': '#f14c4c',
            'border': '#404040',
            'menu_bg': '#252526',
            'menu_fg': '#cccccc',
            'mini_bg': '#000000',
            'mini_fg': '#00ff00'
        }
        
        self.light_theme = {
            'bg': '#ffffff',
            'fg': '#2d2d2d',
            'accent': '#0066cc',
            'time': '#0078d4',
            'date': '#323130',
            'status': '#605e5c',
            'precision': '#8a8886',
            'button_bg': '#f3f2f1',
            'button_fg': '#323130',
            'button_hover': '#e1dfdd',
            'entry_bg': '#ffffff',
            'entry_fg': '#323130',
            'close_bg': '#d13438',
            'border': '#d2d0ce',
            'menu_bg': '#f3f2f1',
            'menu_fg': '#323130',
            'mini_bg': '#000000',
            'mini_fg': '#00ff00'
        }
        
        self.current_theme = self.dark_theme
        self.is_dark = True
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark = not self.is_dark
        self.current_theme = self.dark_theme if self.is_dark else self.light_theme
    
    def get_theme(self):
        """Get current theme colors."""
        return self.current_theme

class NTPClock:
    def __init__(self):
        self.ntp_servers = [
            'pool.ntp.org',
            'time.google.com',
            'time.cloudflare.com',
            'time.nist.gov'
        ]
        self.ntp_offset = 0.0
        self.last_sync = None
        self.sync_interval = 300  # 5 minutes
        self.running = False
        self.sync_thread = None
        
    def sync_with_ntp(self) -> bool:
        """Synchronize with NTP server and calculate offset."""
        for server in self.ntp_servers:
            try:
                client = ntplib.NTPClient()
                response = client.request(server, version=3, timeout=2)
                
                # Calculate offset between local time and NTP time
                ntp_time = response.tx_time
                local_time = time.time()
                self.ntp_offset = ntp_time - local_time
                self.last_sync = datetime.now()
                
                print(f"Synced with {server}, offset: {self.ntp_offset:.4f}s")
                return True
                
            except Exception as e:
                print(f"Failed to sync with {server}: {e}")
                continue
                
        return False
    
    def get_ntp_time(self) -> float:
        """Get current NTP-synchronized time."""
        return time.time() + self.ntp_offset
    
    def set_sync_interval(self, interval: int):
        """Set new sync interval and restart sync thread if running."""
        self.sync_interval = max(30, interval)  # Minimum 30 seconds
        print(f"Sync interval changed to {self.sync_interval} seconds")
        
        # Restart sync thread with new interval if it's running
        if self.running:
            self.stop_sync_thread()
            self.start_sync_thread()
    
    def start_sync_thread(self):
        """Start background NTP synchronization thread."""
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
    
    def stop_sync_thread(self):
        """Stop background synchronization."""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
    
    def _sync_loop(self):
        """Background thread for periodic NTP synchronization."""
        # Initial sync
        self.sync_with_ntp()
        
        while self.running:
            time.sleep(self.sync_interval)
            if self.running:
                self.sync_with_ntp()

class ClockGUI:
    def __init__(self):
        self.ntp_clock = NTPClock()
        self.theme_manager = ThemeManager()
        self.root = tk.Tk()
        self.always_on_top = True  # Track pin state
        self.mini_mode = False  # Track mini mode state
        self.opacity = 0.9  # Default opacity (0.1 to 1.0)
        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.setup_window()
        self.create_widgets()
        self.update_clock()
        
    def setup_window(self):
        """Configure the main window."""
        # Remove window decorations (title bar, borders)
        self.root.overrideredirect(True)
        
        # Set window size based on mode
        if self.mini_mode:
            self.root.geometry("180x45")
        else:
            # Initial size - will be adjusted after content is created
            self.root.geometry("450x260")
        
        # Make window stay on top initially
        self.root.attributes('-topmost', self.always_on_top)
        
        # Set window opacity
        self.root.attributes('-alpha', self.opacity)
        
        # Apply theme
        theme = self.theme_manager.get_theme()
        if self.mini_mode:
            self.root.configure(bg=theme['mini_bg'], relief='solid', bd=1)
        else:
            self.root.configure(bg=theme['bg'], relief='solid', bd=1)
        
        # Center window on screen (initial positioning)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if self.mini_mode:
            x = (screen_width // 2) - 90
            y = (screen_height // 2) - 22
            self.root.geometry(f"180x45+{x}+{y}")
        else:
            x = (screen_width // 2) - 225
            y = (screen_height // 2) - 130
            self.root.geometry(f"450x260+{x}+{y}")
        
        # Bind mouse events for dragging
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag_window)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Right-click menu for close option
        self.root.bind('<Button-3>', self.show_context_menu)
        
        # Bind mouse wheel for opacity control (Ctrl + wheel)
        self.root.bind('<Control-MouseWheel>', self.adjust_opacity)
    
    def adjust_window_size(self):
        """Dynamically adjust window size to fit content."""
        if not self.mini_mode:
            # Update the window to calculate required size
            self.root.update_idletasks()
            
            # Get the required size from the main frame
            main_frame = None
            for child in self.root.winfo_children():
                if isinstance(child, tk.Frame):
                    main_frame = child
                    break
            
            if main_frame:
                # Calculate required dimensions
                required_width = main_frame.winfo_reqwidth() + 20  # Add some padding
                required_height = main_frame.winfo_reqheight() + 20
                
                # Set minimum and maximum bounds
                min_width, min_height = 420, 240
                max_width, max_height = 500, 300
                
                # Clamp to reasonable bounds
                final_width = max(min_width, min(max_width, required_width))
                final_height = max(min_height, min(max_height, required_height))
                
                # Get current position
                current_x = self.root.winfo_x()
                current_y = self.root.winfo_y()
                
                # If window is centered, keep it centered with new size
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                # Check if window is approximately centered
                center_x = (screen_width // 2) - 225  # Original center calculation
                center_y = (screen_height // 2) - 130
                
                if abs(current_x - center_x) < 50 and abs(current_y - center_y) < 50:
                    # Re-center with new dimensions
                    new_x = (screen_width // 2) - (final_width // 2)
                    new_y = (screen_height // 2) - (final_height // 2)
                    self.root.geometry(f"{final_width}x{final_height}+{new_x}+{new_y}")
                else:
                    # Keep current position, just change size
                    self.root.geometry(f"{final_width}x{final_height}+{current_x}+{current_y}")
                
                print(f"Window resized to: {final_width}x{final_height}")
    
    def create_widgets(self):
        """Create and layout GUI widgets."""
        theme = self.theme_manager.get_theme()
        
        if self.mini_mode:
            self.create_mini_widgets()
        else:
            self.create_full_widgets()
            # Adjust window size after widgets are created
            self.root.after(10, self.adjust_window_size)
    
    def create_mini_widgets(self):
        """Create mini mode widgets - just time in a small black box."""
        theme = self.theme_manager.get_theme()
        
        # Main frame for mini mode
        main_frame = tk.Frame(self.root, bg=theme['mini_bg'], padx=8, pady=8)
        main_frame.pack(fill='both', expand=True)
        
        # Bind drag events to main frame
        main_frame.bind('<Button-1>', self.start_drag)
        main_frame.bind('<B1-Motion>', self.drag_window)
        main_frame.bind('<ButtonRelease-1>', self.stop_drag)
        main_frame.bind('<Button-3>', self.show_context_menu)
        main_frame.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Time display only
        self.time_var = tk.StringVar()
        time_label = tk.Label(main_frame, textvariable=self.time_var, 
                             font=("Consolas", 16, "bold"),
                             fg=theme['mini_fg'], bg=theme['mini_bg'])
        time_label.pack(expand=True)
        time_label.bind('<Button-1>', self.start_drag)
        time_label.bind('<B1-Motion>', self.drag_window)
        time_label.bind('<ButtonRelease-1>', self.stop_drag)
        time_label.bind('<Button-3>', self.show_context_menu)
        time_label.bind('<Double-Button-1>', lambda e: self.toggle_mini_mode())
        time_label.bind('<Control-MouseWheel>', self.adjust_opacity)
    
    def create_full_widgets(self):
        """Create full mode widgets - complete interface."""
        theme = self.theme_manager.get_theme()
        
        # Main frame with IDE style - adjusted padding
        main_frame = tk.Frame(self.root, bg=theme['bg'], padx=20, pady=18)  # Increased padding
        main_frame.pack(fill='both', expand=True)
        
        # Bind drag events to main frame
        main_frame.bind('<Button-1>', self.start_drag)
        main_frame.bind('<B1-Motion>', self.drag_window)
        main_frame.bind('<ButtonRelease-1>', self.stop_drag)
        main_frame.bind('<Button-3>', self.show_context_menu)
        main_frame.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Header frame with theme indicator
        header_frame = tk.Frame(main_frame, bg=theme['bg'])
        header_frame.pack(fill='x', pady=(0, 12))  # Increased bottom padding
        
        # Theme indicator
        theme_indicator = tk.Label(header_frame, 
                                  text="● Dark Mode" if self.theme_manager.is_dark else "● Light Mode",
                                  font=("Consolas", 8),
                                  fg=theme['accent'], bg=theme['bg'])
        theme_indicator.pack(side='left')
        theme_indicator.bind('<Button-1>', self.start_drag)
        theme_indicator.bind('<B1-Motion>', self.drag_window)
        theme_indicator.bind('<ButtonRelease-1>', self.stop_drag)
        theme_indicator.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Opacity controls frame (right side of header)
        opacity_controls = tk.Frame(header_frame, bg=theme['bg'])
        opacity_controls.pack(side='right')
        
        # Opacity decrease button
        opacity_minus = tk.Button(opacity_controls, text="−",
                                 command=self.decrease_opacity,
                                 font=("Segoe UI", 10, "bold"),
                                 bg=theme['button_bg'], fg=theme['button_fg'],
                                 relief='flat', width=2, height=1,
                                 activebackground=theme['button_hover'])
        opacity_minus.pack(side='left', padx=(0, 2))
        
        # Opacity label
        self.opacity_label = tk.Label(opacity_controls, 
                                     text=f"◐ {int(self.opacity * 100)}%",
                                     font=("Consolas", 8),
                                     fg=theme['precision'], bg=theme['bg'],
                                     width=6)
        self.opacity_label.pack(side='left', padx=2)
        self.opacity_label.bind('<Button-1>', self.start_drag)
        self.opacity_label.bind('<B1-Motion>', self.drag_window)
        self.opacity_label.bind('<ButtonRelease-1>', self.stop_drag)
        self.opacity_label.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Opacity increase button
        opacity_plus = tk.Button(opacity_controls, text="+",
                                command=self.increase_opacity,
                                font=("Segoe UI", 10, "bold"),
                                bg=theme['button_bg'], fg=theme['button_fg'],
                                relief='flat', width=2, height=1,
                                activebackground=theme['button_hover'])
        opacity_plus.pack(side='left', padx=(2, 0))
        
        # Time display with monospace font
        self.time_var = tk.StringVar()
        time_label = tk.Label(main_frame, textvariable=self.time_var, 
                             font=("Consolas", 28, "bold"),
                             fg=theme['time'], bg=theme['bg'])
        time_label.pack(pady=(5, 8))  # Increased bottom padding
        time_label.bind('<Button-1>', self.start_drag)
        time_label.bind('<B1-Motion>', self.drag_window)
        time_label.bind('<ButtonRelease-1>', self.stop_drag)
        time_label.bind('<Button-3>', self.show_context_menu)
        time_label.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Date display
        self.date_var = tk.StringVar()
        date_label = tk.Label(main_frame, textvariable=self.date_var,
                             font=("Segoe UI", 12),
                             fg=theme['date'], bg=theme['bg'])
        date_label.pack(pady=(0, 10))  # Increased bottom padding
        date_label.bind('<Button-1>', self.start_drag)
        date_label.bind('<B1-Motion>', self.drag_window)
        date_label.bind('<ButtonRelease-1>', self.stop_drag)
        date_label.bind('<Button-3>', self.show_context_menu)
        date_label.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Status display with code style
        self.status_var = tk.StringVar(value="// Initializing NTP sync...")
        status_label = tk.Label(main_frame, textvariable=self.status_var,
                               font=("Consolas", 9),
                               fg=theme['status'], bg=theme['bg'])
        status_label.pack(pady=(0, 12))  # Increased bottom padding
        status_label.bind('<Button-1>', self.start_drag)
        status_label.bind('<B1-Motion>', self.drag_window)
        status_label.bind('<ButtonRelease-1>', self.stop_drag)
        status_label.bind('<Button-3>', self.show_context_menu)
        status_label.bind('<Control-MouseWheel>', self.adjust_opacity)
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame, bg=theme['bg'])
        button_frame.pack(pady=(5, 8))  # Increased bottom padding
        
        # IDE-style buttons
        sync_button = tk.Button(button_frame, text="⟳ Sync", 
                               command=self.manual_sync,
                               font=("Segoe UI", 9),
                               bg=theme['button_bg'], fg=theme['button_fg'],
                               relief='flat', padx=12, pady=4,
                               activebackground=theme['button_hover'])
        sync_button.pack(side='left', padx=3)
        
        # Pin/Unpin button
        pin_text = "📌 Pinned" if self.always_on_top else "📌 Pin"
        self.pin_button = tk.Button(button_frame, text=pin_text,
                                   command=self.toggle_always_on_top,
                                   font=("Segoe UI", 9),
                                   bg=theme['button_bg'], fg=theme['button_fg'],
                                   relief='flat', padx=12, pady=4,
                                   activebackground=theme['button_hover'])
        self.pin_button.pack(side='left', padx=3)
        
        # Mini mode toggle button
        mini_button = tk.Button(button_frame, text="📱 Mini",
                               command=self.toggle_mini_mode,
                               font=("Segoe UI", 9),
                               bg=theme['button_bg'], fg=theme['button_fg'],
                               relief='flat', padx=12, pady=4,
                               activebackground=theme['button_hover'])
        mini_button.pack(side='left', padx=3)
        
        # Theme toggle button
        theme_text = "🌙 Dark" if self.theme_manager.is_dark else "☀️ Light"
        theme_button = tk.Button(button_frame, text=theme_text,
                                command=self.toggle_theme,
                                font=("Segoe UI", 9),
                                bg=theme['button_bg'], fg=theme['button_fg'],
                                relief='flat', padx=12, pady=4,
                                activebackground=theme['button_hover'])
        theme_button.pack(side='left', padx=3)
        
        settings_button = tk.Button(button_frame, text="⚙ Settings", 
                                   command=self.show_settings,
                                   font=("Segoe UI", 9),
                                   bg=theme['button_bg'], fg=theme['button_fg'],
                                   relief='flat', padx=12, pady=4,
                                   activebackground=theme['button_hover'])
        settings_button.pack(side='left', padx=3)
        
        # Close button
        close_button = tk.Button(button_frame, text="✕", 
                                command=self.root.quit,
                                font=("Segoe UI", 9),
                                bg=theme['close_bg'], fg='white',
                                relief='flat', padx=12, pady=4,
                                activebackground='#e03e3e')
        close_button.pack(side='right', padx=3)
        
        # Precision indicator with code comment style
        self.precision_var = tk.StringVar()
        precision_label = tk.Label(main_frame, textvariable=self.precision_var,
                                  font=("Consolas", 8),
                                  fg=theme['precision'], bg=theme['bg'])
        precision_label.pack(pady=(8, 0))  # Increased top padding
        precision_label.bind('<Button-1>', self.start_drag)
        precision_label.bind('<B1-Motion>', self.drag_window)
        precision_label.bind('<ButtonRelease-1>', self.stop_drag)
        precision_label.bind('<Button-3>', self.show_context_menu)
        precision_label.bind('<Control-MouseWheel>', self.adjust_opacity)
    
    def apply_theme(self):
        """Apply current theme to all widgets."""
        theme = self.theme_manager.get_theme()
        
        # Update root window
        if self.mini_mode:
            self.root.configure(bg=theme['mini_bg'])
        else:
            self.root.configure(bg=theme['bg'])
        
        # Update all widgets - this will be called after theme toggle
        self.setup_window()
        
        # Recreate widgets with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
    
    def toggle_mini_mode(self):
        """Toggle between mini and full mode."""
        self.mini_mode = not self.mini_mode
        
        # Destroy current widgets and recreate
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Reconfigure window and create new widgets
        self.setup_window()
        self.create_widgets()
        
        print(f"Mini mode: {'ON' if self.mini_mode else 'OFF'}")
    
    def start_drag(self, event):
        """Start dragging the window."""
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y
    
    def drag_window(self, event):
        """Drag the window."""
        if self.dragging:
            x = self.root.winfo_x() + (event.x - self.start_x)
            y = self.root.winfo_y() + (event.y - self.start_y)
            self.root.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Stop dragging the window."""
        self.dragging = False
    
    def show_context_menu(self, event):
        """Show right-click context menu."""
        theme = self.theme_manager.get_theme()
        context_menu = tk.Menu(self.root, tearoff=0, 
                              bg=theme['menu_bg'], fg=theme['menu_fg'],
                              activebackground=theme['button_hover'],
                              activeforeground=theme['fg'])
        
        if not self.mini_mode:
            context_menu.add_command(label="📌 Pin/Unpin", command=self.toggle_always_on_top)
            context_menu.add_command(label="⚙️ Settings", command=self.show_settings)
            context_menu.add_command(label="🎨 Toggle Theme", command=self.toggle_theme)
            context_menu.add_separator()
        
        # Quick opacity presets submenu (removed slider option since it's integrated)
        opacity_submenu = tk.Menu(context_menu, tearoff=0,
                                 bg=theme['menu_bg'], fg=theme['menu_fg'],
                                 activebackground=theme['button_hover'])
        
        opacity_levels = [
            ("100% - Solid", 1.0), ("75% - Light", 0.75), ("50% - Half", 0.5),
            ("25% - Heavy", 0.25), ("10% - Nearly Invisible", 0.1)
        ]
        
        for label, value in opacity_levels:
            current_mark = "● " if abs(self.opacity - value) < 0.05 else "   "
            opacity_submenu.add_command(
                label=f"{current_mark}{label}",
                command=lambda v=value: self.set_opacity(v)
            )
        
        context_menu.add_cascade(label="🔍 Quick Opacity", menu=opacity_submenu)
        
        mini_text = "📱 Full Mode" if self.mini_mode else "📱 Mini Mode"
        context_menu.add_command(label=mini_text, command=self.toggle_mini_mode)
        
        if not self.mini_mode:
            context_menu.add_separator()
        
        context_menu.add_command(label="✕ Exit", command=self.root.quit)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def toggle_always_on_top(self):
        """Toggle the always-on-top state of the window."""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme_manager.toggle_theme()
        self.apply_theme()
    
    # ADD THESE MISSING OPACITY CONTROL METHODS:
    def increase_opacity(self):
        """Increase window opacity by 5%."""
        self.opacity = min(1.0, self.opacity + 0.05)
        self.root.attributes('-alpha', self.opacity)
        self.update_opacity_display()
        print(f"Opacity increased to: {self.opacity:.2f}")
    
    def decrease_opacity(self):
        """Decrease window opacity by 5%."""
        self.opacity = max(0.1, self.opacity - 0.05)
        self.root.attributes('-alpha', self.opacity)
        self.update_opacity_display()
        print(f"Opacity decreased to: {self.opacity:.2f}")
    
    def adjust_opacity(self, event):
        """Adjust window opacity with Ctrl + mouse wheel."""
        # Determine scroll direction
        if event.delta > 0:  # Scroll up - increase opacity
            self.increase_opacity()
        else:  # Scroll down - decrease opacity
            self.decrease_opacity()
    
    def set_opacity(self, value):
        """Set window opacity to specific value."""
        self.opacity = max(0.1, min(1.0, float(value)))
        self.root.attributes('-alpha', self.opacity)
        self.update_opacity_display()
    
    def update_opacity_display(self):
        """Update the opacity display label."""
        if hasattr(self, 'opacity_label'):
            self.opacity_label.config(text=f"◐ {int(self.opacity * 100)}%")
    
    def update_clock(self):
        """Update the clock display every 10ms for 0.01s precision."""
        try:
            ntp_time = self.ntp_clock.get_ntp_time()
            dt = datetime.fromtimestamp(ntp_time)
            
            # Format time with centiseconds (0.01s precision)
            time_str = dt.strftime("%H:%M:%S") + f".{int((ntp_time % 1) * 100):02d}"
            
            self.time_var.set(time_str)
            
            if not self.mini_mode:
                date_str = dt.strftime("%A, %B %d, %Y")
                self.date_var.set(date_str)
                
                # Update status with code comment style
                if self.ntp_clock.last_sync:
                    sync_age = datetime.now() - self.ntp_clock.last_sync
                    sync_minutes = int(sync_age.total_seconds() / 60)
                    status = f"// Last sync: {sync_minutes}m ago | Offset: {self.ntp_clock.ntp_offset:.4f}s"
                else:
                    status = "// Waiting for NTP synchronization..."
                
                self.status_var.set(status)
                
                # Update precision indicator with code style
                pin_status = "pinned" if self.always_on_top else "floating"
                theme_status = "dark" if self.theme_manager.is_dark else "light"
                mode_status = "mini" if self.mini_mode else "full"
                opacity_status = f"{int(self.opacity * 100)}%"
                self.precision_var.set(f"/* Precision: ±0.01s | Mode: {pin_status} | Theme: {theme_status} | View: {mode_status} | Opacity: {opacity_status} */")
                
                # Update pin button text
                pin_text = "📌 Pinned" if self.always_on_top else "📌 Pin"
                if hasattr(self, 'pin_button'):
                    self.pin_button.config(text=pin_text)
                
                # Update opacity display
                self.update_opacity_display()
            
        except Exception as e:
            self.time_var.set("--:--:--.--")
            if not self.mini_mode and hasattr(self, 'status_var'):
                self.status_var.set(f"// Error: {e}")
        
        # Schedule next update (10ms for 0.01s precision)
        self.root.after(10, self.update_clock)
    
    def manual_sync(self):
        """Manually trigger NTP synchronization."""
        def sync_in_background():
            success = self.ntp_clock.sync_with_ntp()
            if not success:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Sync Failed", "Could not synchronize with any NTP server."))
        
        threading.Thread(target=sync_in_background, daemon=True).start()
    
    def show_settings(self):
        """Show settings dialog."""
        theme = self.theme_manager.get_theme()
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cloooock Settings")
        settings_window.configure(bg=theme['bg'])
        settings_window.resizable(False, False)
        
        # Position settings window near the main window
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        
        # Create frame first to calculate size
        frame = tk.Frame(settings_window, bg=theme['bg'], padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(frame, text="⚙ Configuration", 
                              fg=theme['accent'], bg=theme['bg'], 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Opacity section
        opacity_frame = tk.Frame(frame, bg=theme['bg'])
        opacity_frame.pack(fill='x', pady=(0, 15))
        
        opacity_label = tk.Label(opacity_frame, text="Window Opacity:", 
                                fg=theme['fg'], bg=theme['bg'], 
                                font=("Segoe UI", 11, "bold"))
        opacity_label.pack(anchor='w')
        
        opacity_control_frame = tk.Frame(opacity_frame, bg=theme['bg'])
        opacity_control_frame.pack(fill='x', pady=5)
        
        current_opacity_label = tk.Label(opacity_control_frame, text=f"Current: {int(self.opacity * 100)}%", 
                                        fg=theme['status'], bg=theme['bg'],
                                        font=("Consolas", 9))
        current_opacity_label.pack(side='left')
        
        # Opacity slider
        opacity_var = tk.DoubleVar(value=self.opacity)
        opacity_slider = tk.Scale(opacity_control_frame, from_=0.1, to=1.0,
                                 resolution=0.05, orient='horizontal',
                                 variable=opacity_var, length=200,
                                 bg=theme['button_bg'], fg=theme['button_fg'],
                                 activebackground=theme['accent'],
                                 highlightbackground=theme['bg'],
                                 troughcolor=theme['entry_bg'],
                                 command=lambda v: self.set_opacity(float(v)))
        opacity_slider.pack(side='right', padx=(10, 0))
        
        # Control tip
        tip_label = tk.Label(opacity_frame, text="Tip: Use Ctrl+Mouse Wheel to adjust opacity quickly", 
                            fg=theme['precision'], bg=theme['bg'],
                            font=("Segoe UI", 8, "italic"))
        tip_label.pack(anchor='w', pady=(2, 0))
        
        # NTP Servers section
        servers_label = tk.Label(frame, text="NTP Servers:", 
                                fg=theme['fg'], bg=theme['bg'], 
                                font=("Segoe UI", 11, "bold"))
        servers_label.pack(anchor='w')
        
        servers_text = tk.Text(frame, height=5, width=50,
                              bg=theme['entry_bg'], fg=theme['entry_fg'],
                              insertbackground=theme['accent'], 
                              font=("Consolas", 9), relief='solid', bd=1)
        servers_text.pack(pady=(5, 15))
        servers_text.insert(tk.END, '\n'.join(self.ntp_clock.ntp_servers))
        
        # Sync Interval section
        interval_frame = tk.Frame(frame, bg=theme['bg'])
        interval_frame.pack(fill='x', pady=(0, 15))
        
        interval_label = tk.Label(interval_frame, text="Sync Interval:", 
                                 fg=theme['fg'], bg=theme['bg'], 
                                 font=("Segoe UI", 11, "bold"))
        interval_label.pack(anchor='w')
        
        # Current interval display
        current_frame = tk.Frame(interval_frame, bg=theme['bg'])
        current_frame.pack(fill='x', pady=5)
        
        current_label = tk.Label(current_frame, text=f"Current: {self.ntp_clock.sync_interval}s", 
                                fg=theme['status'], bg=theme['bg'],
                                font=("Consolas", 9))
        current_label.pack(side='left')
        
        # Entry for new interval
        entry_frame = tk.Frame(interval_frame, bg=theme['bg'])
        entry_frame.pack(fill='x', pady=5)
        
        entry_label = tk.Label(entry_frame, text="New interval (seconds):", 
                              fg=theme['fg'], bg=theme['bg'],
                              font=("Segoe UI", 9))
        entry_label.pack(side='left')
        
        interval_var = tk.StringVar(value=str(self.ntp_clock.sync_interval))
        interval_entry = tk.Entry(entry_frame, textvariable=interval_var,
                                 bg=theme['entry_bg'], fg=theme['entry_fg'], 
                                 insertbackground=theme['accent'],
                                 width=8, font=("Consolas", 9), relief='solid', bd=1)
        interval_entry.pack(side='left', padx=(10, 10))
        
        def apply_interval():
            try:
                new_interval = int(interval_var.get())
                if new_interval < 30:
                    messagebox.showwarning("Invalid Interval", 
                                         "Sync interval must be at least 30 seconds.")
                    return
                
                self.ntp_clock.set_sync_interval(new_interval)
                messagebox.showinfo("Success", 
                                  f"Sync interval changed to {new_interval} seconds.")
                settings_window.destroy()
                
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                   "Please enter a valid number of seconds.")
        
        apply_button = tk.Button(entry_frame, text="Apply", 
                                command=apply_interval,
                                bg=theme['accent'], fg='white',
                                relief='flat', font=("Segoe UI", 9), 
                                padx=15, pady=2)
        apply_button.pack(side='left')
        
        # Quick interval buttons
        quick_frame = tk.Frame(interval_frame, bg=theme['bg'])
        quick_frame.pack(fill='x', pady=5)
        
        quick_label = tk.Label(quick_frame, text="Quick set:", 
                              fg=theme['status'], bg=theme['bg'],
                              font=("Segoe UI", 9))
        quick_label.pack(side='left')
        
        quick_intervals = [30, 60, 300, 600, 1800]  # 30s, 1m, 5m, 10m, 30m
        quick_labels = ["30s", "1m", "5m", "10m", "30m"]
        
        for interval, label in zip(quick_intervals, quick_labels):
            def make_quick_set(i):
                return lambda: (interval_var.set(str(i)), 
                              self.ntp_clock.set_sync_interval(i))
            
            quick_btn = tk.Button(quick_frame, text=label,
                                 command=make_quick_set(interval),
                                 bg=theme['button_bg'], fg=theme['button_fg'],
                                 relief='flat', width=4, font=("Consolas", 8),
                                 activebackground=theme['button_hover'])
            quick_btn.pack(side='left', padx=2)
        
        # Status section
        status_frame = tk.Frame(frame, bg=theme['bg'])
        status_frame.pack(fill='x', pady=(15, 0))
        
        status_title = tk.Label(status_frame, text="Status:", 
                               fg=theme['fg'], bg=theme['bg'], 
                               font=("Segoe UI", 11, "bold"))
        status_title.pack(anchor='w')
        
        # Theme status
        theme_status = "Dark Mode" if self.theme_manager.is_dark else "Light Mode"
        theme_status_label = tk.Label(status_frame, text=f"Theme: {theme_status}",
                                     fg=theme['status'], bg=theme['bg'],
                                     font=("Consolas", 9))
        theme_status_label.pack(anchor='w')
        
        # View mode status
        view_mode = "Mini Mode" if self.mini_mode else "Full Mode"
        view_mode_label = tk.Label(status_frame, text=f"View Mode: {view_mode}",
                                  fg=theme['status'], bg=theme['bg'],
                                  font=("Consolas", 9))
        view_mode_label.pack(anchor='w')
        
        # Opacity status
        opacity_status_label = tk.Label(status_frame, text=f"Opacity: {int(self.opacity * 100)}%",
                                       fg=theme['status'], bg=theme['bg'],
                                       font=("Consolas", 9))
        opacity_status_label.pack(anchor='w')
        
        # Pin status
        pin_status = "Enabled" if self.always_on_top else "Disabled"
        pin_status_label = tk.Label(status_frame, text=f"Always on Top: {pin_status}",
                                   fg=theme['status'], bg=theme['bg'],
                                   font=("Consolas", 9))
        pin_status_label.pack(anchor='w')
        
        # Last sync info
        if self.ntp_clock.last_sync:
            sync_time = self.ntp_clock.last_sync.strftime("%H:%M:%S")
            sync_label = tk.Label(status_frame, text=f"Last sync: {sync_time}",
                                 fg=theme['status'], bg=theme['bg'],
                                 font=("Consolas", 9))
            sync_label.pack(anchor='w')
        
        # Close button
        close_frame = tk.Frame(frame, bg=theme['bg'])
        close_frame.pack(fill='x', pady=(20, 0))
        
        close_button = tk.Button(close_frame, text="Close", 
                                command=settings_window.destroy,
                                bg=theme['button_bg'], fg=theme['button_fg'],
                                relief='flat', width=12, pady=5,
                                font=("Segoe UI", 10),
                                activebackground=theme['button_hover'])
        close_button.pack()
        
        # Update window to calculate required size
        settings_window.update_idletasks()
        
        # Calculate the required window size based on content
        required_width = frame.winfo_reqwidth() + 40  # Add padding
        required_height = frame.winfo_reqheight() + 60  # Add padding + title bar space
        
        # Set minimum and maximum reasonable sizes
        min_width, min_height = 400, 380
        max_width, max_height = 650, 600
        
        # Clamp to reasonable bounds
        final_width = max(min_width, min(max_width, required_width))
        final_height = max(min_height, min(max_height, required_height))
        
        # Set the calculated geometry
        settings_window.geometry(f"{final_width}x{final_height}+{x}+{y}")
        
        # Make sure the window is properly displayed
        settings_window.transient(self.root)
        settings_window.grab_set()
        settings_window.focus_set()
    
    def run(self):
        """Start the clock application."""
        try:
            # Start NTP synchronization
            self.ntp_clock.start_sync_thread()
            
            # Start GUI
            self.root.mainloop()
            
        finally:
            # Clean up
            self.ntp_clock.stop_sync_thread()

def main():
    """Main application entry point."""
    print("Cloooock v1.0.0")
    print("================")
    print("High Precision NTP Desktop Clock")
    print("IDE-Style Interface with Light/Dark Themes + Mini Mode + Opacity Control")
    print("Precision: ±0.01 seconds")
    print()
    
    try:
        # Check if required modules are available
        import ntplib
        import tkinter
        
        print("Starting desktop clock application...")
        
        clock_app = ClockGUI()
        clock_app.run()
        
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Please install required dependencies:")
        print("pip install ntplib")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)
    
    print("Desktop clock application closed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
