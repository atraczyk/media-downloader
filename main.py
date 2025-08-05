import yt_dlp as youtube_dl
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

class MediaDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Downloader")
        self.root.geometry("500x600")
        self.root.resizable(True, True)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        self.setup_ui()
        self.download_thread = None

    def setup_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Media Downloader",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # URL input
        ttk.Label(main_frame, text="Video URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Download type selection
        ttk.Label(main_frame, text="Download Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.download_type = tk.StringVar(value="audio")
        audio_radio = ttk.Radiobutton(main_frame, text="Audio (MP3)", variable=self.download_type,
                                     value="audio", command=self.on_type_change)
        video_radio = ttk.Radiobutton(main_frame, text="Video (WebM)", variable=self.download_type,
                                     value="video", command=self.on_type_change)
        audio_radio.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        video_radio.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))

        # Format selection frame
        self.format_frame = ttk.LabelFrame(main_frame, text="Format Options", padding="10")
        self.format_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Audio quality selection
        ttk.Label(self.format_frame, text="Audio Quality:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.audio_quality = tk.StringVar(value="192")
        audio_combo = ttk.Combobox(self.format_frame, textvariable=self.audio_quality,
                                  values=["128", "192", "256", "320"], width=10, state="readonly")
        audio_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        # Video quality selection
        ttk.Label(self.format_frame, text="Video Quality:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.video_quality = tk.StringVar(value="best")
        video_combo = ttk.Combobox(self.format_frame, textvariable=self.video_quality,
                                  values=["best", "worst", "720p", "1080p", "1440p", "2160p"],
                                  width=10, state="readonly")
        video_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        # Destination selection
        ttk.Label(main_frame, text="Save to:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.dest_var = tk.StringVar(value=str(Path.cwd() / "downloads"))
        self.dest_entry = ttk.Entry(main_frame, textvariable=self.dest_var, width=40)
        self.dest_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 10))

        self.browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_destination)
        self.browse_btn.grid(row=4, column=2, pady=5)

        # Download button
        self.download_btn = ttk.Button(main_frame, text="Download",
                                      command=self.start_download, style='Accent.TButton')
        self.download_btn.grid(row=5, column=0, columnspan=3, pady=20)

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to download")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=6, column=0, columnspan=3, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        # Status text area
        ttk.Label(main_frame, text="Status:").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))

        self.status_text = tk.Text(main_frame, height=8, width=70, wrap=tk.WORD)
        self.status_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=9, column=3, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)

        # Configure row weights for proper resizing
        main_frame.rowconfigure(9, weight=1)

    def on_type_change(self):
        """Handle download type change"""
        if self.download_type.get() == "audio":
            self.download_btn.config(text="Download MP3")
        else:
            self.download_btn.config(text="Download Video")

    def browse_destination(self):
        """Open file dialog to select download destination"""
        directory = filedialog.askdirectory(initialdir=self.dest_var.get())
        if directory:
            self.dest_var.set(directory)

    def log_message(self, message):
        """Add message to status text area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def start_download(self):
        """Start download in a separate thread"""
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("Download in Progress", "A download is already in progress.")
            return

        url = self.url_var.get().strip()
        destination = self.dest_var.get().strip()
        download_type = self.download_type.get()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        if not destination:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        if not os.path.exists(destination):
            # Try to create the directory
            os.makedirs(destination)
            if not os.path.exists(destination):
                messagebox.showerror("Error", "Failed to create destination directory.")
                return

        # Disable UI elements during download
        self.download_btn.config(state='disabled')
        self.url_entry.config(state='disabled')
        self.dest_entry.config(state='disabled')
        self.browse_btn.config(state='disabled')

        # Clear status and start progress
        self.status_text.delete(1.0, tk.END)
        self.progress_var.set("Downloading...")
        self.progress_bar.start()

        # Start download in separate thread
        self.download_thread = threading.Thread(target=self.download_media,
                                               args=(url, destination, download_type))
        self.download_thread.daemon = True
        self.download_thread.start()

    def download_media(self, video_url, destination, download_type):
        """Download media from video URL"""
        try:
            self.log_message(f"Starting {download_type} download from: {video_url}")
            self.log_message(f"Destination: {destination}")

            if download_type == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.audio_quality.get(),
                    }],
                    'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
            else:  # video
                quality = self.video_quality.get()
                if quality == "best":
                    format_str = "bestvideo+bestaudio/best"
                elif quality == "worst":
                    format_str = "worstvideo+worstaudio/worst"
                else:
                    # For specific resolutions, use format selection
                    format_str = f"bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]"

                ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                self.log_message("Fetching video information...")
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Unknown Title')
                self.log_message(f"Video title: {title}")

                # Download the media
                if download_type == "audio":
                    self.log_message("Downloading and converting to MP3...")
                else:
                    self.log_message(f"Downloading video in {quality} quality...")

                ydl.download([video_url])

            self.log_message("Download completed successfully!")
            media_type = "MP3" if download_type == "audio" else "Video"
            self.root.after(0, lambda: messagebox.showinfo("Success",
                f"{media_type} downloaded successfully!\nTitle: {title}\nLocation: {destination}"))

        except Exception as e:
            error_msg = f"Error during download: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Download Error", error_msg))

        finally:
            # Re-enable UI elements
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        """Reset UI elements after download completes"""
        self.download_btn.config(state='normal')
        self.url_entry.config(state='normal')
        self.dest_entry.config(state='normal')
        self.browse_btn.config(state='normal')
        self.progress_var.set("Ready to download")
        self.progress_bar.stop()

def main():
    root = tk.Tk()
    app = MediaDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
