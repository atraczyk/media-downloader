import yt_dlp as youtube_dl
import os
import dearpygui.dearpygui as dpg
import threading
from pathlib import Path
import time
from youtube_transcript_api import YouTubeTranscriptApi
import re
import string
from transformers import pipeline
import warnings

class MediaDownloaderGUI:
    def __init__(self):
        self.download_thread = None
        self.is_downloading = False
        # Consistent left/right and top/bottom padding inside main window
        self.window_padding = 15  # Reduced from 20 for more content space
        # Vertical spacing used in height calculations
        self.vertical_spacing = 6  # Reduced from 8 for tighter layout
        # Initialize summarizer (lazy loading)
        self.summarizer = None
        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title="Media Downloader", width=800, height=900)
        dpg.setup_dearpygui()

                # Primary window to match viewport; prevents layout drift
        with dpg.window(
            label="Media Downloader",
            tag="main_window",
            no_resize=True,
            no_move=True,
            no_collapse=True,
            no_close=True,
            no_title_bar=True,
            no_bring_to_front_on_focus=True,
        ):
            with dpg.group(tag="content_group"):
                # URL input
                dpg.add_text("URL:")
                dpg.add_input_text(
                    tag="url_input", hint="Enter URL here...", width=760
                )

                # Download type selection
                dpg.add_text("Download Type:")
                with dpg.group(horizontal=True):
                    dpg.add_radio_button(
                        items=["Audio (MP3)", "Video (WebM)"],
                        tag="download_type",
                        default_value="Audio (MP3)",
                        callback=self.on_type_change
                    )

                # Transcript options
                dpg.add_separator()
                dpg.add_text("Transcript Options:")
                dpg.add_checkbox(
                    label="Download transcript (if available)",
                    tag="transcript_enabled",
                    default_value=True
                )
                dpg.add_checkbox(
                    label="Generate summary (requires transcript)",
                    tag="summary_enabled",
                    default_value=False
                )

                # Format options
                with dpg.collapsing_header(label="Format Options", default_open=True):
                    with dpg.group(tag="audio_opts"):
                        dpg.add_text("Audio Quality:")
                        dpg.add_combo(
                            items=["128", "192", "256", "320"],
                            default_value="192",
                            tag="audio_quality",
                            width=200,
                        )

                    with dpg.group(tag="video_opts"):
                        dpg.add_text("Video Quality:")
                        dpg.add_combo(
                            items=["best", "worst", "720p", "1080p", "1440p", "2160p"],
                            default_value="best",
                            tag="video_quality",
                            width=200,
                        )
                    # Hide video options by default when audio is selected
                    dpg.configure_item("video_opts", show=False)

                # Destination selection
                dpg.add_text("Save to:")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        tag="dest_input",
                        default_value=str(Path.cwd() / "downloads"),
                        width=680,
                    )
                    dpg.add_button(
                        label="Browse", callback=self.browse_destination, width=100
                    )

                # Download button
                dpg.add_separator()
                dpg.add_button(
                    label="Download MP3",
                    tag="download_btn",
                    callback=self.start_download,
                    height=34,
                    width=760
                )

                # Progress section
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text("Status:")
                    dpg.add_text("Ready to download", tag="status_text", color=(255, 255, 0))

                # Progress bar
                dpg.add_progress_bar(
                    tag="progress_bar", default_value=0.0, width=760
                )

            # Transcript display
            dpg.add_text("Transcript:", tag="transcript_label")
            with dpg.child_window(
                tag="transcript_window",
                height=80,
                width=760,
                horizontal_scrollbar=False,
                border=True
            ):
                dpg.add_text(
                    "Transcript will appear here when available...",
                    tag="transcript_text",
                    wrap=740,  # Reduced padding for more text space
                    color=(150, 150, 150)  # Gray hint color
                )
            # Apply reduced padding theme to transcript window
            dpg.bind_item_theme("transcript_window", "child_window_theme")

            # Summary display
            dpg.add_text("Summary:", tag="summary_label")
            with dpg.child_window(
                tag="summary_window",
                height=80,
                width=760,
                horizontal_scrollbar=False,
                border=True
            ):
                dpg.add_text(
                    "Summary will appear here when generated...",
                    tag="summary_text",
                    wrap=740,  # Reduced padding for more text space
                    color=(150, 150, 150)  # Gray hint color
                )
            # Apply reduced padding theme to summary window
            dpg.bind_item_theme("summary_window", "child_window_theme")

            # Status log
            dpg.add_text("Log:", tag="log_label")
            dpg.add_input_text(
                tag="log_text",
                multiline=True,
                readonly=True,
                height=80,  # Start with minimum height
                width=760,
            )

        # Folder chooser for destination selection
        with dpg.file_dialog(directory_selector=True, show=False, callback=self.on_directory_selected, tag="dir_dialog"):
            pass

        # Ensure the main window fills and follows the viewport
        dpg.set_primary_window("main_window", True)

        # Bind window padding theme for symmetric margins
        with dpg.theme(tag="main_window_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(
                    dpg.mvStyleVar_WindowPadding,
                    self.window_padding,
                    self.window_padding,
                )
        dpg.bind_item_theme("main_window", "main_window_theme")

        # Create theme for child windows with reduced padding
        with dpg.theme(tag="child_window_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)  # Reduced internal padding
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)    # Reduced item spacing

        # Handle dynamic resizing to anchor widgets to window width
        with dpg.item_handler_registry(tag="main_window_handlers"):
            dpg.add_item_resize_handler(callback=self.on_main_window_resize)
        dpg.bind_item_handler_registry("main_window", "main_window_handlers")

        # Perform initial layout sizing
        self.on_main_window_resize(None, None, None)

    def on_type_change(self, sender, app_data):
        """Handle download type change"""
        if app_data == "Audio (MP3)":
            dpg.configure_item("download_btn", label="Download MP3")
            dpg.configure_item("audio_opts", show=True)
            dpg.configure_item("video_opts", show=False)
        else:
            dpg.configure_item("download_btn", label="Download Video")
            dpg.configure_item("audio_opts", show=False)
            dpg.configure_item("video_opts", show=True)

    def on_main_window_resize(self, sender, app_data, user_data):
        """Resize anchored controls to fit the `main_window` width."""
        # Calculate content width with padding
        padding = self.window_padding
        browse_button_width = 100
        spacing = 10

        width, height = dpg.get_item_rect_size("main_window")
        if not width:
            return
        content_width = max(100, width - 2 * padding)

        # Full-width elements
        for item in ("url_input", "progress_bar", "log_text", "download_btn"):
            if dpg.does_item_exist(item):
                dpg.configure_item(item, width=content_width)

        # Child windows for transcript and summary
        for item in ("transcript_window", "summary_window"):
            if dpg.does_item_exist(item):
                dpg.configure_item(item, width=content_width)
                # Update wrap width for text inside
                text_tag = item.replace("_window", "_text")
                if dpg.does_item_exist(text_tag):
                    dpg.configure_item(text_tag, wrap=content_width - 20)  # Reduced padding for more text space

        # Destination row: input takes remaining space beside fixed Browse button
        dest_input_width = max(100, content_width - browse_button_width - spacing)
        if dpg.does_item_exist("dest_input"):
            dpg.configure_item("dest_input", width=dest_input_width)

        # Calculate available space for log and transcript areas
        # Compute space used by content group above logs
        content_top_left = dpg.get_item_rect_min("content_group")
        content_bottom_right = dpg.get_item_rect_max("content_group")
        content_height = 0
        if content_top_left and content_bottom_right:
            content_height = content_bottom_right[1] - content_top_left[1]

        # Get label heights for all three areas
        log_label_h = 0
        transcript_label_h = 0
        summary_label_h = 0
        if dpg.does_item_exist("log_label"):
            _, log_label_h = dpg.get_item_rect_size("log_label")
        if dpg.does_item_exist("transcript_label"):
            _, transcript_label_h = dpg.get_item_rect_size("transcript_label")
        if dpg.does_item_exist("summary_label"):
            _, summary_label_h = dpg.get_item_rect_size("summary_label")

        # Calculate available height for all three text areas
        # Account for padding, content, labels, and spacing between elements
        total_label_height = log_label_h + transcript_label_h + summary_label_h
        total_spacing = 6 * self.vertical_spacing  # spacing around and between elements
        available_height = max(0, height - 2 * padding - content_height - total_label_height - total_spacing)

        # Distribute available height evenly among transcript, summary, and log
        # Each gets one third of the available space, constrained by min/max limits
        third_available = available_height / 3
        min_height = 80
        # Max can be infinite
        max_height = float('inf')

        # Calculate target heights with constraints
        target_height = max(min_height, min(max_height, third_available))

        # Apply heights to all three areas (child windows and log text)
        if dpg.does_item_exist("transcript_window"):
            dpg.configure_item("transcript_window", height=int(target_height))
        if dpg.does_item_exist("summary_window"):
            dpg.configure_item("summary_window", height=int(target_height))
        if dpg.does_item_exist("log_text"):
            dpg.configure_item("log_text", height=int(target_height))

    def browse_destination(self):
        """Open directory chooser to avoid manual path entry"""
        dpg.show_item("dir_dialog")

    def on_directory_selected(self, sender, app_data):
        """Capture chosen directory from dialog callback"""
        selected_path = app_data.get("file_path_name") or app_data.get("current_path")
        if selected_path:
            dpg.set_value("dest_input", selected_path)

    def sanitize_filename(self, filename):
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

    def extract_youtube_video_id(self, youtube_url):
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

    def fetch_transcript(self, url):
        """Fetch transcript for YouTube video"""
        video_id = self.extract_youtube_video_id(url)
        if not video_id:
            return None, "Not a valid YouTube URL"

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
            return transcript_text, None
        except Exception as e:
            return None, f"Transcript not available: {str(e)}"

    def get_clean_transcript_text(self, transcript_text):
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

    def get_summarizer(self):
        """Initialize and return the summarizer (lazy loading)"""
        if self.summarizer is None:
            try:
                # Suppress warnings from transformers
                warnings.filterwarnings("ignore", category=UserWarning)
                self.log_message("Loading summarization model (first time only)...")
                self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
                self.log_message("Summarization model loaded successfully!")
            except Exception as e:
                self.log_message(f"ERROR: Failed to load summarization model: {str(e)}")
                return None
        return self.summarizer

    def chunk_text(self, text, max_chunk_size=1000):
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

    def summarize_transcript(self, transcript_text):
        """Generate summary from transcript text"""
        if not transcript_text:
            return None, "No transcript available to summarize"

        try:
            summarizer = self.get_summarizer()
            if not summarizer:
                return None, "Summarization model not available"

            # Remove timestamps and clean text for better summarization
            # Remove various timestamp formats: [MM:SS], [HH:MM:SS], (MM:SS), etc.
            clean_text = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*', '', transcript_text)
            # Remove any remaining brackets or parentheses that might contain timestamps
            clean_text = re.sub(r'\[\s*\]\s*', '', clean_text)
            # Clean up multiple spaces and newlines
            clean_text = re.sub(r'\s+', ' ', clean_text)
            clean_text = clean_text.strip()

            if len(clean_text) < 50:
                return None, "Transcript too short to summarize"

            # Handle long transcripts by chunking
            if len(clean_text) > 1000:
                self.log_message("Transcript is long, processing in chunks...")
                chunks = self.chunk_text(clean_text, max_chunk_size=1000)
                chunk_summaries = []

                for i, chunk in enumerate(chunks):
                    if len(chunk) < 50:  # Skip very short chunks
                        continue
                    try:
                        # Adaptive max_length based on chunk size
                        chunk_max_length = min(100, max(30, len(chunk) // 4))
                        summary = summarizer(chunk, max_length=chunk_max_length, min_length=20, do_sample=False)
                        chunk_summaries.append(summary[0]['summary_text'])
                        self.log_message(f"Processed chunk {i+1}/{len(chunks)}")
                    except Exception as e:
                        self.log_message(f"Warning: Failed to summarize chunk {i+1}: {str(e)}")
                        continue

                if chunk_summaries:
                    # Combine chunk summaries
                    combined_summary = ' '.join(chunk_summaries)
                    # If combined summary is still too long, summarize it again
                    if len(combined_summary) > 1000:
                        final_max_length = min(200, max(50, len(combined_summary) // 3))
                        final_summary = summarizer(combined_summary, max_length=final_max_length, min_length=50, do_sample=False)
                        return final_summary[0]['summary_text'], None
                    else:
                        return combined_summary, None
                else:
                    return None, "Failed to generate summary from chunks"
            else:
                # Short transcript, summarize directly with adaptive length
                text_max_length = min(150, max(30, len(clean_text) // 3))
                summary = summarizer(clean_text, max_length=text_max_length, min_length=20, do_sample=False)
                return summary[0]['summary_text'], None

        except Exception as e:
            return None, f"Summarization failed: {str(e)}"

    def save_transcript_to_file(self, transcript_text, media_filename, destination):
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

            return transcript_path
        except Exception as e:
            self.log_message(f"ERROR: Failed to save transcript: {str(e)}")
            return None

    def save_summary_to_file(self, summary_text, media_filename, destination):
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

            return summary_path
        except Exception as e:
            self.log_message(f"ERROR: Failed to save summary: {str(e)}")
            return None

    def log_message(self, message):
        """Add message to log text area"""
        current_log = dpg.get_value("log_text")
        timestamp = time.strftime("%H:%M:%S")
        if current_log:
            new_log = f"{current_log}\n[{timestamp}] {message}"
        else:
            new_log = f"[{timestamp}] {message}"
        dpg.set_value("log_text", new_log)

    def update_status(self, message, color=(255, 255, 255)):
        """Update status text with color"""
        dpg.set_value("status_text", message)
        dpg.configure_item("status_text", color=color)

    def update_progress(self, value):
        """Update progress bar"""
        dpg.set_value("progress_bar", value)

    def start_download(self):
        """Start download in a separate thread"""
        if self.is_downloading:
            self.log_message("ERROR: A download is already in progress.")
            return

        url = dpg.get_value("url_input").strip()
        destination = dpg.get_value("dest_input").strip()
        download_type = dpg.get_value("download_type")

        if not url:
            self.log_message("ERROR: Please enter a video URL.")
            self.update_status("Error: No URL provided", (255, 100, 100))
            return

        if not destination:
            self.log_message("ERROR: Please select a destination folder.")
            self.update_status("Error: No destination provided", (255, 100, 100))
            return

        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                self.log_message(f"Created destination directory: {destination}")
            except Exception as e:
                self.log_message(f"ERROR: Failed to create destination directory: {str(e)}")
                self.update_status("Error: Cannot create directory", (255, 100, 100))
                return

        # Get transcript and summary options
        transcript_enabled = dpg.get_value("transcript_enabled")
        summary_enabled = dpg.get_value("summary_enabled")

        # Disable UI elements during download
        dpg.configure_item("download_btn", enabled=False)
        dpg.configure_item("url_input", enabled=False)
        dpg.configure_item("dest_input", enabled=False)
        dpg.configure_item("download_type", enabled=False)
        dpg.configure_item("audio_quality", enabled=False)
        dpg.configure_item("video_quality", enabled=False)
        dpg.configure_item("transcript_enabled", enabled=False)
        dpg.configure_item("summary_enabled", enabled=False)

        # Clear log, transcript, and summary, start progress
        dpg.set_value("log_text", "")
        dpg.set_value("transcript_text", "Transcript will appear here when available...")
        dpg.configure_item("transcript_text", color=(150, 150, 150))  # Gray hint color
        dpg.set_value("summary_text", "Summary will appear here when generated...")
        dpg.configure_item("summary_text", color=(150, 150, 150))  # Gray hint color
        self.update_status("Downloading...", (0, 255, 0))
        self.update_progress(0.1)
        self.is_downloading = True

        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_media,
            args=(url, destination, download_type, transcript_enabled, summary_enabled)
        )
        self.download_thread.daemon = True
        self.download_thread.start()

    def progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = d['downloaded_bytes'] / d['total_bytes']
                self.update_progress(0.3 + (percent * 0.6))  # 30-90% for download
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f" at {speed/1024/1024:.1f} MB/s"
                else:
                    speed_str = ""
                self.log_message(f"Downloaded {percent*100:.1f}%{speed_str}")
        elif d['status'] == 'finished':
            self.update_progress(0.9)
            self.log_message(f"Finished downloading: {d['filename']}")

    def download_media(self, video_url, destination, download_type, transcript_enabled=False, summary_enabled=False):
        """Download media from video URL"""
        transcript_text = None
        summary_text = None
        media_filename = None

        try:
            self.log_message(f"Starting {download_type} download from: {video_url}")
            self.log_message(f"Destination: {destination}")
            self.update_progress(0.1)

            # Fetch transcript if enabled and it's a YouTube URL
            if transcript_enabled:
                self.log_message("Fetching transcript...")
                transcript_text, transcript_error = self.fetch_transcript(video_url)
                if transcript_text:
                    self.log_message("Transcript fetched successfully!")
                    dpg.set_value("transcript_text", transcript_text)
                    dpg.configure_item("transcript_text", color=(255, 255, 255))  # White text for content

                    # Generate summary if enabled and transcript is available
                    if summary_enabled:
                        self.log_message("Generating summary...")
                        summary_text, summary_error = self.summarize_transcript(transcript_text)
                        if summary_text:
                            self.log_message("Summary generated successfully!")
                            dpg.set_value("summary_text", summary_text)
                            dpg.configure_item("summary_text", color=(255, 255, 255))  # White text for content
                        elif summary_error:
                            self.log_message(f"Summary: {summary_error}")
                            dpg.set_value("summary_text", f"Summary not available: {summary_error}")
                            dpg.configure_item("summary_text", color=(255, 150, 150))  # Light red for error
                elif transcript_error:
                    self.log_message(f"Transcript: {transcript_error}")
                    dpg.set_value("transcript_text", f"Transcript not available: {transcript_error}")
                    dpg.configure_item("transcript_text", color=(255, 150, 150))  # Light red for error
                    if summary_enabled:
                        dpg.set_value("summary_text", "Summary not available: No transcript")
                        dpg.configure_item("summary_text", color=(255, 150, 150))  # Light red for error

                progress_increment = 0.15 if summary_enabled else 0.1
                self.update_progress(0.1 + progress_increment)

            # Common options to avoid 403 errors
            common_opts = {
                'outtmpl': os.path.join(destination, '%(title).200s.%(ext)s'),  # Limit title length
                'progress_hooks': [self.progress_hook],
                # Headers to avoid bot detection
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                # Retry settings
                'retries': 3,
                'fragment_retries': 3,
                'extractor_retries': 3,
                # Other options
                'ignoreerrors': False,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                # Filename sanitization options
                'restrictfilenames': True,  # Use ASCII characters only
                'windowsfilenames': True,   # Ensure Windows compatibility
                'trim_filenames': 200,      # Limit filename length
            }

            # Set base progress based on whether transcript and summary were processed
            if transcript_enabled and summary_enabled:
                base_progress = 0.25
            elif transcript_enabled:
                base_progress = 0.15
            else:
                base_progress = 0.1

            if download_type == "Audio (MP3)":
                ydl_opts = {
                    **common_opts,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': dpg.get_value("audio_quality"),
                    }],
                }
            else:  # video
                quality = dpg.get_value("video_quality")
                if quality == "best":
                    format_str = "bestvideo+bestaudio/best"
                elif quality == "worst":
                    format_str = "worstvideo+worstaudio/worst"
                else:
                    # For specific resolutions
                    height = quality[:-1]  # Remove 'p'
                    format_str = f"bestvideo[height<={height}]+bestaudio/best"

                ydl_opts = {
                    **common_opts,
                    'format': format_str,
                }

            self.update_progress(base_progress + 0.05)
            self.log_message("Fetching video information...")

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                self.log_message("Extracting video metadata...")
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')

                self.log_message(f"Title: {title}")
                self.log_message(f"Uploader: {uploader}")
                if duration:
                    # duration may be float from extractor; normalize to int seconds to avoid format errors
                    total_seconds = int(round(duration))
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if hours:
                        self.log_message(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")
                    else:
                        self.log_message(f"Duration: {minutes}:{seconds:02d}")

                # Store the expected filename for transcript saving (sanitized)
                sanitized_title = self.sanitize_filename(title)
                if download_type == "Audio (MP3)":
                    media_filename = f"{sanitized_title}.mp3"
                else:
                    media_filename = f"{sanitized_title}.webm"

                self.update_progress(base_progress + 0.15)

                # Download the media
                if download_type == "Audio (MP3)":
                    self.log_message("Starting audio download and MP3 conversion...")
                else:
                    self.log_message(f"Starting video download in {quality} quality...")

                ydl.download([video_url])

            # Save transcript to file if available
            if transcript_enabled and transcript_text and media_filename:
                self.log_message("Saving transcript to file...")
                transcript_path = self.save_transcript_to_file(transcript_text, media_filename, destination)
                if transcript_path:
                    self.log_message(f"Transcript saved to: {os.path.basename(transcript_path)}")

            # Save summary to file if available
            if summary_enabled and summary_text and media_filename:
                self.log_message("Saving summary to file...")
                summary_path = self.save_summary_to_file(summary_text, media_filename, destination)
                if summary_path:
                    self.log_message(f"Summary saved to: {os.path.basename(summary_path)}")

            self.update_progress(1.0)
            self.log_message("Download completed successfully!")
            media_type = "MP3" if download_type == "Audio (MP3)" else "Video"
            success_msg = f"Success: {media_type} downloaded!"
            if transcript_enabled and transcript_text:
                success_msg += " (with transcript"
                if summary_enabled and summary_text:
                    success_msg += " and summary"
                success_msg += ")"
            self.update_status(success_msg, (0, 255, 0))

        except youtube_dl.DownloadError as e:
            error_msg = f"Download error: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.update_status("Download failed", (255, 100, 100))

            # Provide helpful suggestions
            if "403" in str(e) or "Forbidden" in str(e):
                self.log_message("SUGGESTION: This might be a region-blocked video or YouTube is blocking requests.")
                self.log_message("Try: 1) Different video 2) Wait a few minutes 3) Use VPN if region-blocked")
            elif "404" in str(e):
                self.log_message("SUGGESTION: Video not found. Check if the URL is correct and video exists.")
            elif "Private video" in str(e):
                self.log_message("SUGGESTION: This is a private video. Only the owner can download it.")

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.update_status("Download failed", (255, 100, 100))

        finally:
            # Re-enable UI elements
            dpg.configure_item("download_btn", enabled=True)
            dpg.configure_item("url_input", enabled=True)
            dpg.configure_item("dest_input", enabled=True)
            dpg.configure_item("download_type", enabled=True)
            dpg.configure_item("audio_quality", enabled=True)
            dpg.configure_item("video_quality", enabled=True)
            dpg.configure_item("transcript_enabled", enabled=True)
            dpg.configure_item("summary_enabled", enabled=True)
            self.is_downloading = False

    def run(self):
        """Start the GUI application"""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

def main():
    app = MediaDownloaderGUI()
    app.run()

if __name__ == "__main__":
    main()
