"""
AI summarization service implementation.
Follows Single Responsibility Principle (SRP) - handles only text summarization.
"""

import re
import warnings
from typing import Optional, List
from transformers import pipeline

from .interfaces import ISummarizationService, ILogger, SummaryResult


class SummarizationService(ISummarizationService):
    """
    Concrete implementation of AI text summarization functionality.
    Depends on abstractions (ILogger) not concretions - Dependency Inversion Principle.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize with dependencies injected

        Args:
            logger: Logger implementation
        """
        self._logger = logger
        self._summarizer = None
        self._model_name = "sshleifer/distilbart-cnn-12-6"

    def summarize_text(self, text: str) -> SummaryResult:
        """Generate summary from text using AI model"""
        if not text or len(text.strip()) < 50:
            return SummaryResult(
                summary=None,
                error="Text too short to summarize (minimum 50 characters)"
            )

        try:
            summarizer = self._get_summarizer()
            if not summarizer:
                return SummaryResult(
                    summary=None,
                    error="Summarization model not available"
                )

            # Clean text for better summarization
            clean_text = self._clean_text_for_summarization(text)

            if len(clean_text) < 50:
                return SummaryResult(
                    summary=None,
                    error="Cleaned text too short to summarize"
                )

            # Handle long texts by chunking
            if len(clean_text) > 1000:
                self._logger.log("Text is long, processing in chunks...")
                return self._summarize_long_text(clean_text, summarizer)
            else:
                # Short text, summarize directly
                return self._summarize_short_text(clean_text, summarizer)

        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            self._logger.log(error_msg, "ERROR")
            return SummaryResult(
                summary=None,
                error=error_msg
            )

    def is_available(self) -> bool:
        """Check if summarization service is available"""
        try:
            summarizer = self._get_summarizer()
            return summarizer is not None
        except Exception:
            return False

    def _get_summarizer(self):
        """Initialize and return the summarizer (lazy loading)"""
        if self._summarizer is None:
            try:
                # Suppress warnings from transformers
                warnings.filterwarnings("ignore", category=UserWarning)
                self._logger.log("Loading summarization model (first time only)...")
                self._summarizer = pipeline("summarization", model=self._model_name)
                self._logger.log("Summarization model loaded successfully!")
            except Exception as e:
                self._logger.log(f"Failed to load summarization model: {str(e)}", "ERROR")
                return None
        return self._summarizer

    def _clean_text_for_summarization(self, text: str) -> str:
        """Clean text for better summarization results"""
        # Remove various timestamp formats: [MM:SS], [HH:MM:SS], (MM:SS), etc.
        clean_text = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*', '', text)
        # Remove any remaining brackets or parentheses that might contain timestamps
        clean_text = re.sub(r'\[\s*\]\s*', '', clean_text)
        # Clean up multiple spaces and newlines
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    def _summarize_short_text(self, text: str, summarizer) -> SummaryResult:
        """Summarize short text directly"""
        try:
            # Adaptive max_length based on text size
            text_max_length = min(150, max(30, len(text) // 3))
            summary = summarizer(text, max_length=text_max_length, min_length=20, do_sample=False)

            return SummaryResult(
                summary=summary[0]['summary_text'],
                error=None
            )
        except Exception as e:
            return SummaryResult(
                summary=None,
                error=f"Failed to summarize short text: {str(e)}"
            )

    def _summarize_long_text(self, text: str, summarizer) -> SummaryResult:
        """Summarize long text by chunking"""
        try:
            chunks = self._chunk_text(text, max_chunk_size=1000)
            chunk_summaries = []

            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:  # Skip very short chunks
                    continue

                try:
                    # Adaptive max_length based on chunk size
                    chunk_max_length = min(100, max(30, len(chunk) // 4))
                    summary = summarizer(chunk, max_length=chunk_max_length, min_length=20, do_sample=False)
                    chunk_summaries.append(summary[0]['summary_text'])
                    self._logger.log(f"Processed chunk {i+1}/{len(chunks)}")
                except Exception as e:
                    self._logger.log(f"Failed to summarize chunk {i+1}: {str(e)}", "WARNING")
                    continue

            if not chunk_summaries:
                return SummaryResult(
                    summary=None,
                    error="Failed to generate summary from any chunks"
                )

            # Combine chunk summaries
            combined_summary = ' '.join(chunk_summaries)

            # If combined summary is still too long, summarize it again
            if len(combined_summary) > 1000:
                final_max_length = min(200, max(50, len(combined_summary) // 3))
                final_summary = summarizer(combined_summary, max_length=final_max_length, min_length=50, do_sample=False)
                return SummaryResult(
                    summary=final_summary[0]['summary_text'],
                    error=None
                )
            else:
                return SummaryResult(
                    summary=combined_summary,
                    error=None
                )

        except Exception as e:
            return SummaryResult(
                summary=None,
                error=f"Failed to summarize long text: {str(e)}"
            )

    def _chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for summarization, preserving sentence boundaries"""
        # Split on multiple sentence endings for better boundary detection
        sentences = re.split(r'[.!?]+\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Estimate the length with proper punctuation
            sentence_with_punct = sentence + '. '

            # Add sentence to current chunk if it fits
            if len(current_chunk + sentence_with_punct) <= max_chunk_size:
                current_chunk += sentence_with_punct
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence_with_punct

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
