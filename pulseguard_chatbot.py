#!/usr/bin/env python3
"""
PulseGuard AI Chatbot - Ask anything about your system!
Real-time integration with PulseGuard monitoring system
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import os

class PulseGuardAPI:
    """Real PulseGuard API client for live data"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def get_system_status(self):
        """Get real system status from PulseGuard"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ PulseGuard not available: {e}")
        
        # Demo data when main system not available
        return {
            "status": "demo_mode",
            "agents": {"total": 5, "active": 4, "inactive": 1},
            "system": {"cpu": 45.2, "memory": 68.5, "disk": 23.1}
        }
    
    def get_metrics(self, time_range="1h"):
        """Get real system metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics?interval={time_range}", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Metrics not available: {e}")
        
        return {
            "cpu_usage": [45.2, 47.1, 43.8, 46.5],
            "memory_usage": [68.5, 70.2, 67.9, 69.1],
            "network_io": [1024, 1156, 998, 1087],
            "mode": "demo"
        }

# Global API client
pulseguard = PulseGuardAPI()

class ChatbotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).path
        
        if parsed_path == '/':
            self.serve_chatbot()
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404, "Not found")
    
    def serve_chatbot(self):
        """Serve the main chatbot interface"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>[ROBOT] PulseGuard AI Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .intro {
            background: #f0f8ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #4CAF50;
        }
        .chat-container {
            border: 1px solid #ddd;
            height: 400px;
            overflow-y: auto;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
        }
        .bot-message {
            background: #f1f8e9;
            border-left: 4px solid #4CAF50;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
        .examples {
            margin-top: 15px;
            font-size: 14px;
            color: #666;
        }
        .example-btn {
            background: #2196F3;
            margin: 2px;
            padding: 5px 10px;
            font-size: 12px;
        }
        .status {
            text-align: center;
            margin: 10px 0;
            font-weight: bold;
        }
        .live { color: #4CAF50; }
        .demo { color: #FF9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>[ROBOT] PulseGuard AI Assistant</h1>
        
        <div class="intro">
            <strong>[CHAT] Ask me anything about your PulseGuard system!</strong><br><br>
            I can provide real-time information about:
            <ul>
                <li><strong>System Performance:</strong> CPU, memory, disk usage</li>
                <li><strong>Agent Status:</strong> How many agents are running, their health</li>
                <li><strong>Alerts & Issues:</strong> Any system problems or warnings</li>
                <li><strong>Metrics & Trends:</strong> Performance over time</li>
                <li><strong>Integration Status:</strong> MCP server, AI providers</li>
            </ul>
        </div>
        
        <div id="status" class="status"></div>
        
        <div id="chat-container" class="chat-container">
            <div class="bot-message message">
                [WAVE] Hello! I'm your PulseGuard AI assistant. I can answer any questions about your system performance and status.<br><br>
                <strong>Try asking me:</strong><br>
                * "What's the current CPU usage?"<br>
                * "How many agents are running?"<br>
                * "Are there any system alerts?"<br>
                * "Show me memory consumption"<br>
                * "What's the system status?"
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Ask me anything about PulseGuard..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div class="examples">
            <strong>Quick Examples:</strong><br>
            <button class="example-btn" onclick="askQuestion('What is the CPU usage?')">CPU Usage</button>
            <button class="example-btn" onclick="askQuestion('How many agents are online?')">Agent Count</button>
            <button class="example-btn" onclick="askQuestion('Are there any alerts?')">System Alerts</button>
            <button class="example-btn" onclick="askQuestion('Show me system status')">Full Status</button>
            <button class="example-btn" onclick="askQuestion('What is the memory usage?')">Memory Usage</button>
        </div>
    </div>

    <script>
        function addMessage(type, content) {
            const container = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `${type}-message message`;
            messageDiv.innerHTML = content;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        function updateStatus(isLive) {
            const statusDiv = document.getElementById('status');
            if (isLive) {
                statusDiv.innerHTML = '🟢 Connected to Live PulseGuard System';
                statusDiv.className = 'status live';
            } else {
                statusDiv.innerHTML = '[YELLOW] Demo Mode - PulseGuard System Not Available';
                statusDiv.className = 'status demo';
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;

            addMessage('user', message);
            input.value = '';

            // Show typing indicator
            addMessage('bot', '🤔 Checking PulseGuard system...');

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                const container = document.getElementById('chat-container');
                container.removeChild(container.lastChild);
                
                addMessage('bot', data.response);
                updateStatus(data.live_data);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', '❌ Sorry, there was an error processing your request.');
            });
        }

        function askQuestion(question) {
            document.getElementById('messageInput').value = question;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Initialize status
        updateStatus(false);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_chat(self):
        """Handle chat messages with real PulseGuard integration"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            message = data['message'].lower()
            
            # Get real-time PulseGuard data
            status = pulseguard.get_system_status()
            metrics = pulseguard.get_metrics()
            
            is_live = status.get('status') != 'demo_mode'
            
            # Natural language processing for PulseGuard questions
            if any(word in message for word in ['cpu', 'processor']):
                cpu = status.get('system', {}).get('cpu', 'N/A')
                response = f"""<strong>🖥️ CPU Usage Information</strong><br><br>
                Current CPU Usage: <strong>{cpu}%</strong><br>
                Recent trend: {', '.join(map(str, metrics.get('cpu_usage', [])[-4:]))}%<br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['memory', 'ram']):
                memory = status.get('system', {}).get('memory', 'N/A')
                response = f"""<strong>🧠 Memory Usage Information</strong><br><br>
                Current Memory Usage: <strong>{memory}%</strong><br>
                Recent trend: {', '.join(map(str, metrics.get('memory_usage', [])[-4:]))}%<br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['agent', 'agents']):
                total = status.get('agents', {}).get('total', 0)
                active = status.get('agents', {}).get('active', 0)
                response = f"""<strong>[ROBOT] Agent Status</strong><br><br>
                Total Agents: <strong>{total}</strong><br>
                Active Agents: <strong>{active}</strong><br>
                Inactive Agents: <strong>{total - active}</strong><br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['status', 'overview', 'health']):
                cpu = status.get('system', {}).get('cpu', 'N/A')
                memory = status.get('system', {}).get('memory', 'N/A')
                disk = status.get('system', {}).get('disk', 'N/A')
                response = f"""<strong>📊 System Overview</strong><br><br>
                <strong>System Performance:</strong><br>
                • CPU: {cpu}%<br>
                • Memory: {memory}%<br>
                • Disk: {disk}%<br><br>
                <strong>Agents:</strong><br>
                • Total: {status.get('agents', {}).get('total', 0)}<br>
                • Active: {status.get('agents', {}).get('active', 0)}<br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['alert', 'alerts', 'problem', 'issue']):
                cpu = status.get('system', {}).get('cpu', 0)
                memory = status.get('system', {}).get('memory', 0)
                
                alerts = []
                if cpu > 80:
                    alerts.append(f"🔴 High CPU usage: {cpu}%")
                if memory > 85:
                    alerts.append(f"🔴 High memory usage: {memory}%")
                
                if alerts:
                    response = f"""<strong>⚠️ System Alerts</strong><br><br>
                    {('<br>'.join(alerts))}<br><br>
                    {'🟢 Live alerts from PulseGuard' if is_live else '🟡 Demo alerts - PulseGuard not connected'}"""
                else:
                    response = f"""<strong>✅ No Critical Alerts</strong><br><br>
                    System is operating within normal parameters<br><br>
                    {'🟢 Live status from PulseGuard' if is_live else '🟡 Demo status - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['disk', 'storage', 'space']):
                disk = status.get('system', {}).get('disk', 'N/A')
                response = f"""<strong>💾 Disk Usage Information</strong><br><br>
                Current Disk Usage: <strong>{disk}%</strong><br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            elif any(word in message for word in ['performance', 'metrics']):
                response = f"""<strong>📈 Performance Metrics</strong><br><br>
                <strong>Current Values:</strong><br>
                • CPU: {metrics.get('cpu_usage', [0])[-1] if metrics.get('cpu_usage') else 'N/A'}%<br>
                • Memory: {metrics.get('memory_usage', [0])[-1] if metrics.get('memory_usage') else 'N/A'}%<br>
                • Network I/O: {metrics.get('network_io', [0])[-1] if metrics.get('network_io') else 'N/A'} KB/s<br><br>
                {'🟢 Live metrics from PulseGuard' if is_live else '🟡 Demo metrics - PulseGuard not connected'}"""
            
            else:
                # General AI response
                response = f"""<strong>[ROBOT] PulseGuard AI Assistant</strong><br><br>
                I understand you're asking: "<em>{data['message']}</em>"<br><br>
                <strong>Current System Summary:</strong><br>
                • CPU: {status.get('system', {}).get('cpu', 'N/A')}%<br>
                • Memory: {status.get('system', {}).get('memory', 'N/A')}%<br>
                • Active Agents: {status.get('agents', {}).get('active', 0)}<br><br>
                <strong>Try asking more specific questions like:</strong><br>
                • "What's the CPU usage?"<br>
                • "How many agents are running?"<br>
                • "Are there any system alerts?"<br><br>
                {'🟢 Live data from PulseGuard' if is_live else '🟡 Demo data - PulseGuard not connected'}"""
            
            result = {
                'response': response,
                'live_data': is_live,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            result = {
                'response': f'❌ Error processing request: {str(e)}',
                'live_data': False,
                'timestamp': datetime.now().isoformat()
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

if __name__ == '__main__':
    port = 8090
    server = HTTPServer(('localhost', port), ChatbotHandler)
    
    print(f"""
[ROBOT] PULSEGUARD AI ASSISTANT READY!
===================================
[WEB] Open: http://localhost:8090
[CHAT] Ask me ANYTHING about your PulseGuard system!

Examples:
• "What's the CPU usage?"
• "How many agents are running?"
• "Are there any system alerts?"
• "Show me memory consumption"
• "What's the system performance?"

🔗 Integration Status:
• Attempting connection to PulseGuard at http://localhost:8000
• Will fall back to demo data if not available
===================================
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down PulseGuard AI Assistant...")
        server.shutdown()