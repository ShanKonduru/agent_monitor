#!/usr/bin/env python3
"""
Working Dashboard Server - Provides mock API data and serves enhanced dashboard
Designed to bypass database connection issues and provide working demo
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime, timezone
import json

app = FastAPI(title="Working Agent Monitor API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

# Mock agent data with realistic LLM agents
mock_agents = [
    {
        "id": "llm-agent-1",
        "name": "🤖 GPT-4 Production Agent",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "environment": "production",
        "health_score": 0.95,
        "version": "1.0.0",
        "description": "Advanced language model for production workloads"
    },
    {
        "id": "llm-agent-2", 
        "name": "🤖 Claude-3 Research Agent",
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "environment": "production",
        "health_score": 0.92,
        "version": "1.0.0",
        "description": "Anthropic's Claude for research and analysis"
    },
    {
        "id": "llm-agent-3",
        "name": "🤖 Llama-2 Local Agent", 
        "type": "LLM_AGENT",
        "status": "ONLINE",
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "environment": "production",
        "health_score": 0.88,
        "version": "1.0.0",
        "description": "Local Llama-2 model for private inference"
    },
    {
        "id": "api-agent-1",
        "name": "🔌 API Gateway Agent",
        "type": "API_AGENT", 
        "status": "ONLINE",
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "environment": "production",
        "health_score": 0.97,
        "version": "1.0.0",
        "description": "API routing and load balancing"
    },
    {
        "id": "data-agent-1",
        "name": "📊 Data Processing Agent",
        "type": "DATA_AGENT",
        "status": "ONLINE", 
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "environment": "production",
        "health_score": 0.90,
        "version": "1.0.0",
        "description": "ETL and data transformation pipeline"
    }
]

# Mock AI metrics for LLM agents
mock_ai_metrics = {
    "llm-agent-1": {
        "tokens_processed": 1250000,
        "model_accuracy": 0.94,
        "model_inference_time_ms": 145.2,
        "tokens_per_second": 850.3,
        "context_length": 8192,
        "api_call_latency_ms": 89.7
    },
    "llm-agent-2": {
        "tokens_processed": 987000,
        "model_accuracy": 0.91,
        "model_inference_time_ms": 178.5,
        "tokens_per_second": 720.1,
        "context_length": 4096,
        "api_call_latency_ms": 112.3
    },
    "llm-agent-3": {
        "tokens_processed": 654000,
        "model_accuracy": 0.87,
        "model_inference_time_ms": 220.8,
        "tokens_per_second": 445.6,
        "context_length": 2048,
        "api_call_latency_ms": 45.2
    }
}

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

@app.get("/api/v1/agents/{agent_id}/ai-metrics")
async def get_agent_ai_metrics(agent_id: str):
    """Get AI metrics for specific agent"""
    if agent_id in mock_ai_metrics:
        return {
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_metrics": mock_ai_metrics[agent_id]
        }
    return {"error": "AI metrics not found for agent"}, 404

@app.get("/api/v1/system/ai-metrics")
async def get_system_ai_metrics():
    """Get aggregated AI metrics for all LLM agents"""
    total_tokens = sum(metrics["tokens_processed"] for metrics in mock_ai_metrics.values())
    avg_accuracy = sum(metrics["model_accuracy"] for metrics in mock_ai_metrics.values()) / len(mock_ai_metrics)
    avg_latency = sum(metrics["api_call_latency_ms"] for metrics in mock_ai_metrics.values()) / len(mock_ai_metrics)
    total_throughput = sum(metrics["tokens_per_second"] for metrics in mock_ai_metrics.values())
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_llm_agents": len(mock_ai_metrics),
        "total_tokens_processed": total_tokens,
        "avg_model_accuracy": round(avg_accuracy, 3),
        "avg_api_latency_ms": round(avg_latency, 1),
        "total_tokens_per_second": round(total_throughput, 1),
        "agents": list(mock_ai_metrics.keys())
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents_count": len(mock_agents),
        "llm_agents_count": len(mock_ai_metrics)
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the enhanced dashboard"""
    dashboard_paths = [
        "web/pulseguard-enterprise-dashboard.html",
        "web/basic-agent-monitor-dashboard.html"
    ]
    
    for path in dashboard_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Serving dashboard from {path}")
                return content
            except Exception as e:
                print(f"❌ Could not serve {path}: {e}")
                continue
    
    # Fallback HTML
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard Not Found</title></head>
    <body>
        <h1>Dashboard Files Not Found</h1>
        <p>Available endpoints:</p>
        <ul>
            <li><a href="/docs">API Documentation</a></li>
            <li><a href="/api/v1/agents/">Agents API</a></li>
            <li><a href="/api/v1/system/ai-metrics">AI Metrics API</a></li>
            <li><a href="/static/pulseguard-enterprise-dashboard.html">Static Dashboard</a></li>
        </ul>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Working Dashboard Server...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📊 Static Dashboard: http://localhost:8000/static/pulseguard-enterprise-dashboard.html")
    print("📡 API: http://localhost:8000/api/v1/agents/")
    print("🤖 AI Metrics: http://localhost:8000/api/v1/system/ai-metrics")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )