import threading
import queue
from typing import Callable, Dict, Any, Optional
from downloader.video_downloader import VideoDownloader
from utils.logger import logger

class DownloadManager:
    """
    Manages video downloads in separate threads with progress tracking.
    """
    def __init__(self):
        self.progress_queue = queue.Queue()
        self.active_downloads: Dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()

    def start_download(
        self,
        downloader: 'VideoDownloader',
        url: str,
        progress_callback: Callable[[Dict[str, Any]], None],
        completion_callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Start a new download in a separate thread.
        """
        def download_thread():
            try:
                # Set up progress tracking
                def progress_handler(progress: Dict[str, Any]):
                    if not self._stop_event.is_set():
                        self.progress_queue.put(('progress', url, progress))

                downloader.set_progress_callback(progress_handler)
                
                # Start the download
                result = downloader.download_video(url)
                
                # Signal completion
                if not self._stop_event.is_set():
                    self.progress_queue.put(('complete', url, result))
            except Exception as e:
                if not self._stop_event.is_set():
                    self.progress_queue.put(('error', url, str(e)))
                logger.error(f"Download thread error: {str(e)}")
            finally:
                if url in self.active_downloads:
                    del self.active_downloads[url]

        # Create and start the download thread
        thread = threading.Thread(target=download_thread)
        self.active_downloads[url] = thread
        thread.start()

    def process_progress_updates(self, progress_callback: Callable[[Dict[str, Any]], None], completion_callback: Callable[[Dict[str, Any]], None], error_callback: Callable[[str], None]) -> None:
        """
        Process any pending progress updates from the queue.
        Should be called periodically from the main thread.
        """
        try:
            while True:
                update_type, url, data = self.progress_queue.get_nowait()
                if update_type == 'progress':
                    progress_callback(data)
                elif update_type == 'complete':
                    completion_callback(data)
                elif update_type == 'error':
                    error_callback(data)
                self.progress_queue.task_done()
        except queue.Empty:
            pass

    def stop_all_downloads(self) -> None:
        """
        Stop all active downloads.
        """
        self._stop_event.set()
        for thread in self.active_downloads.values():
            thread.join()
        self.active_downloads.clear()
        self._stop_event.clear()

    def is_download_active(self, url: str) -> bool:
        """
        Check if a download is currently active.
        """
        return url in self.active_downloads