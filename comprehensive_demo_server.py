#!/usr/bin/env python3
"""
Comprehensive Demo Server - Chatbot + MCP + PulseGuard Integration
Demonstrates the complete integration between all Phase 6 components
"""

import sys
import os
sys.path.append('src')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timezone
import json
import asyncio

# Import our integrated components
from api.mcp_router import router as mcp_router
from api.chatbot_router import router as chatbot_router
from mcp.mcp_server import MCPServer
from chatbot.chatbot_core import ChatbotCore
from ai_providers.provider_manager import AIProviderManager

app = FastAPI(
    title="PulseGuard Agent Monitor - Complete Integration Demo",
    description="Comprehensive demo of MCP Server, Chatbot, and AI Provider integration",
    version="1.0.0"
)

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

# Global instances
mcp_server = None
chatbot_core = None
ai_provider_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize all integrated components"""
    global mcp_server, chatbot_core, ai_provider_manager
    
    print("🚀 STARTING PULSEGUARD COMPREHENSIVE DEMO")
    print("=" * 60)
    
    try:
        # Initialize AI Provider Manager
        print("🧠 Initializing AI Provider Manager...")
        ai_provider_manager = AIProviderManager()
        await ai_provider_manager.initialize()
        print("✅ AI Provider Manager initialized")
        
        # Initialize MCP Server
        print("📡 Initializing MCP Server...")
        mcp_server = MCPServer()
        await mcp_server.start()
        print("✅ MCP Server started")
        
        # Initialize Chatbot Core with MCP integration
        print("🤖 Initializing Chatbot Core...")
        chatbot_core = ChatbotCore(
            ai_provider_manager=ai_provider_manager,
            mcp_server=mcp_server
        )
        print("✅ Chatbot Core initialized with MCP integration")
        
        # Register chatbot as an MCP agent
        await mcp_server.register_agent(
            agent_id="chatbot_demo",
            agent_type="chatbot",
            metadata={"version": "1.0.0", "capabilities": ["chat", "commands", "ai_integration"]}
        )
        print("✅ Chatbot registered with MCP Server")
        
        print("\n🎯 ALL COMPONENTS INITIALIZED SUCCESSFULLY!")
        print("📱 Chatbot Interface: http://localhost:8000/chat")
        print("📊 PulseGuard Dashboard: http://localhost:8000/dashboard")
        print("🔧 API Documentation: http://localhost:8000/docs")
        print("📡 MCP Server Status: http://localhost:8000/api/v1/mcp/status")
        print("🤖 Chat API: http://localhost:8000/api/v1/chat/sessions")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mcp_server
    print("🛑 Shutting down components...")
    if mcp_server:
        await mcp_server.stop()
    print("✅ Shutdown complete")

# Include routers
app.include_router(mcp_router, prefix="/api/v1", tags=["MCP"])
app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with navigation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PulseGuard Integration Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .card { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0f3460; }
            .button { background: #0f3460; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px; }
            .button:hover { background: #533483; }
            .feature { margin: 10px 0; }
            .status { background: #2d5a27; padding: 10px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 PulseGuard Agent Monitor</h1>
                <h2>Complete Integration Demo</h2>
                <p>Phase 6.1-6.3: AI Providers + MCP Server + Chatbot Interface</p>
            </div>
            
            <div class="card">
                <h3>🤖 Chatbot Interface (Phase 6.3)</h3>
                <p>Interactive AI-powered chatbot with MCP integration</p>
                <div class="feature">✅ 22 Commands (AI, Context, Session, System)</div>
                <div class="feature">✅ Multi-provider AI support (Local, OpenAI, Anthropic)</div>
                <div class="feature">✅ Real-time MCP context sharing</div>
                <a href="/static/chatbot.html" class="button">Open Chatbot 💬</a>
            </div>
            
            <div class="card">
                <h3>📡 MCP Server (Phase 6.2)</h3>
                <p>Model Context Protocol for agent communication</p>
                <div class="feature">✅ Agent registration and discovery</div>
                <div class="feature">✅ Context sharing between agents</div>
                <div class="feature">✅ Conversation threading and memory</div>
                <a href="/api/v1/mcp/status" class="button">MCP Status 📊</a>
                <a href="/docs#/MCP" class="button">MCP API 🔧</a>
            </div>
            
            <div class="card">
                <h3>🧠 AI Provider System (Phase 6.1)</h3>
                <p>Multi-provider AI abstraction with load balancing</p>
                <div class="feature">✅ OpenAI, Anthropic, Local LLM support</div>
                <div class="feature">✅ Provider health monitoring</div>
                <div class="feature">✅ Performance tracking and metrics</div>
                <a href="/dashboard" class="button">Dashboard 📈</a>
                <a href="/docs#/Chatbot" class="button">Chat API 🔧</a>
            </div>
            
            <div class="card">
                <h3>🔗 Integration Features</h3>
                <div class="feature">🔄 Chatbot ↔ MCP Server communication</div>
                <div class="feature">🧠 AI responses with context sharing</div>
                <div class="feature">📝 Persistent conversation storage</div>
                <div class="feature">📊 Real-time system metrics</div>
                <a href="/docs" class="button">Full API Docs 📚</a>
            </div>
            
            <div class="status">
                <strong>🎯 System Status:</strong> All components operational and integrated!
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/chat", response_class=HTMLResponse)
async def chatbot_interface():
    """Serve chatbot interface"""
    try:
        chatbot_path = os.path.join("web", "chatbot.html")
        if os.path.exists(chatbot_path):
            return FileResponse(chatbot_path)
        else:
            raise HTTPException(status_code=404, detail="Chatbot interface not found")
    except Exception as e:
        return HTMLResponse(f"<h1>Error loading chatbot: {e}</h1>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve PulseGuard dashboard"""
    try:
        dashboard_path = os.path.join("web", "pulseguard-enterprise-dashboard.html")
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path)
        else:
            # Return a simple dashboard if the file doesn't exist
            return HTMLResponse("""
            <html>
            <head><title>PulseGuard Dashboard</title></head>
            <body style="font-family: Arial; margin: 40px; background: #1a1a2e; color: white;">
                <h1>📊 PulseGuard Dashboard</h1>
                <p>Enterprise dashboard for agent monitoring</p>
                <a href="/api/v1/mcp/status" style="color: #4CAF50;">MCP Server Status</a> |
                <a href="/docs" style="color: #2196F3;">API Documentation</a> |
                <a href="/chat" style="color: #FF9800;">Chatbot Interface</a>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(f"<h1>Dashboard Error: {e}</h1>", status_code=500)

@app.get("/api/v1/system/integration-status")
async def integration_status():
    """Get integration status of all components"""
    status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "ai_provider_manager": {
                "status": "operational" if ai_provider_manager else "not_initialized",
                "providers": len(ai_provider_manager.providers) if ai_provider_manager else 0
            },
            "mcp_server": {
                "status": "operational" if mcp_server else "not_initialized",
                "active_agents": len(getattr(mcp_server, 'agents', {})) if mcp_server else 0
            },
            "chatbot_core": {
                "status": "operational" if chatbot_core else "not_initialized",
                "active_sessions": len(getattr(chatbot_core, 'sessions', {})) if chatbot_core else 0
            }
        },
        "integration": {
            "mcp_chatbot": "connected" if (mcp_server and chatbot_core) else "disconnected",
            "ai_chatbot": "connected" if (ai_provider_manager and chatbot_core) else "disconnected"
        }
    }
    return status

if __name__ == "__main__":
    print("🚀 Starting PulseGuard Comprehensive Demo Server...")
    print("🔗 This demonstrates complete integration between:")
    print("   • Phase 6.1: AI Provider Manager")
    print("   • Phase 6.2: MCP Server") 
    print("   • Phase 6.3: Chatbot Interface")
    print("   • PulseGuard Dashboard")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )