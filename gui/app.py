import tkinter as tk
from tkinter import filedialog, messagebox
from downloader.video_downloader import VideoDownloader


class DownloaderApp:
    """
    GUI for the YouTube Downloader application.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.output_dir = None

        # URL Input
        self.url_label = tk.Label(root, text="YouTube URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Output Directory Selection
        self.dir_button = tk.Button(
            root, text="Select Save Location", command=self.select_output_directory
        )
        self.dir_button.pack(pady=5)

        # Download Button
        self.download_button = tk.Button(
            root, text="Download Video", command=self.download_video
        )
        self.download_button.pack(pady=10)

    def select_output_directory(self):
        """
        Opens a dialog for selecting the save directory.
        """
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            messagebox.showinfo("Directory Selected", f"Files will be saved to: {self.output_dir}")

    def download_video(self):
        """
        Downloads a video based on the URL entered.
        """
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if not self.output_dir:
            messagebox.showerror("Error", "Please select a save location.")
            return

        try:
            downloader = VideoDownloader(self.output_dir)
            downloader.download_video(url)
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
