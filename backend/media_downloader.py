"""
Media download service implementation.
Follows Single Responsibility Principle (SRP) - handles only media downloading.
"""

import yt_dlp as youtube_dl
import os
from typing import Optional, Tuple
from pathlib import Path

from .interfaces import (
    IMediaDownloader, ILogger, DownloadRequest, DownloadProgress,
    MediaInfo, DownloadStatus, DownloadType, ProgressCallback
)


class MediaDownloadService(IMediaDownloader):
    """
    Concrete implementation of media downloading functionality.
    Depends on abstractions (ILogger) not concretions - Dependency Inversion Principle.
    """

    def __init__(self, logger: ILogger, file_manager):
        """
        Initialize with dependencies injected

        Args:
            logger: Logger implementation
            file_manager: File manager implementation
        """
        self._logger = logger
        self._file_manager = file_manager

    def download(self, request: DownloadRequest, progress_callback: ProgressCallback) -> Tuple[bool, str]:
        """Download media from URL with progress tracking"""
        try:
            self._logger.log(f"Starting {request.download_type.value} download from: {request.url}")
            self._logger.log(f"Destination: {request.destination}")

            # Ensure destination directory exists
            success, error = self._file_manager.ensure_directory(request.destination)
            if not success:
                return False, f"Failed to create destination directory: {error}"

            # Get media info first
            media_info, error = self.get_media_info(request.url)
            if error:
                return False, f"Failed to get media info: {error}"

            if not media_info:
                return False, "Could not retrieve media information"

            self._logger.log(f"Title: {media_info.title}")
            if media_info.uploader:
                self._logger.log(f"Uploader: {media_info.uploader}")
            if media_info.duration:
                self._log_duration(media_info.duration)

            # Configure yt-dlp options
            ydl_opts = self._build_ydl_options(request, progress_callback)

            # Perform download
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([request.url])

            # Generate expected filename
            if request.download_type == DownloadType.AUDIO_MP3:
                expected_filename = f"{media_info.sanitized_filename}.mp3"
            else:
                expected_filename = f"{media_info.sanitized_filename}.webm"

            progress_callback(DownloadProgress(
                status=DownloadStatus.COMPLETED,
                progress=1.0,
                message="Download completed successfully!"
            ))

            return True, expected_filename

        except youtube_dl.DownloadError as e:
            error_msg = f"Download error: {str(e)}"
            self._logger.log(error_msg, "ERROR")
            self._log_download_suggestions(str(e))
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._logger.log(error_msg, "ERROR")
            return False, error_msg

    def get_media_info(self, url: str) -> Tuple[Optional[MediaInfo], Optional[str]]:
        """Get media information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extractaudio': False,
                'writeinfojson': False,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')

                # Sanitize filename
                sanitized_filename = self._file_manager.sanitize_filename(title)

                media_info = MediaInfo(
                    title=title,
                    duration=int(duration) if duration else None,
                    uploader=uploader,
                    sanitized_filename=sanitized_filename
                )

                return media_info, None

        except Exception as e:
            return None, str(e)

    def _build_ydl_options(self, request: DownloadRequest, progress_callback: ProgressCallback) -> dict:
        """Build yt-dlp options based on request parameters"""
        # Common options to avoid 403 errors
        common_opts = {
            'outtmpl': os.path.join(request.destination, '%(title).200s.%(ext)s'),
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback)],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'ignoreerrors': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'restrictfilenames': True,
            'windowsfilenames': True,
            'trim_filenames': 200,
        }

        if request.download_type == DownloadType.AUDIO_MP3:
            return {
                **common_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': request.audio_quality,
                }],
            }
        else:  # Video
            quality = request.video_quality
            if quality == "best":
                format_str = "bestvideo+bestaudio/best"
            elif quality == "worst":
                format_str = "worstvideo+worstaudio/worst"
            else:
                # For specific resolutions
                height = quality[:-1]  # Remove 'p'
                format_str = f"bestvideo[height<={height}]+bestaudio/best"

            return {
                **common_opts,
                'format': format_str,
            }

    def _progress_hook(self, d: dict, progress_callback: ProgressCallback) -> None:
        """Handle yt-dlp progress updates"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = d['downloaded_bytes'] / d['total_bytes']
                progress = 0.3 + (percent * 0.6)  # 30-90% for download

                speed = d.get('speed', 0)
                speed_mb = speed / 1024 / 1024 if speed else 0

                message = f"Downloaded {percent*100:.1f}%"
                if speed_mb > 0:
                    message += f" at {speed_mb:.1f} MB/s"

                progress_callback(DownloadProgress(
                    status=DownloadStatus.DOWNLOADING,
                    progress=progress,
                    message=message,
                    speed=speed_mb
                ))

        elif d['status'] == 'finished':
            progress_callback(DownloadProgress(
                status=DownloadStatus.PROCESSING,
                progress=0.9,
                message=f"Finished downloading: {os.path.basename(d['filename'])}"
            ))

    def _log_duration(self, duration_seconds: int) -> None:
        """Log formatted duration"""
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            self._logger.log(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")
        else:
            self._logger.log(f"Duration: {minutes}:{seconds:02d}")

    def _log_download_suggestions(self, error_str: str) -> None:
        """Log helpful suggestions based on error type"""
        if "403" in error_str or "Forbidden" in error_str:
            self._logger.log("SUGGESTION: This might be a region-blocked video or YouTube is blocking requests.")
            self._logger.log("Try: 1) Different video 2) Wait a few minutes 3) Use VPN if region-blocked")
        elif "404" in error_str:
            self._logger.log("SUGGESTION: Video not found. Check if the URL is correct and video exists.")
        elif "Private video" in error_str:
            self._logger.log("SUGGESTION: This is a private video. Only the owner can download it.")
