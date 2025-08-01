import requests
import random
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
import threading

# Image categories and sizes for random image fetching
IMAGE_CATEGORIES = [
    "nature", "landscape", "animals", "architecture", "food", "technology",
    "art", "abstract", "space", "ocean", "mountains", "forest", "flowers",
    "city", "travel", "photography", "minimal", "texture", "patterns", "sky"
]

IMAGE_SOURCES = [
    {
        "name": "Picsum (Lorem Picsum)",
        "url": "https://picsum.photos/{width}/{height}",
        "supports_categories": False
    },
    {
        "name": "Placeholder Images",
        "url": "https://via.placeholder.com/{width}x{height}/{color}/ffffff?text={category}",
        "supports_categories": True
    }
]

IMAGE_SIZES = [
    (400, 300), (500, 400), (600, 400), (800, 600), 
    (640, 480), (720, 480), (1024, 768)
]

def get_random_image_info():
    """Generate random image parameters."""
    category = random.choice(IMAGE_CATEGORIES)
    width, height = random.choice(IMAGE_SIZES)
    source = IMAGE_SOURCES[0]  # Always use Picsum as it's most reliable
    
    # Generate a random color for placeholder if needed
    colors = ["FF6B6B", "4ECDC4", "45B7D1", "96CEB4", "FECA57", "FF9FF3", "54A0FF"]
    color = random.choice(colors)
    
    return {
        "category": category,
        "width": width,
        "height": height,
        "source": source,
        "color": color,
        "description": f"Random {category} image ({width}x{height})"
    }

