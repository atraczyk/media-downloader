import yt_dlp as youtube_dl
import os
import dearpygui.dearpygui as dpg
import threading
from pathlib import Path
import time

class MediaDownloaderGUI:
    def __init__(self):
        self.download_thread = None
        self.is_downloading = False
        # Consistent left/right and top/bottom padding inside main window
        self.window_padding = 20
        # Minimum height for logs anchored to the bottom
        self.log_min_height = 180
        # Vertical spacing used in height calculations
        self.vertical_spacing = 10
        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title="Media Downloader", width=800, height=700)
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
                # Title
                dpg.add_text("Media Downloader", color=(0, 150, 255))
                dpg.add_separator()

                # URL input
                dpg.add_text("Video URL:")
                dpg.add_input_text(
                    tag="url_input", hint="Enter video URL here...", width=760
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

            # Status log
            dpg.add_text("Log:", tag="log_label")
            dpg.add_input_text(
                tag="log_text",
                multiline=True,
                readonly=True,
                height=260,
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

        # Destination row: input takes remaining space beside fixed Browse button
        dest_input_width = max(100, content_width - browse_button_width - spacing)
        if dpg.does_item_exist("dest_input"):
            dpg.configure_item("dest_input", width=dest_input_width)

        # Anchor logs to bottom with minimum height
        # Compute space used by content group above logs
        content_top_left = dpg.get_item_rect_min("content_group")
        content_bottom_right = dpg.get_item_rect_max("content_group")
        content_height = 0
        if content_top_left and content_bottom_right:
            content_height = content_bottom_right[1] - content_top_left[1]

        # Available vertical space for logs block inside padded window
        # Subtract the label's height and spacing to avoid overflow
        label_w, label_h = (0, 0)
        if dpg.does_item_exist("log_label"):
            label_w, label_h = dpg.get_item_rect_size("log_label")

        available_height = max(0, height - 2 * padding - content_height)
        space_for_log_text = max(0, available_height - label_h - (2 * self.vertical_spacing))
        target_log_height = max(self.log_min_height, space_for_log_text)
        if dpg.does_item_exist("log_text") and target_log_height:
            dpg.configure_item("log_text", height=int(target_log_height))

    def browse_destination(self):
        """Open directory chooser to avoid manual path entry"""
        dpg.show_item("dir_dialog")

    def on_directory_selected(self, sender, app_data):
        """Capture chosen directory from dialog callback"""
        selected_path = app_data.get("file_path_name") or app_data.get("current_path")
        if selected_path:
            dpg.set_value("dest_input", selected_path)

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

        # Disable UI elements during download
        dpg.configure_item("download_btn", enabled=False)
        dpg.configure_item("url_input", enabled=False)
        dpg.configure_item("dest_input", enabled=False)
        dpg.configure_item("download_type", enabled=False)
        dpg.configure_item("audio_quality", enabled=False)
        dpg.configure_item("video_quality", enabled=False)

        # Clear log and start progress
        dpg.set_value("log_text", "")
        self.update_status("Downloading...", (0, 255, 0))
        self.update_progress(0.1)
        self.is_downloading = True

        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_media,
            args=(url, destination, download_type)
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

    def download_media(self, video_url, destination, download_type):
        """Download media from video URL"""
        try:
            self.log_message(f"Starting {download_type} download from: {video_url}")
            self.log_message(f"Destination: {destination}")
            self.update_progress(0.1)

            # Common options to avoid 403 errors
            common_opts = {
                'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
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
            }

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

            self.update_progress(0.2)
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

                self.update_progress(0.3)

                # Download the media
                if download_type == "Audio (MP3)":
                    self.log_message("Starting audio download and MP3 conversion...")
                else:
                    self.log_message(f"Starting video download in {quality} quality...")

                ydl.download([video_url])

            self.update_progress(1.0)
            self.log_message("Download completed successfully!")
            media_type = "MP3" if download_type == "Audio (MP3)" else "Video"
            self.update_status(f"Success: {media_type} downloaded!", (0, 255, 0))

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
