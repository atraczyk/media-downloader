"""
Transcript processing service implementation.
Follows Single Responsibility Principle (SRP) - handles only transcript operations.
"""

import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

from .interfaces import ITranscriptProcessor, ILogger, TranscriptResult


class TranscriptProcessorService(ITranscriptProcessor):
    """
    Concrete implementation of transcript processing functionality.
    Depends on abstractions (ILogger) not concretions - Dependency Inversion Principle.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize with dependencies injected

        Args:
            logger: Logger implementation
        """
        self._logger = logger

    def fetch_transcript(self, url: str) -> TranscriptResult:
        """Fetch transcript from YouTube video URL"""
        video_id = self._extract_youtube_video_id(url)
        if not video_id:
            return TranscriptResult(
                text=None,
                error="Not a valid YouTube URL"
            )

        try:
            # Use the instance-based API correctly
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=['en'])

            # Format transcript as readable text with timestamps
            transcript_text = ""
            for entry in transcript:
                # Convert seconds to MM:SS format
                minutes, seconds = divmod(int(entry.start), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                # Clean up text and handle potential Unicode issues
                clean_text = entry.text.replace('\n', ' ').strip()
                transcript_text += f"[{timestamp}] {clean_text}\n"

            # Also generate clean text version
            clean_text = self.clean_transcript_text(transcript_text)

            return TranscriptResult(
                text=transcript_text,
                error=None,
                clean_text=clean_text
            )

        except Exception as e:
            error_msg = f"Transcript not available: {str(e)}"
            self._logger.log(error_msg, "WARNING")
            return TranscriptResult(
                text=None,
                error=error_msg
            )

    def clean_transcript_text(self, transcript_text: str) -> str:
        """Extract clean text from timestamped transcript for better readability"""
        if not transcript_text:
            return ""

        # Remove timestamps and clean up the text
        clean_text = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*', '', transcript_text)
        # Remove empty brackets
        clean_text = re.sub(r'\[\s*\]\s*', '', clean_text)
        # Clean up multiple spaces and normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        # Split into sentences and rejoin for better formatting
        sentences = re.split(r'([.!?]+)', clean_text)
        formatted_text = ""
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i].strip()
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            if sentence:
                formatted_text += sentence + punct + " "

        return formatted_text.strip()

    def _extract_youtube_video_id(self, youtube_url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([\w-]+)',
            r'(?:https?://)?(?:www\.)?m\.youtube\.com/watch\?.*v=([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([\w-]+)',
        ]

        for pattern in youtube_patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)

        return None
