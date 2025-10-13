"""
Backend module for Media Downloader
Clean separation of business logic from presentation layer following SOLID principles.
"""

from .media_downloader_facade import MediaDownloaderFacade
from .interfaces import (
    DownloadRequest, DownloadProgress, DownloadStatus, DownloadType,
    TranscriptResult, SummaryResult, MediaInfo
)

# Main facade for external use
__all__ = [
    'MediaDownloaderFacade',
    'DownloadRequest',
    'DownloadProgress',
    'DownloadStatus',
    'DownloadType',
    'TranscriptResult',
    'SummaryResult',
    'MediaInfo'
]
