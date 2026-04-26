"""
HTML interface generator for Media Downloader WebView GUI.
Handles the creation of HTML, CSS, and JavaScript content.
Follows Single Responsibility Principle - only handles UI markup generation.
"""


def create_html_interface() -> str:
    """Create the HTML interface for the media downloader"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Downloader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffffff;
            margin: 0;
            padding: 0;
            color: #333;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            background: #ffffff;
            border: none;
            border-radius: 0;
            padding: 0;
            box-shadow: none;
            max-width: none;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #0078d4;
            color: white;
            padding: 20px;
            text-align: center;
            flex-shrink: 0;
        }

        .header h1 {
            margin: 0;
            font-size: 1.8em;
            font-weight: 400;
        }

        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 0.9em;
        }

        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .section {
            margin-bottom: 25px;
            padding: 20px;
            background: #fafafa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .section h3 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #2d3748;
        }

        input, select, textarea {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s ease;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #0078d4;
            box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            align-items: end;
        }

        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .checkbox-item input[type="checkbox"] {
            width: auto;
            margin: 0;
        }

        .radio-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .radio-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .radio-item input[type="radio"] {
            width: auto;
            margin: 0;
        }

        button {
            background: #0078d4;
            color: white;
            border: 1px solid #0078d4;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        button:hover:not(:disabled) {
            background: #106ebe;
            border-color: #106ebe;
        }

        button:active:not(:disabled) {
            background: #005a9e;
            border-color: #005a9e;
        }

        button:disabled {
            background: #ccc;
            border-color: #ccc;
            cursor: not-allowed;
        }

        button.secondary {
            background: #6c757d;
            border-color: #6c757d;
        }

        button.secondary:hover:not(:disabled) {
            background: #5a6268;
            border-color: #5a6268;
        }

        button.success {
            background: #28a745;
            border-color: #28a745;
        }

        button.success:hover:not(:disabled) {
            background: #218838;
            border-color: #218838;
        }

        .download-btn {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            font-weight: 600;
        }

        .progress-section {
            margin-top: 20px;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: #0078d4;
            transition: width 0.3s ease;
            width: 0%;
        }

        .status-text {
            font-size: 14px;
            margin: 5px 0;
            min-height: 20px;
        }

        .status-downloading { color: #0078d4; }
        .status-processing { color: #ffc107; }
        .status-completed { color: #28a745; }
        .status-failed { color: #dc3545; }

        .text-area {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #0078d4;
            border-radius: 4px;
            padding: 15px;
            margin-top: 10px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            color: #495057;
        }

        .text-area.transcript {
            border-left-color: #28a745;
        }

        .text-area.summary {
            border-left-color: #17a2b8;
        }

        .text-area.logs {
            border-left-color: #6c757d;
            max-height: 150px;
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #e9ecef;
            border-top: 2px solid #0078d4;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .url-validation {
            margin-top: 5px;
            font-size: 12px;
            min-height: 16px;
        }

        .url-validation.valid {
            color: #28a745;
        }

        .url-validation.invalid {
            color: #dc3545;
        }

        .media-info {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
            font-size: 13px;
        }

        .hidden {
            display: none;
        }

        .footer {
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            padding: 15px 20px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
            flex-shrink: 0;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .content-area {
                padding: 15px;
            }

            .section {
                padding: 15px;
            }

            .radio-group {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Media Downloader</h1>
            <p>Download audio and video from YouTube with transcript and summary support</p>
        </div>

        <div class="content-area">
            <!-- URL Input Section -->
            <div class="section">
                <h3>🔗 Media URL</h3>
                <div class="form-group">
                    <label for="urlInput">Enter YouTube URL:</label>
                    <input type="url" id="urlInput" placeholder="https://www.youtube.com/watch?v=..." />
                    <div id="urlValidation" class="url-validation"></div>
                    <div id="mediaInfo" class="media-info hidden"></div>
                </div>
            </div>

            <!-- Download Options Section -->
            <div class="section">
                <h3>⚙️ Download Options</h3>
                <div class="form-group">
                    <label>Download Type:</label>
                    <div class="radio-group">
                        <div class="radio-item">
                            <input type="radio" id="audioType" name="downloadType" value="Audio (MP3)" checked />
                            <label for="audioType">Audio (MP3)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="videoType" name="downloadType" value="Video (WebM)" />
                            <label for="videoType">Video (WebM)</label>
                        </div>
                    </div>
                </div>

                <div id="audioOptions" class="form-group">
                    <label for="audioQuality">Audio Quality:</label>
                    <select id="audioQuality">
                        <option value="128">128 kbps</option>
                        <option value="192" selected>192 kbps</option>
                        <option value="256">256 kbps</option>
                        <option value="320">320 kbps</option>
                    </select>
                </div>

                <div id="videoOptions" class="form-group hidden">
                    <label for="videoQuality">Video Quality:</label>
                    <select id="videoQuality">
                        <option value="best" selected>Best Available</option>
                        <option value="720p">720p</option>
                        <option value="1080p">1080p</option>
                        <option value="1440p">1440p</option>
                        <option value="2160p">4K (2160p)</option>
                        <option value="worst">Worst (Smallest)</option>
                    </select>
                </div>
            </div>

            <!-- Transcript & Summary Section -->
            <div class="section">
                <h3>📝 Transcript & Summary</h3>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="transcriptEnabled" checked />
                        <label for="transcriptEnabled">Download transcript (if available)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="summaryEnabled" />
                        <label for="summaryEnabled">Generate summary (requires transcript)</label>
                    </div>
                </div>
            </div>

            <!-- Destination Section -->
            <div class="section">
                <h3>📁 Destination</h3>
                <div class="form-group">
                    <label for="destinationInput">Save to folder:</label>
                    <div class="form-row">
                        <input type="text" id="destinationInput" placeholder="Select destination folder..." readonly />
                        <button type="button" onclick="browseFolder()" class="secondary">Browse</button>
                    </div>
                </div>
            </div>

            <!-- Download Section -->
            <div class="section">
                <button id="downloadBtn" class="download-btn" onclick="startDownload()">
                    🎵 Download MP3
                </button>

                <div id="progressSection" class="progress-section hidden">
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill"></div>
                    </div>
                    <div id="statusText" class="status-text"></div>
                </div>
            </div>

            <!-- Results Section -->
            <div id="resultsSection" class="section hidden">
                <h3>📄 Results</h3>

                <div id="transcriptSection" class="hidden">
                    <label>Transcript:</label>
                    <div id="transcriptText" class="text-area transcript"></div>
                </div>

                <div id="summarySection" class="hidden">
                    <label>Summary:</label>
                    <div id="summaryText" class="text-area summary"></div>
                </div>
            </div>

            <!-- Logs Section -->
            <div class="section">
                <h3>📋 Logs</h3>
                <div id="logsText" class="text-area logs">Ready to download...</div>
                <button type="button" onclick="clearLogs()" class="secondary" style="margin-top: 10px;">Clear Logs</button>
            </div>
        </div>

        <div class="footer">
            <span id="footerStatus">Ready | Media Downloader v2.0 | Python Backend Active</span>
        </div>
    </div>

    <script>
        // Global state
        let isDownloading = false;
        let urlValidationTimeout = null;

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            initializeApp();
            setupEventListeners();
            setDefaultDestination();
        });

        async function initializeApp() {
            try {
                const appInfo = await pywebview.api.get_app_info();
                document.title = appInfo.name;
                updateFooterStatus();
            } catch (error) {
                console.error('Failed to initialize app:', error);
            }
        }

        function setupEventListeners() {
            // URL input validation
            document.getElementById('urlInput').addEventListener('input', function() {
                clearTimeout(urlValidationTimeout);
                urlValidationTimeout = setTimeout(validateUrl, 500);
            });

            // Download type change
            document.querySelectorAll('input[name="downloadType"]').forEach(radio => {
                radio.addEventListener('change', onDownloadTypeChange);
            });

            // Summary checkbox dependency
            document.getElementById('summaryEnabled').addEventListener('change', function() {
                if (this.checked) {
                    document.getElementById('transcriptEnabled').checked = true;
                }
            });

            // Transcript checkbox dependency
            document.getElementById('transcriptEnabled').addEventListener('change', function() {
                if (!this.checked) {
                    document.getElementById('summaryEnabled').checked = false;
                }
            });

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter' && !isDownloading) {
                    startDownload();
                }
                if (e.key === 'F5') {
                    e.preventDefault();
                    location.reload();
                }
            });
        }

        async function setDefaultDestination() {
            // Set default destination to downloads folder
            const defaultPath = 'downloads'; // Relative path
            document.getElementById('destinationInput').value = defaultPath;
        }

        async function validateUrl() {
            const urlInput = document.getElementById('urlInput');
            const validation = document.getElementById('urlValidation');
            const mediaInfo = document.getElementById('mediaInfo');
            const url = urlInput.value.trim();

            if (!url) {
                validation.textContent = '';
                validation.className = 'url-validation';
                mediaInfo.classList.add('hidden');
                return;
            }

            validation.innerHTML = '<span class="loading"></span>Validating URL...';
            validation.className = 'url-validation';

            try {
                const result = await pywebview.api.validate_url(url);

                if (result.valid) {
                    validation.textContent = '✓ Valid URL';
                    validation.className = 'url-validation valid';

                    if (result.title) {
                        let infoHtml = `<strong>Title:</strong> ${result.title}`;
                        if (result.uploader) {
                            infoHtml += `<br><strong>Uploader:</strong> ${result.uploader}`;
                        }
                        if (result.duration) {
                            const minutes = Math.floor(result.duration / 60);
                            const seconds = result.duration % 60;
                            infoHtml += `<br><strong>Duration:</strong> ${minutes}:${seconds.toString().padStart(2, '0')}`;
                        }
                        mediaInfo.innerHTML = infoHtml;
                        mediaInfo.classList.remove('hidden');
                    }
                } else {
                    validation.textContent = `✗ ${result.error}`;
                    validation.className = 'url-validation invalid';
                    mediaInfo.classList.add('hidden');
                }
            } catch (error) {
                validation.textContent = `✗ Validation failed: ${error}`;
                validation.className = 'url-validation invalid';
                mediaInfo.classList.add('hidden');
            }
        }

        function onDownloadTypeChange() {
            const downloadType = document.querySelector('input[name="downloadType"]:checked').value;
            const audioOptions = document.getElementById('audioOptions');
            const videoOptions = document.getElementById('videoOptions');
            const downloadBtn = document.getElementById('downloadBtn');

            if (downloadType === 'Audio (MP3)') {
                audioOptions.classList.remove('hidden');
                videoOptions.classList.add('hidden');
                downloadBtn.innerHTML = '🎵 Download MP3';
            } else {
                audioOptions.classList.add('hidden');
                videoOptions.classList.remove('hidden');
                downloadBtn.innerHTML = '🎬 Download Video';
            }
        }

        async function browseFolder() {
            try {
                const result = await pywebview.api.browse_folder();
                if (result.success) {
                    document.getElementById('destinationInput').value = result.path;
                } else {
                    alert('Failed to select folder: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to open folder browser: ' + error);
            }
        }

        async function startDownload() {
            if (isDownloading) return;

            const url = document.getElementById('urlInput').value.trim();
            const destination = document.getElementById('destinationInput').value.trim();

            if (!url) {
                alert('Please enter a valid URL');
                return;
            }

            if (!destination) {
                alert('Please select a destination folder');
                return;
            }

            const requestData = {
                url: url,
                destination: destination,
                downloadType: document.querySelector('input[name="downloadType"]:checked').value,
                audioQuality: document.getElementById('audioQuality').value,
                videoQuality: document.getElementById('videoQuality').value,
                transcriptEnabled: document.getElementById('transcriptEnabled').checked,
                summaryEnabled: document.getElementById('summaryEnabled').checked
            };

            try {
                const result = await pywebview.api.start_download(requestData);

                if (result.success) {
                    setDownloadingState(true);
                    showProgressSection();
                    clearResults();
                } else {
                    alert('Failed to start download: ' + result.error);
                }
            } catch (error) {
                alert('Download error: ' + error);
            }
        }

        function setDownloadingState(downloading) {
            isDownloading = downloading;
            const downloadBtn = document.getElementById('downloadBtn');
            const inputs = document.querySelectorAll('input, select, button');

            if (downloading) {
                downloadBtn.textContent = 'Downloading...';
                downloadBtn.disabled = true;
                inputs.forEach(input => {
                    if (input !== downloadBtn && input.id !== 'logsText') {
                        input.disabled = true;
                    }
                });
            } else {
                onDownloadTypeChange(); // Restore button text
                downloadBtn.disabled = false;
                inputs.forEach(input => input.disabled = false);
            }
        }

        function showProgressSection() {
            document.getElementById('progressSection').classList.remove('hidden');
        }

        function hideProgressSection() {
            document.getElementById('progressSection').classList.add('hidden');
        }

        function clearResults() {
            document.getElementById('resultsSection').classList.add('hidden');
            document.getElementById('transcriptSection').classList.add('hidden');
            document.getElementById('summarySection').classList.add('hidden');
        }

        async function clearLogs() {
            try {
                await pywebview.api.clear_logs();
                document.getElementById('logsText').textContent = 'Logs cleared...';
            } catch (error) {
                console.error('Failed to clear logs:', error);
            }
        }

        function updateFooterStatus() {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            const status = isDownloading ? 'Downloading' : 'Ready';
            document.getElementById('footerStatus').textContent =
                `${status} | Media Downloader v2.0 | Python Backend Active | ${timeString}`;
        }

        // Callback functions for Python backend
        window.handleProgressUpdate = function(progressData) {
            const progressFill = document.getElementById('progressFill');
            const statusText = document.getElementById('statusText');

            progressFill.style.width = (progressData.progress * 100) + '%';
            statusText.textContent = progressData.message;
            statusText.className = `status-text status-${progressData.status}`;

            updateFooterStatus();
        };

        window.handleTranscriptUpdate = function(transcriptData) {
            const transcriptSection = document.getElementById('transcriptSection');
            const transcriptText = document.getElementById('transcriptText');
            const resultsSection = document.getElementById('resultsSection');

            if (transcriptData.text) {
                transcriptText.textContent = transcriptData.text;
                transcriptSection.classList.remove('hidden');
                resultsSection.classList.remove('hidden');
            } else if (transcriptData.error) {
                transcriptText.textContent = `Transcript not available: ${transcriptData.error}`;
                transcriptSection.classList.remove('hidden');
                resultsSection.classList.remove('hidden');
            }
        };

        window.handleSummaryUpdate = function(summaryData) {
            const summarySection = document.getElementById('summarySection');
            const summaryText = document.getElementById('summaryText');
            const resultsSection = document.getElementById('resultsSection');

            if (summaryData.summary) {
                summaryText.textContent = summaryData.summary;
                summarySection.classList.remove('hidden');
                resultsSection.classList.remove('hidden');
            } else if (summaryData.error) {
                summaryText.textContent = `Summary not available: ${summaryData.error}`;
                summarySection.classList.remove('hidden');
                resultsSection.classList.remove('hidden');
            }
        };

        window.handleDownloadComplete = function(completionData) {
            setDownloadingState(false);

            if (completionData.success) {
                alert(`Download completed successfully!\\n${completionData.message}`);
            } else {
                alert(`Download failed: ${completionData.message}`);
                hideProgressSection();
            }

            updateFooterStatus();
        };

        window.handleLogUpdate = function(logEntry) {
            const logsText = document.getElementById('logsText');
            const currentLogs = logsText.textContent;

            if (currentLogs === 'Ready to download...' || currentLogs === 'Logs cleared...') {
                logsText.textContent = logEntry;
            } else {
                logsText.textContent = currentLogs + '\\n' + logEntry;
            }

            // Auto-scroll to bottom
            logsText.scrollTop = logsText.scrollHeight;
        };

        // Update footer status every second
        setInterval(updateFooterStatus, 1000);
    </script>
</body>
</html>
    """

