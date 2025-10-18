"""
Agent Monitor Framework - Local Development Server
Simplified version for dashboard development
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Agent Monitor Framework - Local Dev",
    description="Local development server for dashboard improvements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for development
MOCK_AGENTS = [
    {
        "id": "agent-001",
        "name": "🖥️ Local Dev Agent 1",
        "type": "API_AGENT",
        "status": "ONLINE",
        "environment": "LOCAL",
        "health_score": 0.95,
        "last_seen": datetime.now().isoformat(),
        "host": "localhost",
        "port": 8001,
        "cpu_usage": 45,
        "memory_usage": 62,
        "response_time": 150,
        "requests_per_minute": 245,
        "error_rate": 0.01
    },
    {
        "id": "agent-002", 
        "name": "🔍 Local Monitor Agent",
        "type": "MONITOR_AGENT",
        "status": "ONLINE",
        "environment": "LOCAL",
        "health_score": 0.88,
        "last_seen": datetime.now().isoformat(),
        "host": "localhost",
        "port": 8002,
        "cpu_usage": 32,
        "memory_usage": 71,
        "response_time": 200,
        "requests_per_minute": 156,
        "error_rate": 0.02
    },
    {
        "id": "agent-003",
        "name": "📊 Local Data Agent",
        "type": "DATA_AGENT", 
        "status": "MAINTENANCE",
        "environment": "LOCAL",
        "health_score": 0.75,
        "last_seen": datetime.now().isoformat(),
        "host": "localhost",
        "port": 8003,
        "cpu_usage": 78,
        "memory_usage": 85,
        "response_time": 450,
        "requests_per_minute": 89,
        "error_rate": 0.05
    },
    {
        "id": "agent-004",
        "name": "🤖 Local ML Agent",
        "type": "CUSTOM",
        "status": "ERROR",
        "environment": "LOCAL", 
        "health_score": 0.45,
        "last_seen": datetime.now().isoformat(),
        "host": "localhost",
        "port": 8004,
        "cpu_usage": 95,
        "memory_usage": 92,
        "response_time": 850,
        "requests_per_minute": 23,
        "error_rate": 0.15
    },
    {
        "id": "agent-005",
        "name": "⚡ Local Fast Agent",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "environment": "LOCAL",
        "health_score": 0.98,
        "last_seen": datetime.now().isoformat(),
        "host": "localhost",
        "port": 8005,
        "cpu_usage": 25,
        "memory_usage": 45,
        "response_time": 75,
        "requests_per_minute": 412,
        "error_rate": 0.001
    }
]

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint"""
    return """
    <html>
        <head>
            <title>Agent Monitor - Local Development</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; margin-bottom: 20px; }
                a { color: #007bff; text-decoration: none; margin-right: 20px; display: inline-block; margin-bottom: 10px; }
                a:hover { text-decoration: underline; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Agent Monitor Framework - Local Development</h1>
                <div class="status">
                    <strong>Status:</strong> Local development server running<br>
                    <strong>Mode:</strong> Dashboard development with mock data
                </div>
                
                <h3>📊 Dashboard & API Links:</h3>
                <a href="/dashboard">🖥️ React Dashboard</a>
                <a href="/docs">📚 API Documentation</a>
                <a href="/api/v1/agents/">🤖 Agents API</a>
                <a href="/api/v1/health">💚 Health Check</a>
                
                <h3>🔧 Development Features:</h3>
                <ul>
                    <li>✅ Auto-reload enabled for code changes</li>
                    <li>✅ Mock agent data for testing</li>
                    <li>✅ CORS enabled for local development</li>
                    <li>✅ Dashboard optimization ready</li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the React dashboard for development"""
    try:
        return FileResponse("web/dashboard.html")
    except Exception as e:
        logger.error(f"Failed to serve dashboard: {e}")
        return HTMLResponse("<h1>Dashboard temporarily unavailable</h1>", status_code=500)

@app.get("/api/v1/agents/")
async def get_agents():
    """Get all agents - using mock data for development"""
    return MOCK_AGENTS

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent"""
    agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "local_development",
        "agents_count": len(MOCK_AGENTS),
        "agents_online": len([a for a in MOCK_AGENTS if a["status"] == "ONLINE"])
    }

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics - mock data"""
    return {
        "system": {
            "cpu_usage": 45.2,
            "memory_usage": 68.5,
            "disk_usage": 72.1,
            "network_io": {"in": 1250, "out": 890}
        },
        "agents": {
            "total": len(MOCK_AGENTS),
            "online": len([a for a in MOCK_AGENTS if a["status"] == "ONLINE"]),
            "offline": len([a for a in MOCK_AGENTS if a["status"] == "OFFLINE"]),
            "error": len([a for a in MOCK_AGENTS if a["status"] == "ERROR"]),
            "maintenance": len([a for a in MOCK_AGENTS if a["status"] == "MAINTENANCE"])
        },
        "performance": {
            "avg_response_time": sum(a["response_time"] for a in MOCK_AGENTS) / len(MOCK_AGENTS),
            "total_requests": sum(a["requests_per_minute"] for a in MOCK_AGENTS),
            "avg_error_rate": sum(a["error_rate"] for a in MOCK_AGENTS) / len(MOCK_AGENTS)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)