"""
Logger service implementation.
Follows Single Responsibility Principle (SRP) - handles only logging operations.
"""

import time
from typing import Callable, Optional

from .interfaces import ILogger


class LoggerService(ILogger):
    """
    Concrete implementation of logging functionality.
    Can be extended or replaced without affecting other components - Open/Closed Principle.
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize logger with optional callback for GUI integration

        Args:
            log_callback: Optional callback function to handle log messages
        """
        self._log_callback = log_callback

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message with timestamp and level

        Args:
            message: Message to log
            level: Log level (INFO, ERROR, WARNING, etc.)
        """
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Send to callback if available (for GUI integration)
        if self._log_callback:
            self._log_callback(formatted_message)

        # Also print to console for debugging
        print(f"[{level}] {formatted_message}")

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set or update the log callback function

        Args:
            callback: New callback function
        """
        self._log_callback = callback
