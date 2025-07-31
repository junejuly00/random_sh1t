from pynput import keyboard
import time
from collections import Counter
import threading
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pystray
from PIL import Image, ImageDraw
import sys
import os

class KeyStalkerGUI:
    def __init__(self):
        self.key_counter = Counter()
        self.running = False
        self.listener = None
        self.listener_thread = None
        self.stats_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("KeyStalker - Keyboard Monitor")
        self.root.geometry("600x500")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        
        # System tray icon
        self.tray_icon = None
        
        self.setup_ui()
        self.create_tray_icon()
        
        # Message data (same as original)
        self.funny_idle_msgs = [
            "KeyStalker: 🦗 ...silence... are you still there?",
            "KeyStalker: Did you die or just stop typing?",
            "KeyStalker: Zero keys. Peak productivity.",
            "KeyStalker: Wow. Keyboard vacation mode, huh?"
        ]

        self.funny_activity_msgs = [
            "🔥 You're on fire! Keep smashing those keys.",
            "⌨️ That poor keyboard is crying for help.",
            "🚀 Typing speed = light speed detected.",
            "🕵 KeyStalker sees everything. Even THAT typo."
        ]

        self.roast_msgs = {
            "backspace": [
                "💀 Backspace again?! What are you even typing?",
                "📉 Backspace count rising. Typos > Words?",
                "🤦 Maybe slow down. Or buy Grammarly."
            ],
            "space": [
                "🚀 Spacebar spam unlocked. Are you moonwalking?",
                "🌌 Infinite space achieved.",
                "✨ Spacebar addiction is real."
            ],
            "enter": [
                "⏎ Enter abuse detected. Emails won't send faster!",
                "📨 Enter again? Calm down champ.",
                "💥 Enter key is begging for mercy."
            ],
            "esc": [
                "🚪 Escape key again? You can't leave this simulation.",
                "👀 Escaping reality, huh?",
                "🕳 ESC pressed. Is life okay?"
            ]
        }
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="KeyStalker - Keyboard Monitor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", 
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", 
                                     command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.heatmap_button = ttk.Button(button_frame, text="Show Heatmap", 
                                        command=self.plot_heatmap)
        self.heatmap_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Data", 
                                      command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", 
                                     font=("Arial", 10))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Live Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                        pady=(0, 10))
        
        # Top keys display
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=60)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Activity log
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Hide to tray instruction
        instruction_label = ttk.Label(main_frame, 
                                     text="Close window to minimize to system tray", 
                                     font=("Arial", 9), foreground="gray")
        instruction_label.grid(row=5, column=0, columnspan=3, pady=(10, 0))
    
    def create_tray_icon(self):
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.text((20, 25), "KS", fill='black')
        
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Start Monitoring", self.start_monitoring),
            pystray.MenuItem("Stop Monitoring", self.stop_monitoring),
            pystray.MenuItem("Show Heatmap", self.plot_heatmap),
            pystray.MenuItem("Exit", self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("KeyStalker", image, "KeyStalker", menu)
    
    def hide_to_tray(self):
        self.root.withdraw()
        if not self.tray_icon.visible:
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def start_monitoring(self, icon=None, item=None):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Monitoring...")
            
            # Start keyboard listener
            self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
            self.listener_thread.start()
            
            # Start stats updater
            self.stats_thread = threading.Thread(target=self.update_stats_loop, daemon=True)
            self.stats_thread.start()
            
            self.log_message("[KeyStalker] Monitoring started!")
    
    def stop_monitoring(self, icon=None, item=None):
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Stopped")
            
            if self.listener:
                self.listener.stop()
            
            self.log_message("[KeyStalker] Monitoring stopped!")
    
    def clear_data(self):
        self.key_counter.clear()
        self.stats_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.log_message("[KeyStalker] Data cleared!")
    
    def on_press(self, key):
        if self.running:
            self.key_counter[key] += 1
    
    def start_listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener
            listener.join()
    
    def update_stats_loop(self):
        last_funny_time = time.time()
        
        while self.running:
            # Update stats display every 5 seconds
            time.sleep(5)
            if self.running:
                self.root.after(0, self.update_stats_display)
            
            # Show funny stats every 20 seconds
            if time.time() - last_funny_time >= 20:
                if self.running:
                    self.root.after(0, self.display_funny_stats)
                last_funny_time = time.time()
    
    def update_stats_display(self):
        if not self.key_counter:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No keys pressed yet...")
            return
        
        # Get top 10 keys
        top = self.key_counter.most_common(10)
        total_presses = sum(self.key_counter.values())
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"📊 Total Key Presses: {total_presses}\n\n")
        self.stats_text.insert(tk.END, "🔥 Top Keys:\n")
        
        for i, (key, count) in enumerate(top, 1):
            keyname = str(key).replace("'", "")
            percentage = (count / total_presses) * 100
            self.stats_text.insert(tk.END, f"{i:2d}. {keyname:<15} {count:>5} presses ({percentage:.1f}%)\n")
    
    def display_funny_stats(self):
        if not self.key_counter:
            message = random.choice(self.funny_idle_msgs)
            self.log_message(message)
            return
        
        # Show activity message
        activity_msg = random.choice(self.funny_activity_msgs)
        self.log_message(activity_msg)
        
        # Check for roasts
        if self.key_counter[keyboard.Key.backspace] > 5:
            self.log_message(random.choice(self.roast_msgs["backspace"]))
        if self.key_counter[keyboard.Key.space] > 15:
            self.log_message(random.choice(self.roast_msgs["space"]))
        if self.key_counter[keyboard.Key.enter] > 10:
            self.log_message(random.choice(self.roast_msgs["enter"]))
        if self.key_counter[keyboard.Key.esc] > 5:
            self.log_message(random.choice(self.roast_msgs["esc"]))
    
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def plot_heatmap(self, icon=None, item=None):
        if not self.key_counter:
            if self.root.winfo_viewable():
                messagebox.showinfo("No Data", "No keyboard data to display!")
            return
        
        try:
            # Define keyboard layout (QWERTY)
            keyboard_layout = [
                ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BackSpace'],
                ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
                ['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
                ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
                ['Ctrl', 'Alt', 'Space', 'Alt', 'Ctrl']
            ]
            
            # Key mappings from pynput to display names
            key_mappings = {
                'Key.backspace': 'BackSpace',
                'Key.tab': 'Tab',
                'Key.caps_lock': 'CapsLock',
                'Key.enter': 'Enter',
                'Key.shift': 'Shift',
                'Key.shift_l': 'Shift',
                'Key.shift_r': 'Shift',
                'Key.ctrl': 'Ctrl',
                'Key.ctrl_l': 'Ctrl',
                'Key.ctrl_r': 'Ctrl',
                'Key.alt': 'Alt',
                'Key.alt_l': 'Alt',
                'Key.alt_r': 'Alt',
                'Key.space': 'Space',
                'Key.esc': 'Esc'
            }
            
            # Get key counts and normalize
            key_counts = {}
            total_presses = sum(self.key_counter.values())
            
            for key, count in self.key_counter.items():
                key_str = str(key).replace("'", "")
                
                # Map special keys
                if key_str in key_mappings:
                    key_str = key_mappings[key_str]
                
                # Normalize count for color intensity
                normalized_count = count / total_presses if total_presses > 0 else 0
                key_counts[key_str.lower()] = {
                    'count': count,
                    'normalized': normalized_count
                }
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(18, 10))
            ax.set_xlim(0, 18)
            ax.set_ylim(0, 7)
            ax.set_aspect('equal')
            
            # Colors for heat levels (cold to hot)
            def get_color(normalized_count):
                if normalized_count == 0:
                    return '#E8E8E8'  # Light gray for unused keys
                elif normalized_count < 0.01:
                    return '#B3E5FC'  # Light blue
                elif normalized_count < 0.03:
                    return '#4FC3F7'  # Blue
                elif normalized_count < 0.05:
                    return '#29B6F6'  # Medium blue
                elif normalized_count < 0.08:
                    return '#FFD54F'  # Yellow
                elif normalized_count < 0.12:
                    return '#FFB74D'  # Orange
                elif normalized_count < 0.15:
                    return '#FF8A65'  # Light red
                else:
                    return '#F44336'  # Hot red
            
            # Draw keyboard keys with better spacing
            row_offsets = [0, 0.6, 0.9, 1.3, 3.0]  # Visual offset for each row
            key_width = 0.85
            key_height = 0.75
            key_spacing = 0.05  # Gap between keys
            
            for row_idx, row in enumerate(keyboard_layout):
                y_pos = 6 - row_idx  # Start from top
                x_offset = row_offsets[row_idx]
                current_x = x_offset
                
                for col_idx, key in enumerate(row):
                    # Adjust width for special keys
                    width = key_width
                    if key == 'BackSpace':
                        width = 2.0
                    elif key == 'Tab':
                        width = 1.5
                    elif key == 'CapsLock':
                        width = 1.8
                    elif key == 'Enter':
                        width = 2.2
                    elif key == 'Shift':
                        width = 2.0 if col_idx == 0 else 1.8
                    elif key == 'Space':
                        width = 7.0
                        current_x = 5.0  # Center the spacebar
                    elif key in ['Ctrl', 'Alt']:
                        width = 1.5
                    
                    # Get key count
                    key_data = key_counts.get(key.lower(), {'count': 0, 'normalized': 0})
                    color = get_color(key_data['normalized'])
                    
                    # Draw key rectangle
                    rect = patches.Rectangle((current_x, y_pos), width, key_height, 
                                           linewidth=1.5, edgecolor='#333333', 
                                           facecolor=color, alpha=0.9)
                    ax.add_patch(rect)
                    
                    # Add key label
                    label = key
                    if len(label) > 8:  # Shorten long key names
                        if key == 'BackSpace':
                            label = 'Backsp'
                        elif key == 'CapsLock':
                            label = 'Caps'
                        else:
                            label = label[:8]
                    
                    # Add text with key name and count
                    text_y = y_pos + key_height/2
                    ax.text(current_x + width/2, text_y + 0.12, label, 
                           ha='center', va='center', fontsize=9, fontweight='bold',
                           color='black')
                    
                    # Add count if key was pressed
                    if key_data['count'] > 0:
                        ax.text(current_x + width/2, text_y - 0.15, str(key_data['count']), 
                               ha='center', va='center', fontsize=8, color='darkred',
                               fontweight='bold')
                    
                    # Move to next key position
                    if key != 'Space':  # Don't add spacing after spacebar
                        current_x += width + key_spacing
            
            # Create color legend
            legend_colors = [
                ('#E8E8E8', '0 presses'),
                ('#B3E5FC', 'Very Low'),
                ('#4FC3F7', 'Low'),
                ('#29B6F6', 'Medium-Low'),
                ('#FFD54F', 'Medium'),
                ('#FFB74D', 'Medium-High'),
                ('#FF8A65', 'High'),
                ('#F44336', 'Very High')
            ]
            
            # Add legend - moved to right side with more space
            legend_x = 15.0
            legend_title_y = 5.5
            ax.text(legend_x, legend_title_y, 'Heat Scale:', 
                   va='center', fontsize=10, fontweight='bold')
            
            for i, (color, label) in enumerate(legend_colors):
                legend_y = 5.0 - i * 0.45
                rect = patches.Rectangle((legend_x, legend_y), 0.4, 0.35, 
                                       facecolor=color, edgecolor='#333333', 
                                       alpha=0.9, linewidth=1)
                ax.add_patch(rect)
                ax.text(legend_x + 0.5, legend_y + 0.175, label, 
                       va='center', fontsize=9)
            
            # Add title and statistics - repositioned to avoid overlap
            ax.text(9, 6.7, 'KeyStalker Keyboard Heatmap', 
                   ha='center', va='center', fontsize=18, fontweight='bold')
            ax.text(9, 6.35, f'Total Key Presses: {total_presses:,}', 
                   ha='center', va='center', fontsize=13)
            
            # Add most pressed key info
            if self.key_counter:
                top_key = self.key_counter.most_common(1)[0]
                top_key_name = str(top_key[0]).replace("'", "")
                if top_key_name in key_mappings:
                    top_key_name = key_mappings[top_key_name]
                ax.text(9, 6.0, f'Most Pressed: {top_key_name} ({top_key[1]} times)', 
                       ha='center', va='center', fontsize=11, style='italic')
            
            # Remove axes
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            if self.root.winfo_viewable():
                messagebox.showerror("Error", f"Could not generate heatmap: {str(e)}")
    
    def quit_application(self, icon=None, item=None):
        self.running = False
        if self.listener:
            self.listener.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = KeyStalkerGUI()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Silent error handling for GUI mode
        sys.exit(1)
