#!/usr/bin/env python3
"""
Ultra-simple test server for PulseGuard dashboard
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse as urlparse
import os

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)
    
    def do_GET(self):
        if self.path == '/dashboard':
            self.path = '/pulseguard-enterprise-dashboard.html'
            return super().do_GET()
        elif self.path == '/api/v1/agents/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Mock agent data
            agents = [
                {
                    "id": "agent-1",
                    "name": "Docker Test Agent",
                    "type": "LLM_AGENT",
                    "status": "ONLINE",
                    "last_seen": "2025-10-23T01:00:00Z",
                    "environment": "docker",
                    "health_score": 0.8
                },
                {
                    "id": "agent-2", 
                    "name": "LLM Agent - Live Demo",
                    "type": "LLM_AGENT",
                    "status": "ONLINE",
                    "last_seen": "2025-10-23T01:00:00Z",
                    "environment": "production",
                    "health_score": 0.95
                },
                {
                    "id": "agent-3",
                    "name": "System Monitor",
                    "type": "SYSTEM_AGENT", 
                    "status": "ONLINE",
                    "last_seen": "2025-10-23T01:00:00Z",
                    "environment": "production",
                    "health_score": 0.88
                }
            ]
            
            self.wfile.write(json.dumps(agents).encode())
            return
        else:
            return super().do_GET()

if __name__ == '__main__':
    print("🚀 Starting Ultra-Simple PulseGuard Dashboard Server...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📡 API: http://localhost:8000/api/v1/agents/")
    print()
    
    server = HTTPServer(('localhost', 8000), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()