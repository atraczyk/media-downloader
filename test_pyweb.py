import webview
import json
import time

class Api:
    def greet(self, name):
        print(f"Python received: {name}")
        return f"Hello, {name} from Python!"

    def get_system_info(self):
        import platform
        return {
            'platform': platform.system(),
            'version': platform.version(),
            'processor': platform.processor(),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def calculate(self, operation, a, b):
        operations = {
            'add': lambda x, y: x + y,
            'subtract': lambda x, y: x - y,
            'multiply': lambda x, y: x * y,
            'divide': lambda x, y: x / y if y != 0 else 'Cannot divide by zero'
        }
        return operations.get(operation, lambda x, y: 'Invalid operation')(a, b)

    def get_app_info(self):
        return {
            'name': 'Desktop Application Demo',
            'version': '1.0.0',
            'framework': 'PyWebView',
            'backend': 'Python 3.x'
        }

api = Api()

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebView Beautiful Demo</title>
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

        h1 {
            color: #2c3e50;
            margin: 0 0 20px 0;
            font-size: 1.8em;
            font-weight: 400;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            padding: 20px 20px 15px 20px;
        }

        .demo-section {
            margin: 0 20px 20px 20px;
            padding: 20px;
            background: #fafafa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 0;
        }

        .demo-section h3 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        button {
            background: #0078d4;
            color: white;
            border: 1px solid #0078d4;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 400;
            margin: 5px;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        button:hover {
            background: #106ebe;
            border-color: #106ebe;
        }

        button:active {
            background: #005a9e;
            border-color: #005a9e;
        }

        button:focus {
            outline: 2px solid #0078d4;
            outline-offset: 2px;
        }

        input {
            padding: 8px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 5px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s ease;
        }

        input:focus {
            outline: none;
            border-color: #0078d4;
            box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
        }

        select {
            padding: 8px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 5px;
            font-size: 14px;
            font-family: inherit;
            background: white;
        }

        select:focus {
            outline: none;
            border-color: #0078d4;
            box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
        }

        .result {
            margin-top: 15px;
            padding: 12px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #28a745;
            border-radius: 4px;
            text-align: left;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            color: #495057;
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #e9ecef;
            border-top: 2px solid #0078d4;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .calculator {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            align-items: center;
            margin-top: 15px;
        }

        .calc-input {
            width: 100%;
        }

        .toolbar {
            background: #ffffff;
            border-bottom: 1px solid #dee2e6;
            padding: 15px 20px;
            margin: 0;
            border-radius: 0;
            flex-shrink: 0;
        }

        .toolbar h2 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #495057;
        }

        .status-bar {
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            padding: 8px 20px;
            margin: 0;
            border-radius: 0;
            font-size: 12px;
            color: #6c757d;
            text-align: center;
            flex-shrink: 0;
        }

        .menu-bar {
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            padding: 8px 20px;
            margin: 0;
            border-radius: 0;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-shrink: 0;
        }

        .menu-item {
            background: none;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            color: #495057;
            transition: background-color 0.2s ease;
        }

        .menu-item:hover {
            background: #e9ecef;
        }

        .keyboard-hint {
            font-size: 11px;
            color: #6c757d;
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="menu-bar">
            <button class="menu-item" onclick="showAbout()">About <span class="keyboard-hint">F1</span></button>
            <button class="menu-item" onclick="clearAll()">Clear All <span class="keyboard-hint">Ctrl+L</span></button>
            <button class="menu-item" onclick="refreshApp()">Refresh <span class="keyboard-hint">F5</span></button>
        </div>
        <div class="toolbar">
            <h2>PyWebView Desktop Application Demo</h2>
        </div>

        <div class="content-area">
            <h1>Application Features</h1>

            <div class="demo-section">
            <h3>👋 Greeting Demo</h3>
            <input type="text" id="nameInput" placeholder="Enter your name" value="World">
            <button onclick="sayHi()">Greet Me!</button>
            <div id="greetResult"></div>
        </div>

        <div class="demo-section">
            <h3>💻 System Information</h3>
            <button onclick="getSystemInfo()">Get System Info</button>
            <div id="systemResult"></div>
        </div>

        <div class="demo-section">
            <h3>🧮 Calculator</h3>
            <div class="calculator">
                <input type="number" id="num1" placeholder="First number" class="calc-input">
                <input type="number" id="num2" placeholder="Second number" class="calc-input">
                <select id="operation" class="calc-input">
                    <option value="add">Add (+)</option>
                    <option value="subtract">Subtract (-)</option>
                    <option value="multiply">Multiply (×)</option>
                    <option value="divide">Divide (÷)</option>
                </select>
                <button onclick="calculate()" class="calc-input">Calculate</button>
            </div>
            <div id="calcResult"></div>
            </div>
        </div>

        <div class="status-bar">
            Ready | PyWebView Desktop Application | Python Backend Active
        </div>
    </div>

    <script>
        async function sayHi() {
            const name = document.getElementById('nameInput').value || 'World';
            const resultDiv = document.getElementById('greetResult');

            resultDiv.innerHTML = '<div class="loading"></div>';

            try {
                const result = await pywebview.api.greet(name);
                resultDiv.innerHTML = `<div class="result">✨ ${result}</div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result">❌ Error: ${error}</div>`;
            }
        }

        async function getSystemInfo() {
            const resultDiv = document.getElementById('systemResult');

            resultDiv.innerHTML = '<div class="loading"></div>';

            try {
                const info = await pywebview.api.get_system_info();
                const formatted = `🖥️ Platform: ${info.platform}
📋 Version: ${info.version}
⚡ Processor: ${info.processor}
🕒 Timestamp: ${info.timestamp}`;
                resultDiv.innerHTML = `<div class="result">${formatted}</div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result">❌ Error: ${error}</div>`;
            }
        }

        async function calculate() {
            const num1 = parseFloat(document.getElementById('num1').value);
            const num2 = parseFloat(document.getElementById('num2').value);
            const operation = document.getElementById('operation').value;
            const resultDiv = document.getElementById('calcResult');

            if (isNaN(num1) || isNaN(num2)) {
                resultDiv.innerHTML = '<div class="result">❌ Please enter valid numbers</div>';
                return;
            }

            resultDiv.innerHTML = '<div class="loading"></div>';

            try {
                const result = await pywebview.api.calculate(operation, num1, num2);
                const operationSymbols = {
                    'add': '+',
                    'subtract': '-',
                    'multiply': '×',
                    'divide': '÷'
                };
                const symbol = operationSymbols[operation];
                resultDiv.innerHTML = `<div class="result">🧮 ${num1} ${symbol} ${num2} = ${result}</div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result">❌ Error: ${error}</div>`;
            }
        }

        // Desktop application features
        document.addEventListener('DOMContentLoaded', function() {
            // Add enter key support for inputs
            document.getElementById('nameInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sayHi();
            });

            // Add enter key support for calculator
            ['num1', 'num2'].forEach(id => {
                document.getElementById(id).addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') calculate();
                });
            });

            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // F1 - About
                if (e.key === 'F1') {
                    e.preventDefault();
                    showAbout();
                }
                // Ctrl+L - Clear All
                if (e.ctrlKey && e.key === 'l') {
                    e.preventDefault();
                    clearAll();
                }
                // F5 - Refresh
                if (e.key === 'F5') {
                    e.preventDefault();
                    refreshApp();
                }
            });

            // Update status bar with current time
            updateStatusBar();
            setInterval(updateStatusBar, 1000);
        });

        async function showAbout() {
            try {
                const info = await pywebview.api.get_app_info();
                alert(`${info.name}\\nVersion: ${info.version}\\nFramework: ${info.framework}\\nBackend: ${info.backend}`);
            } catch (error) {
                alert('Desktop Application Demo\\nVersion: 1.0.0\\nFramework: PyWebView\\nBackend: Python');
            }
        }

        function clearAll() {
            document.getElementById('greetResult').innerHTML = '';
            document.getElementById('systemResult').innerHTML = '';
            document.getElementById('calcResult').innerHTML = '';
            document.getElementById('nameInput').value = 'World';
            document.getElementById('num1').value = '';
            document.getElementById('num2').value = '';
        }

        function refreshApp() {
            location.reload();
        }

        function updateStatusBar() {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            const statusBar = document.querySelector('.status-bar');
            statusBar.textContent = `Ready | PyWebView Desktop Application | Python Backend Active | ${timeString}`;
        }
    </script>
</body>
</html>
"""

webview.create_window(
    "Desktop Application Demo",
    html=html,
    js_api=api,
    width=900,
    height=750,
    resizable=True,
    on_top=False
)
webview.start(debug=False)
