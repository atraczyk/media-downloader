"""
Facade pattern implementation for Media Downloader operations.
Provides a simplified interface to the complex subsystem of services.
Follows Facade Pattern - provides a unified interface to a set of interfaces in a subsystem.
"""

import threading
from typing import Optional, Callable

from .interfaces import (
    DownloadRequest, DownloadProgress, DownloadStatus,
    TranscriptResult
)
from .service_container import ServiceContainer


class MediaDownloaderFacade:
    """
    Facade that coordinates all media downloading operations.
    Simplifies the interface for the GUI layer.
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize facade with service container

        Args:
            log_callback: Optional callback for GUI log integration
        """
        self._container = ServiceContainer(log_callback)
        self._download_thread = None
        self._is_downloading = False

    def download_media_async(
        self,
        request: DownloadRequest,
        progress_callback: Callable[[DownloadProgress], None],
        transcript_callback: Optional[Callable[[TranscriptResult], None]] = None,
        completion_callback: Optional[Callable[[bool, str, Optional[str]], None]] = None
    ) -> bool:
        """
        Start asynchronous media download with optional transcript and summary processing

        Args:
            request: Download request parameters
            progress_callback: Callback for progress updates
            transcript_callback: Optional callback for transcript results
            summary_callback: Optional callback for summary results
            completion_callback: Optional callback for completion (success, message, filename)

        Returns:
            True if download started successfully, False if already downloading
        """
        if self._is_downloading:
            return False

        self._is_downloading = True
        self._download_thread = threading.Thread(
            target=self._download_worker,
            args=(request, progress_callback, transcript_callback, completion_callback),
            daemon=True
        )
        self._download_thread.start()
        return True

    def get_media_info(self, url: str):
        """Get media information without downloading"""
        downloader = self._container.get_media_downloader()
        return downloader.get_media_info(url)

    def is_downloading(self) -> bool:
        """Check if a download is currently in progress"""
        return self._is_downloading

    def update_log_callback(self, callback: Callable[[str], None]) -> None:
        """Update the log callback for GUI integration"""
        self._container.update_log_callback(callback)

    def _download_worker(
        self,
        request: DownloadRequest,
        progress_callback: Callable[[DownloadProgress], None],
        transcript_callback: Optional[Callable[[TranscriptResult], None]],
        completion_callback: Optional[Callable[[bool, str, Optional[str]], None]]
    ) -> None:
        """Worker method that runs in separate thread"""
        try:
            # Initialize progress
            progress_callback(DownloadProgress(
                status=DownloadStatus.PENDING,
                progress=0.1,
                message="Starting download..."
            ))

            # Get services
            downloader = self._container.get_media_downloader()
            transcript_processor = self._container.get_transcript_processor()
            file_manager = self._container.get_file_manager()

            transcript_result = None
            media_filename = None

            # Process transcript if enabled
            if request.transcript_enabled:
                progress_callback(DownloadProgress(
                    status=DownloadStatus.PROCESSING,
                    progress=0.15,
                    message="Fetching transcript..."
                ))

                transcript_result = transcript_processor.fetch_transcript(request.url)
                if transcript_callback:
                    transcript_callback(transcript_result)

            # Set base progress based on preprocessing
            base_progress = 0.15 if request.transcript_enabled else 0.1

            # Download media
            progress_callback(DownloadProgress(
                status=DownloadStatus.DOWNLOADING,
                progress=base_progress,
                message="Starting media download..."
            ))

            success, result = downloader.download(request, progress_callback)

            if success:
                media_filename = result
                logger = self._container.get_logger()

                # Save transcript and summary files if available
                if transcript_result and transcript_result.text and media_filename:
                    logger.log("Saving transcript to file...")
                    file_manager.save_transcript(transcript_result.text, media_filename, request.destination)

                # Log completion message
                logger.log("Download completed successfully!")

                # Final completion
                progress_callback(DownloadProgress(
                    status=DownloadStatus.COMPLETED,
                    progress=1.0,
                    message="Download completed successfully!"
                ))

                if completion_callback:
                    completion_callback(True, "Download completed successfully!", media_filename)
            else:
                # Download failed
                progress_callback(DownloadProgress(
                    status=DownloadStatus.FAILED,
                    progress=0.0,
                    message=f"Download failed: {result}"
                ))

                if completion_callback:
                    completion_callback(False, result, None)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            progress_callback(DownloadProgress(
                status=DownloadStatus.FAILED,
                progress=0.0,
                message=error_msg
            ))

            if completion_callback:
                completion_callback(False, error_msg, None)

        finally:
            self._is_downloading = False
