#!/usr/bin/env python3
"""
PulseGuard Dashboard Server
The ONE and ONLY server you need to run the dashboard
Uses only Python standard library - no external dependencies
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse as urlparse
import os

app = FastAPI(title="Simple Agent Monitor API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock agent data
mock_agents = [
    {
        "id": "c6d0a511-a0ea-4f33-91ec-c70e8f299db0",
        "name": "Docker Test Agent",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-22T22:38:55.923359Z",
        "environment": "docker",
        "health_score": 0.8
    },
    {
        "id": "eb4854c2-1d3c-4a06-8e8c-54a189d8735f",
        "name": "LLM Agent - Live Demo",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-22T22:16:47.366753Z",
        "environment": "production",
        "health_score": 0.95
    },
    {
        "id": "74e00029-45ef-40f9-92ee-d0e108b684c9",
        "name": "Fresh LLM Agent",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-22T22:16:54.624850Z",
        "environment": "production",
        "health_score": 0.87
    },
    {
        "id": "b3daa0f9-4fa1-4580-8cec-a87281ccecde",
        "name": "GPT-4 Simulator",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-22T22:16:53.859562Z",
        "environment": "production",
        "health_score": 0.92
    },
    {
        "id": "system-1",
        "name": "System Monitor",
        "type": "SYSTEM_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-22T22:17:01.108629Z",
        "environment": "production",
        "health_score": 0.78
    }
]

@app.get("/api/v1/agents/")
async def get_agents():
    """Get all agents"""
    return mock_agents

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent"""
    agent = next((a for a in mock_agents if a["id"] == agent_id), None)
    if not agent:
        return {"error": "Agent not found"}, 404
    return agent

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Serve static files
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/dashboard")
async def dashboard():
    """Serve the main dashboard"""
    return FileResponse("web/pulseguard-enterprise-dashboard.html")

@app.get("/test")
async def test_dashboard():
    """Serve the test dashboard"""
    return FileResponse("web/test-dashboard.html")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Simple Agent Monitor API", "dashboard": "/dashboard", "test": "/test"}

if __name__ == "__main__":
    print("🚀 Starting Simple Agent Monitor API Server...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🧪 Test Dashboard: http://localhost:8000/test")
    print("📡 API: http://localhost:8000/api/v1/agents/")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")