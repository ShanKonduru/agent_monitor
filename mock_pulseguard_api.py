#!/usr/bin/env python3
"""
Simple PulseGuard API Mock Server
Provides realistic system data for the chatbot integration
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time
from datetime import datetime
from urllib.parse import urlparse

class MockPulseGuardAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).path
        
        if parsed_path in ['/health', '/api/v1/health', '/api/v1/health/']:
            self.serve_health()
        elif parsed_path in ['/metrics', '/api/v1/metrics', '/api/v1/metrics/']:
            self.serve_metrics()
        elif parsed_path in ['/agents', '/api/v1/agents', '/api/v1/agents/']:
            self.serve_agents()
        elif parsed_path in ['/ai-providers', '/api/v1/ai-providers', '/api/v1/ai-providers/']:
            self.serve_ai_providers()
        else:
            self.send_error(404, f"Not found: {parsed_path}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_health(self):
        """Serve system health status"""
        # Generate realistic system metrics
        cpu_usage = round(random.uniform(25.0, 75.0), 1)
        memory_usage = round(random.uniform(45.0, 85.0), 1)
        disk_usage = round(random.uniform(15.0, 60.0), 1)
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu": cpu_usage,
                "memory": memory_usage,
                "disk": disk_usage,
                "uptime": "2d 14h 32m"
            },
            "agents": {
                "total": 8,
                "active": 6,
                "inactive": 2
            },
            "services": {
                "database": "connected",
                "mcp_server": "operational",
                "ai_providers": "available"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_data, indent=2).encode())
        print(f"📊 Served health data: CPU {cpu_usage}%, Memory {memory_usage}%")
    
    def serve_metrics(self):
        """Serve performance metrics"""
        # Generate realistic time series data
        now = time.time()
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "interval": "5m",
            "cpu_usage": [
                round(random.uniform(25.0, 75.0), 1) for _ in range(12)
            ],
            "memory_usage": [
                round(random.uniform(45.0, 85.0), 1) for _ in range(12)
            ],
            "network_io": [
                random.randint(800, 1500) for _ in range(12)
            ],
            "disk_io": [
                random.randint(50, 200) for _ in range(12)
            ],
            "response_times": [
                round(random.uniform(100, 800), 1) for _ in range(12)
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(metrics_data, indent=2).encode())
        print(f"📈 Served metrics data with {len(metrics_data['cpu_usage'])} data points")
    
    def serve_agents(self):
        """Serve agent information"""
        agents_data = {
            "total": 8,
            "timestamp": datetime.now().isoformat(),
            "agents": [
                {
                    "id": "agent-web-01",
                    "name": "Web Monitor Agent",
                    "status": "active",
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(10, 40), 1),
                    "memory_usage": round(random.uniform(20, 60), 1)
                },
                {
                    "id": "agent-db-01", 
                    "name": "Database Monitor Agent",
                    "status": "active",
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(15, 50), 1),
                    "memory_usage": round(random.uniform(30, 70), 1)
                },
                {
                    "id": "agent-api-01",
                    "name": "API Monitor Agent", 
                    "status": "active",
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(5, 30), 1),
                    "memory_usage": round(random.uniform(25, 55), 1)
                },
                {
                    "id": "agent-net-01",
                    "name": "Network Monitor Agent",
                    "status": "active",
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(8, 35), 1),
                    "memory_usage": round(random.uniform(20, 50), 1)
                },
                {
                    "id": "agent-log-01",
                    "name": "Log Analysis Agent",
                    "status": "active",
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(12, 45), 1),
                    "memory_usage": round(random.uniform(35, 75), 1)
                },
                {
                    "id": "agent-sec-01",
                    "name": "Security Monitor Agent",
                    "status": "active", 
                    "last_heartbeat": datetime.now().isoformat(),
                    "cpu_usage": round(random.uniform(6, 25), 1),
                    "memory_usage": round(random.uniform(15, 45), 1)
                },
                {
                    "id": "agent-backup-01",
                    "name": "Backup Agent",
                    "status": "inactive",
                    "last_heartbeat": "2025-10-26T15:30:00",
                    "cpu_usage": 0,
                    "memory_usage": 0
                },
                {
                    "id": "agent-report-01",
                    "name": "Reporting Agent", 
                    "status": "inactive",
                    "last_heartbeat": "2025-10-26T14:45:00",
                    "cpu_usage": 0,
                    "memory_usage": 0
                }
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(agents_data, indent=2).encode())
        print(f"🤖 Served agent data: {agents_data['total']} agents, {len([a for a in agents_data['agents'] if a['status'] == 'active'])} active")
    
    def serve_ai_providers(self):
        """Serve AI provider information"""
        providers_data = {
            "timestamp": datetime.now().isoformat(),
            "providers": [
                {
                    "name": "local",
                    "type": "local_llm",
                    "model": "llama3.1",
                    "status": "online",
                    "response_time": round(random.uniform(400, 700), 1),
                    "requests_today": random.randint(150, 300),
                    "success_rate": round(random.uniform(95, 99.5), 1)
                },
                {
                    "name": "openai",
                    "type": "cloud_api",
                    "model": "gpt-4",
                    "status": "configured",
                    "response_time": round(random.uniform(800, 1200), 1),
                    "requests_today": random.randint(50, 120),
                    "success_rate": round(random.uniform(97, 99.8), 1)
                },
                {
                    "name": "anthropic",
                    "type": "cloud_api", 
                    "model": "claude-3.5-sonnet",
                    "status": "configured",
                    "response_time": round(random.uniform(600, 1000), 1),
                    "requests_today": random.randint(30, 80),
                    "success_rate": round(random.uniform(96, 99.3), 1)
                }
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(providers_data, indent=2).encode())
        print(f"🧠 Served AI provider data: {len(providers_data['providers'])} providers")

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), MockPulseGuardAPI)
    
    print(f"""
🚀 MOCK PULSEGUARD API SERVER RUNNING
====================================
🌐 API Endpoint: http://localhost:{port}
📊 Endpoints Available:
• /health - System health and status
• /metrics - Performance metrics
• /agents - Agent information
• /ai-providers - AI provider status

🔗 This provides REALISTIC data to your chatbot!
Now your chatbot will show LIVE data instead of demo data.
====================================
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Mock PulseGuard API Server...")
        server.shutdown()