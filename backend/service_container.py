"""
Dependency injection container for Media Downloader services.
Follows Dependency Inversion Principle (DIP) - high-level modules should not depend on low-level modules.
Both should depend on abstractions.
"""

from typing import Optional, Callable

from .interfaces import (
    IMediaDownloader, ITranscriptProcessor,
    IFileManager, ILogger
)
from .media_downloader import MediaDownloadService
from .transcript_processor import TranscriptProcessorService
from .file_manager import FileManagerService
from .logger import LoggerService


class ServiceContainer:
    """
    Service container for dependency injection.
    Manages service lifetimes and dependencies.
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize service container

        Args:
            log_callback: Optional callback for GUI log integration
        """
        self._log_callback = log_callback
        self._services = {}
        self._initialize_services()

    def _initialize_services(self) -> None:
        """Initialize all services with proper dependency injection"""
        # Create logger first (no dependencies)
        logger = LoggerService(self._log_callback)
        self._services['logger'] = logger

        # Create file manager (depends on logger)
        file_manager = FileManagerService(logger)
        self._services['file_manager'] = file_manager

        # Create transcript processor (depends on logger)
        transcript_processor = TranscriptProcessorService(logger)
        self._services['transcript_processor'] = transcript_processor

        # Create media downloader (depends on logger and file_manager)
        media_downloader = MediaDownloadService(logger, file_manager)
        self._services['media_downloader'] = media_downloader

    def get_logger(self) -> ILogger:
        """Get logger service instance"""
        return self._services['logger']

    def get_file_manager(self) -> IFileManager:
        """Get file manager service instance"""
        return self._services['file_manager']

    def get_transcript_processor(self) -> ITranscriptProcessor:
        """Get transcript processor service instance"""
        return self._services['transcript_processor']

    def get_media_downloader(self) -> IMediaDownloader:
        """Get media downloader service instance"""
        return self._services['media_downloader']

    def update_log_callback(self, callback: Callable[[str], None]) -> None:
        """
        Update the log callback for GUI integration

        Args:
            callback: New callback function
        """
        self._log_callback = callback
        logger = self._services.get('logger')
        if isinstance(logger, LoggerService):
            logger.set_callback(callback)
