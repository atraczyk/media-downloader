"""
Abstract interfaces for Media Downloader backend services.
Following Interface Segregation Principle (ISP) - clients should not be forced
to depend on interfaces they don't use.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class DownloadType(Enum):
    """Enumeration for download types"""
    AUDIO_MP3 = "Audio (MP3)"
    VIDEO_WEBM = "Video (WebM)"


class DownloadStatus(Enum):
    """Enumeration for download status"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DownloadRequest:
    """Data class representing a download request"""
    url: str
    destination: str
    download_type: DownloadType
    audio_quality: Optional[str] = "192"
    video_quality: Optional[str] = "best"
    transcript_enabled: bool = False


@dataclass
class DownloadProgress:
    """Data class representing download progress"""
    status: DownloadStatus
    progress: float  # 0.0 to 1.0
    message: str
    speed: Optional[float] = None  # MB/s


@dataclass
class MediaInfo:
    """Data class representing media information"""
    title: str
    duration: Optional[int] = None  # seconds
    uploader: Optional[str] = None
    sanitized_filename: str = ""


@dataclass
class TranscriptResult:
    """Data class representing transcript processing result"""
    text: Optional[str]
    error: Optional[str]
    clean_text: Optional[str] = None


# Progress callback type
ProgressCallback = Callable[[DownloadProgress], None]


class IMediaDownloader(ABC):
    """Interface for media downloading functionality"""

    @abstractmethod
    def download(self, request: DownloadRequest, progress_callback: ProgressCallback) -> Tuple[bool, str]:
        """
        Download media from URL

        Args:
            request: Download request parameters
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    @abstractmethod
    def get_media_info(self, url: str) -> Tuple[Optional[MediaInfo], Optional[str]]:
        """
        Get media information without downloading

        Args:
            url: Media URL

        Returns:
            Tuple of (media_info: MediaInfo | None, error: str | None)
        """
        pass


class ITranscriptProcessor(ABC):
    """Interface for transcript processing functionality"""

    @abstractmethod
    def fetch_transcript(self, url: str) -> TranscriptResult:
        """
        Fetch transcript from video URL

        Args:
            url: Video URL

        Returns:
            TranscriptResult with text or error
        """
        pass

    @abstractmethod
    def clean_transcript_text(self, transcript_text: str) -> str:
        """
        Clean transcript text for better readability

        Args:
            transcript_text: Raw transcript text

        Returns:
            Cleaned transcript text
        """
        pass


class IFileManager(ABC):
    """Interface for file management operations"""

    @abstractmethod
    def save_transcript(self, transcript_text: str, media_filename: str, destination: str) -> Optional[str]:
        """
        Save transcript to file

        Args:
            transcript_text: Transcript content
            media_filename: Base media filename
            destination: Destination directory

        Returns:
            Path to saved file or None if failed
        """
        pass

    @abstractmethod
    def save_summary(self, summary_text: str, media_filename: str, destination: str) -> Optional[str]:
        """
        Save summary to file

        Args:
            summary_text: Summary content
            media_filename: Base media filename
            destination: Destination directory

        Returns:
            Path to saved file or None if failed
        """
        pass

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        pass

    @abstractmethod
    def ensure_directory(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Ensure directory exists, create if necessary

        Args:
            path: Directory path

        Returns:
            Tuple of (success: bool, error_message: str | None)
        """
        pass


class ILogger(ABC):
    """Interface for logging functionality"""

    @abstractmethod
    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message

        Args:
            message: Message to log
            level: Log level (INFO, ERROR, WARNING, etc.)
        """
        pass
