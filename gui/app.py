import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from downloader.video_downloader import VideoDownloader
from utils.logger import logger
from datetime import datetime  # Add this import

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x500")
        
        # Initialize ttkbootstrap style
        self.style = tb.Style("darkly")
        self.current_theme = "darkly"
        
        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Create header frame for theme toggle
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=X, pady=(0, 10))
        
        # Add spacer to push theme toggle to right
        ttk.Label(self.header_frame, text="").pack(side=LEFT, expand=True)
        
        # Theme Toggle Button in top right
        self.theme_toggle_btn = ttk.Button(
            self.header_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            width=15
        )
        self.theme_toggle_btn.pack(side=RIGHT)

        # Create input frame
        self.input_frame = ttk.LabelFrame(self.main_container, text="Download Settings")
        self.input_frame.pack(fill=X, padx=5, pady=5)
        
        # Video URL Input
        self.url_frame = ttk.Frame(self.input_frame)
        self.url_frame.pack(fill=X, padx=5, pady=5)
        self.url_label = ttk.Label(self.url_frame, text="YouTube URL:")
        self.url_label.pack(side=LEFT, padx=(0, 5))
        self.url_entry = ttk.Entry(self.url_frame)
        self.url_entry.pack(side=LEFT, fill=X, expand=True)

        # Output Directory Input with Browse Button
        self.output_frame = ttk.Frame(self.input_frame)
        self.output_frame.pack(fill=X, padx=5, pady=5)
        self.output_label = ttk.Label(self.output_frame, text="Save Location:")
        self.output_label.pack(side=LEFT, padx=(0, 5))
        self.output_entry = ttk.Entry(self.output_frame)
        self.output_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.browse_btn = ttk.Button(
            self.output_frame,
            text="Browse",
            command=self.browse_directory,
            width=10
        )
        self.browse_btn.pack(side=LEFT)

        # Download Button
        self.download_frame = ttk.Frame(self.main_container)
        self.download_frame.pack(fill=X, pady=10)
        self.download_button = ttk.Button(
            self.download_frame,
            text="Download",
            command=self.download_video,
            style="primary.TButton",
            width=20
        )
        self.download_button.pack(anchor=CENTER)

        # Logging Area
        self.log_frame = ttk.LabelFrame(self.main_container, text="Logs")
        self.log_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to log area
        self.scrollbar = ttk.Scrollbar(self.log_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.log_text = tk.Text(
            self.log_frame,
            wrap="word",
            height=15,
            state="disabled",
            yscrollcommand=self.scrollbar.set
        )
        self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.scrollbar.config(command=self.log_text.yview)

        # Configure text tags for different log levels
        self.log_text.tag_configure("INFO", foreground="#007bff")    # Blue
        self.log_text.tag_configure("SUCCESS", foreground="#28a745") # Green
        self.log_text.tag_configure("ERROR", foreground="#dc3545")   # Red

    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, directory)
            self.log_message(f"Save location set to: {directory}")

    def toggle_theme(self):
        # Toggle between dark and light themes
        self.current_theme = "litera" if self.current_theme == "darkly" else "darkly"
        self.style.theme_use(self.current_theme)
        logger.info(f"Theme toggled to {self.current_theme}")

    def log_message(self, message, level="INFO"):
        # Insert log messages into the text widget with appropriate color
        self.log_text.configure(state="normal")
        
        # Insert timestamp and level with color
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_prefix = f"{timestamp} [{level}] "
        self.log_text.insert("end", log_prefix, level)
        
        # Insert the actual message and newline
        self.log_text.insert("end", f"{message}\n")
        
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def download_video(self):
        # Fetch inputs
        url = self.url_entry.get().strip()
        output_dir = self.output_entry.get().strip()
        
        if not url or not output_dir:
            self.log_message("Please fill in both the YouTube URL and Save Location.", "ERROR")
            return
        
        # Log the start
        self.log_message("Starting download...")
        try:
            downloader = VideoDownloader(output_dir)
            downloader.download_video(url)
            self.log_message("Download completed successfully!", "SUCCESS")
        except Exception as e:
            self.log_message(f"Error during download: {str(e)}", "ERROR")

# Initialize the app
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = VideoDownloaderApp(root)
    root.mainloop()