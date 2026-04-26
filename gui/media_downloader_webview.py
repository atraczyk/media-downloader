"""
WebView-based GUI implementation for Media Downloader.
Follows Single Responsibility Principle (SRP) - handles only presentation logic.
Depends on backend abstractions, not concrete implementations - Dependency Inversion Principle.
"""

import webview

from .webview_api import MediaDownloaderAPI
from .html_interface import create_html_interface


class MediaDownloaderWebViewGUI:
    """
    WebView-based GUI class that handles presentation logic.
    Business logic is delegated to the backend facade through the API.
    """

    def __init__(self):
        """Initialize WebView GUI"""
        self.api = MediaDownloaderAPI()
        self.window = None


    def run(self):
        """Start the WebView GUI application"""
        html_content = create_html_interface()

        # Create webview window
        self.window = webview.create_window(
            title="Media Downloader",
            html=html_content,
            js_api=self.api,
            width=1000,
            height=800,
            resizable=True,
            on_top=False,
            shadow=True
        )

        # Set window reference in API for callbacks
        self.api.set_window(self.window)

        # Start webview
        webview.start(debug=False)


def main():
    """Main entry point"""
    app = MediaDownloaderWebViewGUI()
    app.run()


if __name__ == "__main__":
    main()
