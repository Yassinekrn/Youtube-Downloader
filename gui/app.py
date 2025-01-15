import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from downloader.video_downloader import VideoDownloader
from downloader.download_manager import DownloadManager
from utils.logger import logger
from datetime import datetime

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x500")
        
        # Initialize download manager
        self.download_manager = DownloadManager()
        
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

        # Download Controls Frame
        self.controls_frame = ttk.Frame(self.main_container)
        self.controls_frame.pack(fill=X, pady=5)
        
        # Download Button and Cancel Button
        self.download_button = ttk.Button(
            self.controls_frame,
            text="Download",
            command=self.download_video,
            style="primary.TButton",
            width=20
        )
        self.download_button.pack(side=LEFT, padx=5)
        
        self.cancel_button = ttk.Button(
            self.controls_frame,
            text="Cancel",
            command=self.cancel_download,
            state="disabled",
            width=20
        )
        self.cancel_button.pack(side=LEFT, padx=5)

        # Progress Frame
        self.progress_frame = ttk.Frame(self.main_container)
        self.progress_frame.pack(fill=X, pady=5)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=X, padx=5, pady=5)
        
        # Progress Labels
        self.status_frame = ttk.Frame(self.progress_frame)
        self.status_frame.pack(fill=X, padx=5)
        
        self.progress_label = ttk.Label(self.status_frame, text="")
        self.progress_label.pack(side=LEFT)
        
        self.speed_label = ttk.Label(self.status_frame, text="")
        self.speed_label.pack(side=RIGHT)

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

        # Set up periodic progress check
        self.root.after(100, self.check_progress)

    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, directory)
            self.log_message(f"Save location set to: {directory}")

    def toggle_theme(self):
        self.current_theme = "litera" if self.current_theme == "darkly" else "darkly"
        self.style.theme_use(self.current_theme)
        logger.info(f"Theme toggled to {self.current_theme}")

    def format_size(self, bytes: float) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"

    def format_speed(self, bytes_per_sec: float) -> str:
        """Format bytes/sec to human readable speed"""
        return f"{self.format_size(bytes_per_sec)}/s"

    def format_time(self, seconds: int) -> str:
        """Format seconds to human readable time"""
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        seconds = seconds % 60
        if minutes < 60:
            return f"{minutes}m {seconds}s"
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}h {minutes}m {seconds}s"

    def update_progress_display(self, progress_info: dict):
        """Update the progress display with download information"""
        if progress_info['status'] == 'downloading':
            # Update progress bar
            self.progress_var.set(progress_info['percentage'])
            
            # Update status labels
            downloaded = self.format_size(progress_info['downloaded_bytes'])
            total = self.format_size(progress_info['total_bytes'])
            speed = self.format_speed(progress_info['speed'])
            eta = self.format_time(progress_info['eta'])
            
            self.progress_label.config(
                text=f"Downloaded: {downloaded} / {total} ({progress_info['percentage']:.1f}%)"
            )
            self.speed_label.config(text=f"Speed: {speed} • ETA: {eta}")

    def handle_download_complete(self, result: dict):
        """Handle download completion"""
        self.progress_var.set(100)
        self.progress_label.config(text="Download Complete!")
        self.speed_label.config(text="")
        self.download_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.log_message("Download completed successfully!", "SUCCESS")
        self.log_message(f"File saved to: {result['filepath']}", "SUCCESS")

    def handle_download_error(self, error: str):
        """Handle download error"""
        self.progress_var.set(0)
        self.progress_label.config(text="")
        self.speed_label.config(text="")
        self.download_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.log_message(f"Error during download: {error}", "ERROR")

    def check_progress(self):
        """Check for progress updates from the download manager"""
        self.download_manager.process_progress_updates(
            self.update_progress_display,
            self.handle_download_complete,
            self.handle_download_error
        )
        self.root.after(100, self.check_progress)

    def log_message(self, message, level="INFO"):
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_prefix = f"{timestamp} [{level}] "
        self.log_text.insert("end", log_prefix, level)
        self.log_text.insert("end", f"{message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def download_video(self):
        url = self.url_entry.get().strip()
        output_dir = self.output_entry.get().strip()
        
        if not url or not output_dir:
            self.log_message("Please fill in both the YouTube URL and Save Location.", "ERROR")
            return
        
        self.log_message("Starting download...")
        self.download_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.progress_var.set(0)
        
        try:
            downloader = VideoDownloader(output_dir)
            self.download_manager.start_download(
                downloader,
                url,
                self.update_progress_display,
                self.handle_download_complete
            )
        except Exception as e:
            self.handle_download_error(str(e))

    def cancel_download(self):
        """Cancel the current download"""
        self.download_manager.stop_all_downloads()
        self.download_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="Download Cancelled")
        self.speed_label.config(text="")
        self.log_message("Download cancelled by user", "INFO")

# Initialize the app
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = VideoDownloaderApp(root)
    root.mainloop()