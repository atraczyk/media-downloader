"""
File management service implementation.
Follows Single Responsibility Principle (SRP) - handles only file operations.
"""

import os
import re
from typing import Optional, Tuple
from pathlib import Path

from .interfaces import IFileManager, ILogger


class FileManagerService(IFileManager):
    """
    Concrete implementation of file management functionality.
    Depends on abstractions (ILogger) not concretions - Dependency Inversion Principle.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize with dependencies injected

        Args:
            logger: Logger implementation
        """
        self._logger = logger

    def save_transcript(self, transcript_text: str, media_filename: str, destination: str) -> Optional[str]:
        """Save transcript to a text file with similar name as media file"""
        if not transcript_text:
            return None

        try:
            # Create transcript filename based on media filename
            base_name = os.path.splitext(media_filename)[0]
            transcript_filename = f"{base_name}_transcript.txt"
            transcript_path = os.path.join(destination, transcript_filename)

            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            self._logger.log(f"Transcript saved to: {os.path.basename(transcript_path)}")
            return transcript_path

        except Exception as e:
            self._logger.log(f"Failed to save transcript: {str(e)}", "ERROR")
            return None

    def save_summary(self, summary_text: str, media_filename: str, destination: str) -> Optional[str]:
        """Save summary to a text file with similar name as media file"""
        if not summary_text:
            return None

        try:
            # Create summary filename based on media filename
            base_name = os.path.splitext(media_filename)[0]
            summary_filename = f"{base_name}_summary.txt"
            summary_path = os.path.join(destination, summary_filename)

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Video Summary:\n\n{summary_text}")

            self._logger.log(f"Summary saved to: {os.path.basename(summary_path)}")
            return summary_path

        except Exception as e:
            self._logger.log(f"Failed to save summary: {str(e)}", "ERROR")
            return None

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters for Windows filesystem"""
        # Characters not allowed in Windows filenames
        invalid_chars = '<>:"/\\|?*'

        # Replace invalid characters with underscores
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove or replace other problematic characters
        filename = filename.replace('｜', '_')  # Replace full-width vertical bar
        filename = filename.replace('·', '_')   # Replace middle dot
        filename = filename.replace('…', '...')  # Replace ellipsis

        # Remove emojis and other Unicode symbols
        filename = re.sub(r'[\U0001F600-\U0001F64F]', '', filename)  # Emoticons
        filename = re.sub(r'[\U0001F300-\U0001F5FF]', '', filename)  # Symbols & pictographs
        filename = re.sub(r'[\U0001F680-\U0001F6FF]', '', filename)  # Transport & map symbols
        filename = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', filename)  # Flags
        filename = re.sub(r'[\U00002600-\U000026FF]', '', filename)  # Miscellaneous symbols
        filename = re.sub(r'[\U00002700-\U000027BF]', '', filename)  # Dingbats

        # Remove hashtags
        filename = filename.replace('#', '')

        # Convert to ASCII, replacing non-ASCII characters
        filename = filename.encode('ascii', 'ignore').decode('ascii')

        # Replace multiple consecutive spaces/underscores with single underscore
        filename = re.sub(r'[_\s]+', '_', filename)

        # Remove leading/trailing spaces and underscores
        filename = filename.strip(' _')

        # Limit filename length (Windows has 260 char path limit)
        if len(filename) > 200:
            filename = filename[:200].rstrip('_')

        # Ensure filename is not empty and doesn't end with period (Windows restriction)
        if not filename or filename == '.':
            filename = "untitled"
        elif filename.endswith('.'):
            filename = filename.rstrip('.') + '_'

        return filename

    def ensure_directory(self, path: str) -> Tuple[bool, Optional[str]]:
        """Ensure directory exists, create if necessary"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                self._logger.log(f"Created destination directory: {path}")
            return True, None
        except Exception as e:
            error_msg = f"Failed to create directory: {str(e)}"
            self._logger.log(error_msg, "ERROR")
            return False, error_msg
