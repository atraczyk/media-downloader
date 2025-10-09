# Media Downloader

A modern GUI application for downloading audio and video from YouTube videos. Supports MP3 audio conversion and various video quality options.

## Features

- 🎵 Download audio from YouTube videos (MP3)
- 🎬 Download videos in various qualities
- 🎨 Modern Dear PyGui interface
- 📁 Easy destination folder selection
- 📊 Real-time progress tracking
- 🔄 Background download processing
- ✅ Automatic MP3 conversion
- 🎛️ Quality selection options
- 🛡️ Error handling and validation

## Requirements

- Python 3.7 or higher
- FFmpeg (for audio conversion)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   - **Windows:** Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Usage

### Running the Python Script
```bash
python main.py
```

### Creating a Self-Contained Executable

**Single command to build:**
```bash
python build.py
```

**Find your executable:**
- Location: `dist/Media_Downloader.exe`
- Double-click to run

## How to Use

1. **Enter Video URL:** Paste a YouTube video URL in the input field
2. **Choose Download Type:** Select Audio (MP3) or Video
3. **Set Quality:** Choose audio quality (128-320 kbps) or video quality (720p-4K)
4. **Select Destination:** Click "Browse" to choose where to save the file
5. **Download:** Click "Download" to start the process
6. **Monitor Progress:** Watch the status area for download progress
7. **Complete:** Get notified when the download finishes

## Supported Platforms

- ✅ Windows (with executable)
- ✅ macOS
- ✅ Linux

## Troubleshooting

### Common Issues

1. **FFmpeg not found:**
   - Ensure FFmpeg is installed and in your system PATH
   - For Windows, restart your terminal after adding FFmpeg to PATH

2. **Download fails:**
   - Check your internet connection
   - Verify the video URL is valid and accessible
   - Some videos may have download restrictions

3. **Executable not working:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Try running the Python script directly first: `python main.py`

### Build Issues

If the executable build fails:

1. **Clean and retry:**
   ```bash
   # Remove build artifacts
   rmdir /s build dist
   del Media_Downloader.spec

   # Reinstall PyInstaller
   pip uninstall pyinstaller
   pip install pyinstaller

   # Try building again
   python build.py
   ```

2. **Manual PyInstaller command:**
   ```bash
   pyinstaller --onefile --windowed --name=Media_Downloader main.py
   ```

## File Structure

```
mp3_dl/
├── main.py              # Main application
├── build.py             # Build script for executable
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── dist/               # Generated executable (after build)
    └── Media_Downloader.exe
```

## License

This project is open source. Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request