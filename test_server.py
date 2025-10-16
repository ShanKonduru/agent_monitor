"""
Simple test server to verify the monitoring framework works
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    print("✅ FastAPI imports successful")
    
    # Create a simple test app
    app = FastAPI(title="Agent Monitor Test", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Agent Monitor Framework is running!", "status": "ok"}
    
    @app.get("/api/v1/system/status")
    async def system_status():
        return {
            "status": "healthy",
            "uptime_seconds": 100,
            "total_agents": 0,
            "active_agents": 0,
            "framework_version": "1.0.0"
        }
    
    @app.post("/api/v1/agents/register")
    async def register_agent(agent_data: dict):
        # Simple mock registration
        agent_id = "test-agent-123"
        return {
            "agent_id": agent_id,
            "status": "registered",
            "message": "Agent registered successfully"
        }
    
    @app.post("/api/v1/agents/{agent_id}/heartbeat")
    async def heartbeat(agent_id: str):
        return {"status": "ok", "message": "Heartbeat received"}
    
    @app.post("/api/v1/agents/{agent_id}/metrics")
    async def receive_metrics(agent_id: str, metrics: dict):
        return {"status": "ok", "message": "Metrics received"}
    
    print("✅ Test server created successfully")
    
    if __name__ == "__main__":
        print("🚀 Starting test server on http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)