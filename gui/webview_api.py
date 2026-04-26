"""
WebView API bridge for Media Downloader.
Handles communication between Python backend and JavaScript frontend.
Follows Single Responsibility Principle - only handles API bridging.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import webview

from backend import (
    MediaDownloaderFacade, DownloadRequest, DownloadProgress,
    DownloadStatus, DownloadType, TranscriptResult, SummaryResult
)


class MediaDownloaderAPI:
    """
    API class that bridges Python backend with JavaScript frontend.
    Provides a clean interface for webview communication.
    """

    def __init__(self):
        """Initialize API with backend facade"""
        self.facade = MediaDownloaderFacade()
        self.window = None

        # Set up logging callback
        self.facade.update_log_callback(self._handle_log_message)

        # State management
        self._current_download = None
        self._logs = []

    def set_window(self, window):
        """Set the webview window reference for callbacks"""
        self.window = window

    def get_app_info(self) -> Dict[str, Any]:
        """Get application information"""
        return {
            'name': 'Media Downloader',
            'version': '2.0.0',
            'framework': 'PyWebView',
            'backend': 'Python 3.x',
            'description': 'Download audio and video from YouTube with transcript and summary support'
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import platform
        return {
            'platform': platform.system(),
            'version': platform.version(),
            'processor': platform.processor(),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'python_version': platform.python_version()
        }

    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate and get information about a media URL"""
        try:
            if not url or not url.strip():
                return {'valid': False, 'error': 'URL is required'}

            # Get media info to validate URL
            media_info, error = self.facade.get_media_info(url.strip())

            if error:
                return {'valid': False, 'error': error}

            if media_info:
                return {
                    'valid': True,
                    'title': media_info.title,
                    'duration': media_info.duration,
                    'uploader': media_info.uploader
                }

            return {'valid': False, 'error': 'Could not retrieve media information'}

        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}

    def browse_folder(self) -> Dict[str, Any]:
        """Open folder browser dialog"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=str(Path.cwd() / "downloads")
            )

            if result and len(result) > 0:
                return {'success': True, 'path': result[0]}
            else:
                return {'success': False, 'error': 'No folder selected'}

        except Exception as e:
            return {'success': False, 'error': f'Folder selection error: {str(e)}'}

    def start_download(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start media download with given parameters"""
        try:
            if self.facade.is_downloading():
                return {'success': False, 'error': 'A download is already in progress'}

            # Validate required fields
            url = request_data.get('url', '').strip()
            destination = request_data.get('destination', '').strip()

            if not url:
                return {'success': False, 'error': 'URL is required'}

            if not destination:
                return {'success': False, 'error': 'Destination folder is required'}

            # Create download request
            download_type_str = request_data.get('downloadType', 'Audio (MP3)')
            download_type = DownloadType.AUDIO_MP3 if download_type_str == 'Audio (MP3)' else DownloadType.VIDEO_WEBM

            request = DownloadRequest(
                url=url,
                destination=destination,
                download_type=download_type,
                audio_quality=request_data.get('audioQuality', '192'),
                video_quality=request_data.get('videoQuality', 'best'),
                transcript_enabled=request_data.get('transcriptEnabled', False),
                summary_enabled=request_data.get('summaryEnabled', False)
            )

            # Clear previous logs
            self._logs = []

            # Start download
            success = self.facade.download_media_async(
                request=request,
                progress_callback=self._handle_progress,
                transcript_callback=self._handle_transcript,
                summary_callback=self._handle_summary,
                completion_callback=self._handle_completion
            )

            if success:
                self._current_download = request_data
                return {'success': True, 'message': 'Download started successfully'}
            else:
                return {'success': False, 'error': 'Failed to start download'}

        except Exception as e:
            return {'success': False, 'error': f'Download error: {str(e)}'}

    def get_download_status(self) -> Dict[str, Any]:
        """Get current download status"""
        return {
            'isDownloading': self.facade.is_downloading(),
            'currentDownload': self._current_download
        }

    def get_logs(self) -> Dict[str, Any]:
        """Get current logs"""
        return {'logs': self._logs}

    def clear_logs(self) -> Dict[str, Any]:
        """Clear current logs"""
        self._logs = []
        return {'success': True}

    def _handle_log_message(self, message: str):
        """Handle log messages from backend"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self._logs.append(log_entry)

        # Notify frontend of new log
        if self.window:
            self.window.evaluate_js(f'window.handleLogUpdate({json.dumps(log_entry)})')

    def _handle_progress(self, progress: DownloadProgress):
        """Handle progress updates from backend"""
        if self.window:
            progress_data = {
                'status': progress.status.value,
                'progress': progress.progress,
                'message': progress.message,
                'speed': progress.speed
            }
            self.window.evaluate_js(f'window.handleProgressUpdate({json.dumps(progress_data)})')

    def _handle_transcript(self, result: TranscriptResult):
        """Handle transcript results from backend"""
        if self.window:
            transcript_data = {
                'text': result.text,
                'error': result.error,
                'clean_text': result.clean_text
            }
            self.window.evaluate_js(f'window.handleTranscriptUpdate({json.dumps(transcript_data)})')

    def _handle_summary(self, result: SummaryResult):
        """Handle summary results from backend"""
        if self.window:
            summary_data = {
                'summary': result.summary,
                'error': result.error
            }
            self.window.evaluate_js(f'window.handleSummaryUpdate({json.dumps(summary_data)})')

    def _handle_completion(self, success: bool, message: str, filename: Optional[str]):
        """Handle download completion from backend"""
        self._current_download = None

        if self.window:
            completion_data = {
                'success': success,
                'message': message,
                'filename': filename
            }
            self.window.evaluate_js(f'window.handleDownloadComplete({json.dumps(completion_data)})')

