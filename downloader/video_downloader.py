from utils.logger import logger
from typing import Callable, Dict, Any, Optional
import yt_dlp
import os
from utils.validator import sanitize_filename, get_available_filename

class VideoDownloader:
    """
    Handles downloading videos from YouTube using yt-dlp with progress tracking.
    """

    def __init__(self, output_dir: str, format: str = "video+audio"):
        """
        Initialize the downloader with a target output directory.
        :param output_dir: Directory where files will be saved.
        :param format: Format of the download (video, audio, or video+audio).
        """
        self.output_dir = output_dir
        self.format = format
        self._progress_callback: Optional[Callable] = None
        self._current_filename: Optional[str] = None

    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set a callback function to receive progress updates.
        :param callback: Function that takes a dictionary of progress information
        """
        self._progress_callback = callback

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Internal progress hook for yt-dlp.
        """
        if self._progress_callback is None:
            return

        # Prepare progress information
        progress_info = {
            'status': d.get('status', 'unknown'),
            'filename': self._current_filename,
            'elapsed': d.get('elapsed', 0),
            'total_bytes': d.get('total_bytes', 0),
            'total_bytes_estimate': d.get('total_bytes_estimate', 0),
            'downloaded_bytes': d.get('downloaded_bytes', 0),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0),
            'percentage': 0.0
        }

        # Calculate percentage
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                progress_info['percentage'] = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                progress_info['percentage'] = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100

        # Call the callback with progress information
        self._progress_callback(progress_info)

    def download_video(self, url: str) -> Dict[str, Any]:
        """
        Downloads a video from YouTube with progress tracking.
        :param url: The URL of the YouTube video.
        :return: Dictionary containing download results
        """
        if not self._validate_url(url):
            raise ValueError("Invalid YouTube URL")
        
        try:
            # Get video info first
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                
            # Get the extension from the best format
            ext = info['ext']
            sanitized_title = sanitize_filename(info.get("title", "video"))
            base_filename = f"{sanitized_title}.{ext}"
            
            # Get an available filename with the actual extension
            final_filename = get_available_filename(self.output_dir, base_filename)
            self._current_filename = final_filename
            
            logger.info(f"Video title sanitized: {sanitized_title}")
            logger.info(f"Final filename: {final_filename}")

            # yt-dlp options
            options = {
                "format": self._get_format_option(),
                "outtmpl": os.path.join(self.output_dir, final_filename),
                "quiet": False,
                "no_warnings": False,
                "nooverwrites": True,
                "progress_hooks": [self._progress_hook],
            }

            # Download the video
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            logger.info("Download completed successfully.")
            
            return {
                'status': 'completed',
                'filename': final_filename,
                'filepath': os.path.join(self.output_dir, final_filename),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'filesize': info.get('filesize'),
                'format': info.get('format')
            }

        except Exception as e:
            logger.error(f"Error during download: {str(e)}")
            raise

    def _get_format_option(self) -> str:
        """
        Get the format option for yt-dlp based on the desired format.
        :return: Format option string for yt-dlp.
        """
        if self.format == "video":
            return "bestvideo"
        elif self.format == "audio":
            return "bestaudio"
        return "best"

    @staticmethod
    def _validate_url(url: str) -> bool:
        """
        Validates if a URL is a YouTube link.
        :param url: The URL to validate.
        :return: True if valid, False otherwise.
        """
        return "youtube.com/watch" in url or "youtu.be/" in url