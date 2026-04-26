"""
Media Downloader - Main Entry Point
Clean architecture with separated concerns following SOLID principles.
"""

from gui.media_downloader_webview import main as webview_gui_main

def main():
    """Main entry point for Media Downloader application"""
    webview_gui_main()

if __name__ == "__main__":
    main()
