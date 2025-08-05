#!/usr/bin/env python3
"""
Simple build script for MP3 Downloader executable
Uses pyproject.toml configuration
"""

import subprocess
import sys
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    build_dirs = ['build', 'dist', '__pycache__']
    spec_files = Path('.').glob('*.spec')

    for dir_name in build_dirs:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ Cleaned {dir_name}/")

    for spec_file in spec_files:
        spec_file.unlink()
        print(f"✓ Removed {spec_file}")

def build_executable():
    """Build executable using PyInstaller with project configuration"""
    print("Building MP3 Downloader executable...")
    
    # PyInstaller command with comprehensive yt-dlp inclusion
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name=Media_Downloader",
        "--collect-all=yt_dlp",
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--hidden-import=yt_dlp.extractor.youtube",
        "--hidden-import=yt_dlp.downloader",
        "--hidden-import=yt_dlp.downloader.http",
        "--hidden-import=yt_dlp.postprocessor",
        "--hidden-import=yt_dlp.postprocessor.ffmpeg",
        "--hidden-import=yt_dlp.utils",
        "--hidden-import=yt_dlp.version",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk", 
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--clean",
        "main.py"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build successful!")

        exe_path = Path("dist/Media_Downloader.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ Executable created: {exe_path}")
            print(f"✓ Size: {size_mb:.1f} MB")
            return True
        else:
            print("✗ Executable not found after build")
            return False

    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("=== MP3 Downloader Build Script ===\n")

    # Check if PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"],
                      check=True, capture_output=True)
        print("✓ PyInstaller is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                          check=True)
            print("✓ PyInstaller installed")
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

    # Clean and build
    clean_build()
    success = build_executable()

    if success:
        print("\n=== Build Complete ===")
        print("Run the executable: dist/Media_Downloader.exe")

    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)