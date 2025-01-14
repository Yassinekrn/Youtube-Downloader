from utils.logger import logger

logger.info("Starting video download...")
try:
    from utils.validator import sanitize_filename
    from utils.validator import get_available_filename
    import yt_dlp
    import os

    class VideoDownloader:
        """
        Handles downloading videos from YouTube using yt-dlp.
        """

        def __init__(self, output_dir: str):
            """
            Initialize the downloader with a target output directory.
            :param output_dir: Directory where files will be saved.
            """
            self.output_dir = output_dir

        def download_video(self, url: str) -> None:
            """
            Downloads a video from YouTube.
            :param url: The URL of the YouTube video.
            """
            if not self._validate_url(url):
                raise ValueError("Invalid YouTube URL")
            
            # Get video info first
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                
            # Get the extension from the best format
            ext = info['ext']
            sanitized_title = sanitize_filename(info.get("title", "video"))
            base_filename = f"{sanitized_title}.{ext}"
            
            # Get an available filename with the actual extension
            final_filename = get_available_filename(self.output_dir, base_filename)
            logger.info(f"Video title sanitized: {sanitized_title}")
            logger.info(f"Final filename: {final_filename}")

            # yt-dlp options with exact filename (no template)
            options = {
                "format": "best",
                "outtmpl": os.path.join(self.output_dir, final_filename),
                "quiet": False,
                "no_warnings": False,
                # Prevent auto-numbering
                "nooverwrites": True,
            }

            # Download the video
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            logger.info("Download completed successfully.")

        @staticmethod
        def _validate_url(url: str) -> bool:
            """
            Validates if a URL is a YouTube link.
            :param url: The URL to validate.
            :return: True if valid, False otherwise.
            """
            return "youtube.com/watch" in url or "youtu.be/" in url

except Exception as e:
    logger.error(f"Error during download: {e}")
    raise