def save_image(img, info):
    """Save the generated image with a descriptive filename."""
    try:
        # Create images directory if it doesn't exist
        os.makedirs("downloaded_images", exist_ok=True)
        
        # Create a safe filename from info
        category = info.get("category", "random")
        width = info.get("width", 0)
        height = info.get("height", 0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"downloaded_images/{timestamp}_{category}_{width}x{height}.jpg"
        
        img.save(filename)
        print(f"💾 Image saved as: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return None

class ImageGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖼️ Random Image Viewer")
        self.root.geometry("800x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_image = None
        self.current_image_info = {"category": "random", "description": "No image loaded"}
        self.is_generating = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🖼️ Random Image Viewer", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Current image info display
        info_frame = ttk.LabelFrame(main_frame, text="Current Image Info", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_var = tk.StringVar(value="Click 'Get Random Image' to start!")
        self.info_label = ttk.Label(info_frame, textvariable=self.info_var, 
                                   font=('Arial', 11), foreground='#333')
        self.info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Control buttons frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        
        # Get random image button
        self.fetch_btn = ttk.Button(controls_frame, text="🖼️ Get Random Image", 
                                   command=self.start_image_generation, 
                                   style='Accent.TButton')
        self.fetch_btn.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # Category selection button
        self.category_btn = ttk.Button(controls_frame, text="🎲 Change Category", 
                                      command=self.change_category)
        self.category_btn.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to fetch images!")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                     font=('Arial', 10), foreground='#666')
        self.status_label.grid(row=4, column=0, pady=(0, 20))
        
        # Image display frame
        image_frame = ttk.LabelFrame(main_frame, text="Random Image", padding="10")
        image_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Image canvas with scrollbars
        canvas_frame = ttk.Frame(image_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', relief='sunken', borderwidth=2)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Image action buttons
        image_actions_frame = ttk.Frame(main_frame)
        image_actions_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        image_actions_frame.columnconfigure(0, weight=1)
        image_actions_frame.columnconfigure(1, weight=1)
        image_actions_frame.columnconfigure(2, weight=1)
        
        self.save_btn = ttk.Button(image_actions_frame, text="💾 Save Image", 
                                  command=self.save_image_dialog, state='disabled')
        self.save_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.copy_btn = ttk.Button(image_actions_frame, text="📋 Copy Info", 
                                  command=self.copy_info, state='disabled')
        self.copy_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.open_folder_btn = ttk.Button(image_actions_frame, text="📁 Open Folder", 
                                         command=self.open_images_folder)
        self.open_folder_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Set initial category
        self.current_category = random.choice(IMAGE_CATEGORIES)
        self.update_info_display()
        
    def update_info_display(self):
        """Update the image info display."""
        info_text = f"Category: {self.current_category.title()} | {self.current_image_info['description']}"
        self.info_var.set(info_text)
        
    def change_category(self):
        """Change the current image category."""
        self.current_category = random.choice(IMAGE_CATEGORIES)
        self.update_info_display()
        self.status_var.set(f"🎯 Category changed to: {self.current_category.title()}")
        
    def start_image_generation(self):
        """Start image fetching in a separate thread."""
        if self.is_generating:
            return
            
        # Start generation in background thread
        thread = threading.Thread(target=self.generate_image_thread)
        thread.daemon = True
        thread.start()
        
    def generate_image_thread(self):
        """Generate image in background thread."""
        self.is_generating = True
        
        # Update UI on main thread
        self.root.after(0, self.start_generation_ui)
        
        try:
            success = self.generate_image()
            self.root.after(0, lambda: self.finish_generation_ui(success))
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(str(e)))
            
    def start_generation_ui(self):
        """Update UI when starting generation."""
        self.fetch_btn.configure(state='disabled', text='🔄 Fetching...')
        self.category_btn.configure(state='disabled')
        self.progress.start(10)
        self.status_var.set("Fetching random image...")
        
    def finish_generation_ui(self, success):
        """Update UI when finishing generation."""
        self.fetch_btn.configure(state='normal', text='🖼️ Get Random Image')
        self.category_btn.configure(state='normal')
        self.progress.stop()
        self.is_generating = False
        
        if success:
            self.status_var.set("✅ Image fetched successfully!")
            self.save_btn.configure(state='normal')
            self.copy_btn.configure(state='normal')
            self.update_info_display()
        else:
            self.status_var.set("❌ Failed to fetch image. Please try again.")
            
    def handle_error(self, error_msg):
        """Handle errors during generation."""
        self.finish_generation_ui(False)
        self.status_var.set(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", f"Failed to fetch image:\n{error_msg}")
        
    def generate_image(self):
        """Fetch and display a random image from the internet."""
        print("🔄 Starting image generation...")
        self.root.after(0, lambda: self.status_var.set("🔄 Fetching random image..."))
        
        # Get image info with current category preference
        image_info = get_random_image_info()
        image_info["category"] = self.current_category  # Use the selected category
        
        print(f"📝 Image info: {image_info}")
        
        try:
            # Always use Picsum first as it's the most reliable
            url = f"https://picsum.photos/{image_info['width']}/{image_info['height']}"
            print(f"🔗 Fetching from URL: {url}")
            
            self.root.after(0, lambda: self.status_var.set(f"📥 Downloading {image_info['category']} image..."))
            
            # Download image with headers to appear as a regular browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print("📥 Making request...")
            response = requests.get(url, timeout=30, headers=headers, allow_redirects=True)
            print(f"📊 Response status: {response.status_code}")
            print(f"📊 Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                raise Exception(f"Failed to download image: HTTP {response.status_code}")
            
            if len(response.content) == 0:
                raise Exception("Received empty response")
            
            print(f"📊 Response content length: {len(response.content)} bytes")
            
            # Create image from response
            try:
                img = Image.open(BytesIO(response.content))
                print(f"🖼️ Image loaded: {img.size}, mode: {img.mode}")
            except Exception as e:
                print(f"❌ Failed to create image from response: {e}")
                raise Exception(f"Invalid image data received: {e}")
            
            # Convert to RGB if necessary (for saving as JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                print(f"🔄 Converting from {img.mode} to RGB")
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-save the image
            print("💾 Saving image...")
            save_result = save_image(img, image_info)
            print(f"💾 Save result: {save_result}")
            
            # Update the current image info for display
            self.current_image_info = image_info
            
            # Display in GUI
            print("🖼️ Displaying image in GUI...")
            self.root.after(0, lambda: self.display_image(img))
            
            print("✅ Image generation completed successfully!")
            return True
            
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
            return self._try_fallback_sources(image_info)
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error")
            return self._try_fallback_sources(image_info)
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error: {e}")
            return self._try_fallback_sources(image_info)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise Exception(f"Error processing image: {e}")
    
    def _try_fallback_sources(self, image_info):
        """Try alternative image sources as fallback."""
        print("🔄 Trying fallback sources...")
        
        fallback_urls = [
            f"https://picsum.photos/{image_info['width']}/{image_info['height']}?random={random.randint(1, 1000)}",
            f"https://via.placeholder.com/{image_info['width']}x{image_info['height']}/4ECDC4/ffffff?text={image_info['category'].replace(' ', '+')}",
            f"https://dummyimage.com/{image_info['width']}x{image_info['height']}/cccccc/969696.png&text={image_info['category'].replace(' ', '+')}"
        ]
        
        for i, fallback_url in enumerate(fallback_urls):
            try:
                print(f"🔄 Trying fallback {i+1}: {fallback_url}")
                response = requests.get(fallback_url, timeout=15, allow_redirects=True)
                
                if response.status_code == 200 and len(response.content) > 0:
                    img = Image.open(BytesIO(response.content))
                    
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    save_image(img, {"category": "fallback", "width": image_info["width"], "height": image_info["height"]})
                    self.current_image_info = {"category": "fallback", "description": f"Fallback image ({image_info['width']}x{image_info['height']})"}
                    self.root.after(0, lambda: self.display_image(img))
                    print(f"✅ Fallback {i+1} successful!")
                    return True
                    
            except Exception as e:
                print(f"❌ Fallback {i+1} failed: {e}")
                continue
        
        print("❌ All fallback sources failed")
        return False
            
    def display_image(self, img):
        """Display image in the canvas."""
        # Resize image if too large
        max_size = 600
        img_width, img_height = img.size
        
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size / img_width, max_size / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, img.size[0], img.size[1]))
        self.canvas.create_image(img.size[0]//2, img.size[1]//2, image=photo)
        
        # Keep a reference to prevent garbage collection
        self.canvas.image = photo
        self.current_image = img
        
    def save_image_dialog(self):
        """Open save dialog for the current image."""
        if not self.current_image:
            return
            
        # Create safe filename from image info
        category = self.current_image_info.get("category", "random")
        width = self.current_image_info.get("width", 0)
        height = self.current_image_info.get("height", 0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{timestamp}_{category}_{width}x{height}.jpg"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            initialfilename=default_filename,
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.current_image.save(filename)
                self.status_var.set(f"💾 Image saved as: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Image saved successfully!\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{e}")
                
    def copy_info(self):
        """Copy current image info to clipboard."""
        info_text = f"Category: {self.current_image_info.get('category', 'random')}\nDescription: {self.current_image_info.get('description', 'No description')}"
        self.root.clipboard_clear()
        self.root.clipboard_append(info_text)
        self.status_var.set("📋 Image info copied to clipboard!")
            
    def open_images_folder(self):
        """Open the downloaded images folder."""
        folder_path = os.path.abspath("downloaded_images")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Open folder in file explorer (Windows)
        try:
            os.startfile(folder_path)
        except:
            messagebox.showinfo("Folder Location", f"Images folder: {folder_path}")
            
    def run(self):
        """Run the GUI application."""
        # Configure ttk styles
        style = ttk.Style()
        if 'Accent.TButton' not in style.theme_names():
            style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
            
        self.root.mainloop()

def main():
    """Main function to run the GUI image generator."""
    app = ImageGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main()