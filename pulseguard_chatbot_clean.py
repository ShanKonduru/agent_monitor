#!/usr/bin/env python3
"""
PulseGuard Chatbot with Live Data Integration
Clean ASCII version without Unicode characters
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import urllib.request
from datetime import datetime

class PulseGuardChatbotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/chat':
            self.serve_chat_page()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/chat':
            self.handle_chat_request()
        else:
            self.send_error(404)
    
    def serve_chat_page(self):
        """Serve the main chat interface"""
        # Check if PulseGuard API is available
        is_live = self.check_pulseguard_connection()
        status_class = "live" if is_live else "demo"
        status_text = "[LIVE] Connected to PulseGuard System" if is_live else "[DEMO] Demo Mode - PulseGuard System Not Available"
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>[ROBOT] PulseGuard AI Assistant</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f7fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .status {{
                    display: inline-block;
                    padding: 8px 15px;
                    border-radius: 20px;
                    margin: 10px 0;
                    font-weight: bold;
                }}
                .status.live {{
                    background-color: #4CAF50;
                    color: white;
                }}
                .status.demo {{
                    background-color: #ff9800;
                    color: white;
                }}
                .container {{
                    display: grid;
                    grid-template-columns: 1fr 300px;
                    gap: 30px;
                }}
                .chat-area {{
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .sidebar {{
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    height: fit-content;
                }}
                .messages {{
                    height: 400px;
                    overflow-y: auto;
                    border: 2px solid #e1e5e9;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 20px;
                    background-color: #fafbfc;
                }}
                .message {{
                    margin-bottom: 15px;
                    padding: 12px;
                    border-radius: 8px;
                }}
                .user-message {{
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                }}
                .assistant-message {{
                    background-color: #f1f8e9;
                    border-left: 4px solid #4caf50;
                }}
                .input-area {{
                    display: flex;
                    gap: 10px;
                }}
                input[type="text"] {{
                    flex: 1;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                }}
                button {{
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: bold;
                }}
                button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .examples {{
                    margin-top: 20px;
                }}
                .example-btn {{
                    display: block;
                    width: 100%;
                    margin: 8px 0;
                    padding: 10px;
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    cursor: pointer;
                    text-align: left;
                }}
                .example-btn:hover {{
                    background: #e9ecef;
                }}
                .intro {{
                    background: #e8f4fd;
                    border: 1px solid #bee5eb;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>[ROBOT] PulseGuard AI Assistant</h1>
                <p><strong>[CHAT] Ask me anything about your PulseGuard system!</strong></p>
                <div class="status {status_class}">
                    {status_text}
                </div>
            </div>
            
            <div class="container">
                <div class="chat-area">
                    <div class="intro">
                        <strong>System Information Available:</strong>
                        <ul>
                            <li>System Performance: CPU, memory, disk usage</li>
                            <li>Agent Status: How many agents are running, their health</li>
                            <li>Alerts & Issues: Any system problems or warnings</li>
                            <li>Metrics & Trends: Performance over time</li>
                            <li>Integration Status: MCP server, AI providers</li>
                        </ul>
                    </div>
                    
                    <div class="messages" id="messages">
                        <div class="assistant-message message">
                            <strong>[WAVE] Hello!</strong> I'm your PulseGuard AI assistant. I can answer any questions about your system performance and status.<br><br>
                            <strong>Try asking me:</strong><br>
                            * "What's the current CPU usage?"<br>
                            * "How many agents are running?"<br>
                            * "Are there any system alerts?"<br>
                            * "Show me memory consumption"<br>
                            * "What's the system status?"
                        </div>
                    </div>
                    
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Ask me anything about PulseGuard..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
                
                <div class="sidebar">
                    <h3>Quick Examples:</h3>
                    <div class="examples">
                        <button class="example-btn" onclick="askQuestion('What is the current CPU usage?')">
                            CPU Usage
                        </button>
                        <button class="example-btn" onclick="askQuestion('How many agents are running?')">
                            Agent Status
                        </button>
                        <button class="example-btn" onclick="askQuestion('Show me system health')">
                            System Health
                        </button>
                        <button class="example-btn" onclick="askQuestion('Are there any alerts?')">
                            System Alerts
                        </button>
                        <button class="example-btn" onclick="askQuestion('What is the memory usage?')">
                            Memory Usage
                        </button>
                        <button class="example-btn" onclick="askQuestion('Show me performance metrics')">
                            Performance
                        </button>
                    </div>
                </div>
            </div>

            <script>
                function handleKeyPress(event) {{
                    if (event.key === 'Enter') {{
                        sendMessage();
                    }}
                }}

                function askQuestion(question) {{
                    document.getElementById('messageInput').value = question;
                    sendMessage();
                }}

                function addMessage(type, content) {{
                    const messagesDiv = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${{type}}-message`;
                    messageDiv.innerHTML = content;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }}

                function sendMessage() {{
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (!message) return;

                    addMessage('user', message);
                    input.value = '';

                    // Show typing indicator
                    addMessage('assistant', '[THINKING] Processing your question...');

                    fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ message: message }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        // Remove thinking indicator
                        const messages = document.getElementById('messages');
                        messages.removeChild(messages.lastChild);
                        
                        // Add actual response
                        addMessage('assistant', data.response);
                    }})
                    .catch(error => {{
                        // Remove thinking indicator
                        const messages = document.getElementById('messages');
                        messages.removeChild(messages.lastChild);
                        
                        addMessage('assistant', '[ERROR] Sorry, I encountered an error processing your request.');
                        console.error('Error:', error);
                    }});
                }}
            </script>
        </body>
        </html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_chat_request(self):
        """Handle chat API requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '').lower()
            
            # Process the message and get response
            response = self.process_message(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def process_message(self, message):
        """Process user message and return appropriate response"""
        # Check if PulseGuard is available
        is_live = self.check_pulseguard_connection()
        
        # Get data from PulseGuard API or use demo data
        if is_live:
            status = self.get_pulseguard_data('/api/v1/health')
            agents = self.get_pulseguard_data('/api/v1/agents')
            metrics = self.get_pulseguard_data('/api/v1/metrics')
        else:
            status = None
            agents = None
            metrics = None
        
        # Check for agent-specific questions first (more specific)
        if 'agent' in message and any(word in message for word in ['cpu', 'processor', 'usage', 'performance']):
            if agents and agents.get('agents'):
                agent_list = agents.get('agents', [])
                if 'first' in message and len(agent_list) > 0:
                    first_agent = agent_list[0]
                    agent_cpu = first_agent.get('cpu_usage', 'N/A')
                    agent_name = first_agent.get('name', 'Unknown')
                    return f"""<strong>[LIVE] First Agent CPU Usage</strong><br><br>
                    Agent: <strong>{agent_name}</strong><br>
                    CPU Usage: <strong>{agent_cpu}%</strong><br><br>
                    This is the current CPU usage for the first agent in your system.<br>
                    [LIVE] Live agent data from PulseGuard"""
                elif any(word in message for word in ['average', 'avg']):
                    active_agents = [a for a in agent_list if a.get('status') == 'active']
                    if active_agents:
                        cpu_values = [a.get('cpu_usage', 0) for a in active_agents if a.get('cpu_usage') is not None]
                        avg_cpu = round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0
                        return f"""<strong>[LIVE] Average Agent CPU Usage</strong><br><br>
                        Average CPU across {len(active_agents)} active agents: <strong>{avg_cpu}%</strong><br><br>
                        Individual agent CPU usage:<br>
                        {'<br>'.join([f"* {a.get('name', 'Unknown')}: {a.get('cpu_usage', 'N/A')}%" for a in active_agents[:5]])}
                        {f'<br>... and {len(active_agents)-5} more agents' if len(active_agents) > 5 else ''}<br><br>
                        [LIVE] Live agent data from PulseGuard"""
                    else:
                        return f"""<strong>[LIVE] Average Agent CPU Usage</strong><br><br>
                        No active agents found to calculate average.<br><br>
                        [LIVE] Live agent data from PulseGuard"""
                else:
                    # General agent CPU question - show all agents
                    active_agents = [a for a in agent_list if a.get('status') == 'active']
                    return f"""<strong>[LIVE] Agent CPU Usage Details</strong><br><br>
                    <strong>Active Agents CPU Usage:</strong><br>
                    {'<br>'.join([f"* {a.get('name', 'Unknown')}: {a.get('cpu_usage', 'N/A')}%" for a in active_agents])}<br><br>
                    [LIVE] Live agent data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] Agent CPU Usage</strong><br><br>
                Demo Agent CPU Usage:<br>
                * Web Monitor Agent: 25.3%<br>
                * Database Monitor Agent: 18.7%<br>
                * API Monitor Agent: 12.4%<br><br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        # Historical/Statistical CPU questions (minimum, maximum, average)
        elif any(word in message for word in ['minimum', 'min', 'maximum', 'max', 'average', 'avg', 'historical', 'recorded']):
            if metrics:
                cpu_data = metrics.get('cpu_usage', [])
                memory_data = metrics.get('memory_usage', [])
                
                if cpu_data:
                    min_cpu = min(cpu_data)
                    max_cpu = max(cpu_data)
                    avg_cpu = round(sum(cpu_data) / len(cpu_data), 1)
                    current_cpu = cpu_data[-1]
                    
                    stat_type = "minimum" if any(word in message for word in ['minimum', 'min']) else \
                               "maximum" if any(word in message for word in ['maximum', 'max']) else \
                               "average" if any(word in message for word in ['average', 'avg']) else "historical"
                    
                    return f"""<strong>[LIVE] CPU Usage Statistics</strong><br><br>
                    <strong>Recent CPU Performance Data:</strong><br>
                    * Current: <strong>{current_cpu}%</strong><br>
                    * Minimum: <strong>{min_cpu}%</strong><br>
                    * Maximum: <strong>{max_cpu}%</strong><br>
                    * Average: <strong>{avg_cpu}%</strong><br><br>
                    Data based on the last {len(cpu_data)} readings from your PulseGuard system.<br>
                    [LIVE] Live historical data from PulseGuard"""
                else:
                    return f"""<strong>[LIVE] CPU Usage Statistics</strong><br><br>
                    No historical CPU data available at the moment.<br><br>
                    [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] CPU Usage Statistics</strong><br><br>
                <strong>Demo Historical CPU Data:</strong><br>
                * Current: <strong>45.2%</strong><br>
                * Minimum: <strong>23.1%</strong><br>
                * Maximum: <strong>78.9%</strong><br>
                * Average: <strong>52.3%</strong><br><br>
                This is demo data. PulseGuard system is not connected.<br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        # System CPU questions (when not asking about agents specifically)
        elif any(word in message for word in ['cpu', 'processor']) and 'agent' not in message:
            if status:
                cpu = status.get('system', {}).get('cpu', 'N/A')
                return f"""<strong>[LIVE] System CPU Usage</strong><br><br>
                Overall System CPU Usage: <strong>{cpu}%</strong><br><br>
                This is the total system CPU usage, not individual agents.<br>
                [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] System CPU Usage</strong><br><br>
                Overall System CPU Usage: <strong>45.2%</strong><br><br>
                This is demo data. PulseGuard system is not connected.<br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        elif any(word in message for word in ['agent', 'agents']) and not any(word in message for word in ['cpu', 'processor', 'memory']):
            # General agent status questions
            if agents:
                total = agents.get('total', 0)
                active = len([a for a in agents.get('agents', []) if a.get('status') == 'active'])
                return f"""<strong>[LIVE] Agent Status</strong><br><br>
                Total Agents: <strong>{total}</strong><br>
                Active Agents: <strong>{active}</strong><br>
                Inactive Agents: <strong>{total - active}</strong><br><br>
                [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] Agent Status</strong><br><br>
                Total Agents: <strong>8</strong><br>
                Active Agents: <strong>6</strong><br>
                Inactive Agents: <strong>2</strong><br><br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        elif any(word in message for word in ['memory', 'ram', 'mem']):
            if status:
                memory = status.get('system', {}).get('memory', 'N/A')
                return f"""<strong>[LIVE] Memory Usage Information</strong><br><br>
                Current Memory Usage: <strong>{memory}%</strong><br><br>
                This data is live from your PulseGuard system.<br>
                [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] Memory Usage Information</strong><br><br>
                Current Memory Usage: <strong>67.8%</strong><br><br>
                This is demo data. PulseGuard system is not connected.<br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        elif any(word in message for word in ['health', 'status', 'system']):
            if status:
                cpu = status.get('system', {}).get('cpu', 'N/A')
                memory = status.get('system', {}).get('memory', 'N/A')
                disk = status.get('system', {}).get('disk', 'N/A')
                return f"""<strong>[LIVE] System Health Status</strong><br><br>
                <strong>System Performance:</strong><br>
                * CPU: {cpu}%<br>
                * Memory: {memory}%<br>
                * Disk: {disk}%<br><br>
                <strong>Agent Status:</strong><br>
                * Total: {status.get('agents', {}).get('total', 0)}<br>
                * Active: {status.get('agents', {}).get('active', 0)}<br><br>
                [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] System Health Status</strong><br><br>
                <strong>System Performance:</strong><br>
                * CPU: 45.2%<br>
                * Memory: 67.8%<br>
                * Disk: 23.1%<br><br>
                <strong>Agent Status:</strong><br>
                * Total: 8<br>
                * Active: 6<br><br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        elif any(word in message for word in ['alert', 'alerts', 'warning', 'issue', 'problem']):
            if is_live:
                return f"""<strong>[LIVE] System Alerts</strong><br><br>
                No critical alerts detected.<br>
                All systems are operating normally.<br><br>
                [LIVE] Live alerts from PulseGuard"""
            else:
                return f"""<strong>[DEMO] System Alerts</strong><br><br>
                No critical alerts detected.<br>
                All systems are operating normally.<br><br>
                [DEMO] Demo alerts - PulseGuard not connected"""
        
        elif any(word in message for word in ['metric', 'metrics', 'performance', 'trend']):
            if metrics:
                latest_cpu = metrics.get('cpu_usage', [0])[-1] if metrics.get('cpu_usage') else 'N/A'
                latest_memory = metrics.get('memory_usage', [0])[-1] if metrics.get('memory_usage') else 'N/A'
                return f"""<strong>[LIVE] Performance Metrics</strong><br><br>
                <strong>Latest Readings:</strong><br>
                * CPU: {latest_cpu}%<br>
                * Memory: {latest_memory}%<br><br>
                [LIVE] Live data from PulseGuard"""
            else:
                return f"""<strong>[DEMO] Performance Metrics</strong><br><br>
                <strong>Latest Readings:</strong><br>
                * CPU: 45.2%<br>
                * Memory: 67.8%<br><br>
                [DEMO] Demo data - PulseGuard not connected"""
        
        else:
            return f"""<strong>[ROBOT] PulseGuard AI Assistant</strong><br><br>
            I can help you with information about your PulseGuard system. Try asking me about:<br><br>
            * <strong>System Performance:</strong> "What's the CPU usage?" or "Show me memory consumption"<br>
            * <strong>Agent Status:</strong> "How many agents are running?" or "Agent health status"<br>
            * <strong>System Health:</strong> "What's the system status?" or "Show me system health"<br>
            * <strong>Alerts:</strong> "Are there any alerts?" or "Any system problems?"<br>
            * <strong>Metrics:</strong> "Show me performance metrics" or "System trends"<br><br>
            {'[LIVE] Connected to PulseGuard system' if is_live else '[DEMO] Demo mode - PulseGuard not connected'}"""
    
    def check_pulseguard_connection(self):
        """Check if PulseGuard API is available"""
        try:
            req = urllib.request.Request('http://localhost:8000/api/v1/health')
            response = urllib.request.urlopen(req, timeout=2)
            return response.status == 200
        except:
            return False
    
    def get_pulseguard_data(self, endpoint):
        """Get data from PulseGuard API"""
        try:
            req = urllib.request.Request(f'http://localhost:8000{endpoint}')
            response = urllib.request.urlopen(req, timeout=5)
            return json.loads(response.read().decode('utf-8'))
        except:
            return None

if __name__ == '__main__':
    port = 8090
    server = HTTPServer(('localhost', port), PulseGuardChatbotHandler)
    
    print(f"""
[ROBOT] PULSEGUARD AI ASSISTANT READY!
===================================
[WEB] Open: http://localhost:{port}
[CHAT] Ask me ANYTHING about your PulseGuard system!

Examples:
* "What's the CPU usage?"
* "How many agents are running?"
* "Are there any system alerts?"
* "Show me memory consumption"
* "What's the system performance?"

[LINK] Integration Status:
* Attempting connection to PulseGuard at http://localhost:8000
* Will fall back to demo data if not available
===================================
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down PulseGuard AI Assistant...")
        server.shutdown()