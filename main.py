"""
Media Downloader - Main Entry Point
Clean architecture with separated concerns following SOLID principles.
"""

from gui.media_downloader_gui import main as gui_main

def main():
    """Main entry point for Media Downloader application"""
    gui_main()

if __name__ == "__main__":
    main()
