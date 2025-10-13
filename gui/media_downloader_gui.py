"""
GUI implementation for Media Downloader.
Follows Single Responsibility Principle (SRP) - handles only presentation logic.
Depends on backend abstractions, not concrete implementations - Dependency Inversion Principle.
"""

import dearpygui.dearpygui as dpg
import os
from pathlib import Path

from backend import (
    MediaDownloaderFacade, DownloadRequest, DownloadProgress,
    DownloadStatus, DownloadType, TranscriptResult, SummaryResult
)


class MediaDownloaderGUI:
    """
    GUI class that handles only presentation logic.
    Business logic is delegated to the backend facade.
    """

    def __init__(self):
        """Initialize GUI with backend facade"""
        self.facade = MediaDownloaderFacade()

        # GUI state
        self.window_padding = 15
        self.vertical_spacing = 6

        # Set up logging callback
        self.facade.update_log_callback(self._handle_log_message)

        self.setup_gui()

    def setup_gui(self):
        """Set up the DearPyGui interface"""
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
            no_scrollbar=True,  # Disable scrollbar to prevent overflow
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
                        callback=self._on_type_change
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
                        label="Browse", callback=self._browse_destination, width=100
                    )

                # Download button
                dpg.add_separator()
                dpg.add_button(
                    label="Download MP3",
                    tag="download_btn",
                    callback=self._start_download,
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
                    wrap=740,
                    color=(150, 150, 150)
                )

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
                    wrap=740,
                    color=(150, 150, 150)
                )

            # Status log
            dpg.add_text("Log:", tag="log_label")
            dpg.add_input_text(
                tag="log_text",
                multiline=True,
                readonly=True,
                height=80,
                width=760,
            )

        # Folder chooser for destination selection
        with dpg.file_dialog(directory_selector=True, show=False, callback=self._on_directory_selected, tag="dir_dialog"):
            pass

        # Set up themes and handlers
        self._setup_themes()
        self._setup_handlers()

        # Ensure the main window fills and follows the viewport
        dpg.set_primary_window("main_window", True)

        # Perform initial layout sizing
        self._on_main_window_resize(None, None, None)

    def _setup_themes(self):
        """Set up DearPyGui themes"""
        # Main window theme
        with dpg.theme(tag="main_window_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(
                    dpg.mvStyleVar_WindowPadding,
                    self.window_padding,
                    self.window_padding,
                )
        dpg.bind_item_theme("main_window", "main_window_theme")

        # Child window theme
        with dpg.theme(tag="child_window_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)

        dpg.bind_item_theme("transcript_window", "child_window_theme")
        dpg.bind_item_theme("summary_window", "child_window_theme")

    def _setup_handlers(self):
        """Set up event handlers"""
        with dpg.item_handler_registry(tag="main_window_handlers"):
            dpg.add_item_resize_handler(callback=self._on_main_window_resize)
        dpg.bind_item_handler_registry("main_window", "main_window_handlers")

    def _on_type_change(self, sender, app_data):
        """Handle download type change"""
        if app_data == "Audio (MP3)":
            dpg.configure_item("download_btn", label="Download MP3")
            dpg.configure_item("audio_opts", show=True)
            dpg.configure_item("video_opts", show=False)
        else:
            dpg.configure_item("download_btn", label="Download Video")
            dpg.configure_item("audio_opts", show=False)
            dpg.configure_item("video_opts", show=True)

    def _on_main_window_resize(self, sender, app_data, user_data):
        """Resize anchored controls to fit the main_window width"""
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
                text_tag = item.replace("_window", "_text")
                if dpg.does_item_exist(text_tag):
                    dpg.configure_item(text_tag, wrap=content_width - 20)

        # Destination row
        dest_input_width = max(100, content_width - browse_button_width - spacing)
        if dpg.does_item_exist("dest_input"):
            dpg.configure_item("dest_input", width=dest_input_width)

        # Calculate and distribute heights for text areas
        self._calculate_text_area_heights(height, content_width)

    def _calculate_text_area_heights(self, window_height, content_width):
        """Calculate and set heights for transcript, summary, and log areas"""
        content_top_left = dpg.get_item_rect_min("content_group")
        content_bottom_right = dpg.get_item_rect_max("content_group")
        content_height = 0
        if content_top_left and content_bottom_right:
            content_height = content_bottom_right[1] - content_top_left[1]

        # Get label heights
        label_heights = 0
        for label in ["log_label", "transcript_label", "summary_label"]:
            if dpg.does_item_exist(label):
                _, h = dpg.get_item_rect_size(label)
                if h:
                    label_heights += h

        # More conservative calculation to prevent overflow
        # Account for: window padding, content height, labels, separators, and extra spacing
        reserved_height = (
            2 * self.window_padding +  # Top and bottom padding
            content_height +           # All content above text areas
            label_heights +           # Label heights
            80                        # Extra buffer for separators, spacing, and safety margin
        )

        available_height = max(0, window_height - reserved_height)

        # Distribute height evenly among three areas with smaller minimum
        # Use smaller minimum and cap maximum to prevent overflow
        target_height = max(50, min(120, available_height / 3))  # Min 50, max 120 per area

        # Apply heights
        for item in ["transcript_window", "summary_window", "log_text"]:
            if dpg.does_item_exist(item):
                dpg.configure_item(item, height=int(target_height))

    def _browse_destination(self):
        """Open directory chooser"""
        dpg.show_item("dir_dialog")

    def _on_directory_selected(self, sender, app_data):
        """Handle directory selection"""
        selected_path = app_data.get("file_path_name") or app_data.get("current_path")
        if selected_path:
            dpg.set_value("dest_input", selected_path)

    def _start_download(self):
        """Start download using backend facade"""
        if self.facade.is_downloading():
            self._handle_log_message("ERROR: A download is already in progress.")
            return

        # Validate inputs
        url = dpg.get_value("url_input").strip()
        destination = dpg.get_value("dest_input").strip()
        download_type_str = dpg.get_value("download_type")

        if not url:
            self._handle_log_message("ERROR: Please enter a video URL.")
            self._update_status("Error: No URL provided", (255, 100, 100))
            return

        if not destination:
            self._handle_log_message("ERROR: Please select a destination folder.")
            self._update_status("Error: No destination provided", (255, 100, 100))
            return

        # Create download request
        download_type = DownloadType.AUDIO_MP3 if download_type_str == "Audio (MP3)" else DownloadType.VIDEO_WEBM

        request = DownloadRequest(
            url=url,
            destination=destination,
            download_type=download_type,
            audio_quality=dpg.get_value("audio_quality"),
            video_quality=dpg.get_value("video_quality"),
            transcript_enabled=dpg.get_value("transcript_enabled"),
            summary_enabled=dpg.get_value("summary_enabled")
        )

        # Disable UI during download
        self._set_ui_enabled(False)

        # Clear previous results
        self._clear_results()

        # Start download
        success = self.facade.download_media_async(
            request=request,
            progress_callback=self._handle_progress,
            transcript_callback=self._handle_transcript,
            summary_callback=self._handle_summary,
            completion_callback=self._handle_completion
        )

        if not success:
            self._handle_log_message("ERROR: Failed to start download.")
            self._set_ui_enabled(True)

    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        ui_elements = [
            "download_btn", "url_input", "dest_input", "download_type",
            "audio_quality", "video_quality", "transcript_enabled", "summary_enabled"
        ]

        for element in ui_elements:
            if dpg.does_item_exist(element):
                dpg.configure_item(element, enabled=enabled)

    def _clear_results(self):
        """Clear previous results"""
        dpg.set_value("log_text", "")
        dpg.set_value("transcript_text", "Transcript will appear here when available...")
        dpg.configure_item("transcript_text", color=(150, 150, 150))
        dpg.set_value("summary_text", "Summary will appear here when generated...")
        dpg.configure_item("summary_text", color=(150, 150, 150))
        self._update_status("Downloading...", (0, 255, 0))
        dpg.set_value("progress_bar", 0.1)

    def _handle_log_message(self, message: str):
        """Handle log messages from backend"""
        current_log = dpg.get_value("log_text")
        if current_log:
            new_log = f"{current_log}\n{message}"
        else:
            new_log = message
        dpg.set_value("log_text", new_log)

    def _handle_progress(self, progress: DownloadProgress):
        """Handle progress updates from backend"""
        dpg.set_value("progress_bar", progress.progress)

        # Update status based on progress status
        if progress.status == DownloadStatus.DOWNLOADING:
            self._update_status(progress.message, (0, 255, 255))  # Cyan for downloading
        elif progress.status == DownloadStatus.PROCESSING:
            self._update_status(progress.message, (255, 255, 0))  # Yellow for processing
        elif progress.status == DownloadStatus.COMPLETED:
            self._update_status(progress.message, (0, 255, 0))    # Green for completed
        elif progress.status == DownloadStatus.FAILED:
            self._update_status(progress.message, (255, 100, 100))  # Red for failed
        else:
            self._update_status(progress.message, (255, 255, 255))  # White for other

    def _handle_transcript(self, result: TranscriptResult):
        """Handle transcript results from backend"""
        if result.text:
            dpg.set_value("transcript_text", result.text)
            dpg.configure_item("transcript_text", color=(255, 255, 255))
        elif result.error:
            dpg.set_value("transcript_text", f"Transcript not available: {result.error}")
            dpg.configure_item("transcript_text", color=(255, 150, 150))

    def _handle_summary(self, result: SummaryResult):
        """Handle summary results from backend"""
        if result.summary:
            dpg.set_value("summary_text", result.summary)
            dpg.configure_item("summary_text", color=(255, 255, 255))
        elif result.error:
            dpg.set_value("summary_text", f"Summary not available: {result.error}")
            dpg.configure_item("summary_text", color=(255, 150, 150))

    def _handle_completion(self, success: bool, message: str, filename: str):
        """Handle download completion from backend"""
        self._set_ui_enabled(True)

        if success:
            # Build success message
            download_type_str = dpg.get_value("download_type")
            media_type = "MP3" if download_type_str == "Audio (MP3)" else "Video"
            success_msg = f"Success: {media_type} downloaded!"

            # Add transcript/summary info if applicable
            if dpg.get_value("transcript_enabled"):
                transcript_text = dpg.get_value("transcript_text")
                if transcript_text and not transcript_text.startswith("Transcript not available"):
                    success_msg += " (with transcript"
                    if dpg.get_value("summary_enabled"):
                        summary_text = dpg.get_value("summary_text")
                        if summary_text and not summary_text.startswith("Summary not available"):
                            success_msg += " and summary"
                    success_msg += ")"

            self._update_status(success_msg, (0, 255, 0))
        else:
            self._update_status("Download failed", (255, 100, 100))

    def _update_status(self, message: str, color=(255, 255, 255)):
        """Update status text with color"""
        dpg.set_value("status_text", message)
        dpg.configure_item("status_text", color=color)

    def run(self):
        """Start the GUI application"""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main entry point"""
    app = MediaDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()
