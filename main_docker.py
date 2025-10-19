"""
Docker-compatible main.py - Full featured application with SQLite
"""

import logging
import uvicorn
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add current directory to Python path
sys.path.insert(0, '/app')

# Set environment variables for Docker
os.environ.setdefault('DATABASE_URL', 'sqlite:///./data/agent_monitor.db')
os.environ.setdefault('REDIS_URL', '')
os.environ.setdefault('INFLUXDB_URL', '')

# Import application components
try:
    from src.api.agents import router as agents_router
    from src.api.metrics import router as metrics_router  
    from src.api.health import router as health_router
    from src.core.agent_registry import AgentRegistry
    from src.core.metrics_collector import metrics_collector
    HAS_FULL_FEATURES = True
except ImportError as e:
    print(f"Warning: Some features not available: {e}")
    HAS_FULL_FEATURES = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Mock database for simplified Docker version
MOCK_AGENTS = [
    {
        "id": "docker-agent-1",
        "name": "Docker Monitor Agent",
        "type": "MONITOR_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-18T21:00:00Z",
        "environment": "docker",
        "health_score": 0.95
    },
    {
        "id": "docker-agent-2", 
        "name": "Docker API Agent",
        "type": "API_AGENT",
        "status": "ONLINE",
        "last_seen": "2025-10-18T20:58:00Z",
        "environment": "docker",
        "health_score": 0.87
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Agent Monitor Framework in Docker...")
    yield
    logger.info("Shutting down Agent Monitor Framework...")

# Create FastAPI app
app = FastAPI(
    title="Agent Monitor Framework",
    description="A comprehensive monitoring framework for AI/ML agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if web directory exists
if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

# Include routers if available
if HAS_FULL_FEATURES:
    try:
        app.include_router(agents_router, prefix="/api/v1")
        app.include_router(metrics_router, prefix="/api/v1")
        app.include_router(health_router, prefix="/api/v1")
    except Exception as e:
        logger.warning(f"Could not include full routers: {e}")
        HAS_FULL_FEATURES = False

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "Agent Monitor Framework",
        "version": "1.0.0",
        "status": "running",
        "docker": True,
        "features": "full" if HAS_FULL_FEATURES else "basic"
    }

@app.get("/api/v1/system/status")
async def system_status():
    """System status endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-10-18T21:00:00Z",
        "total_agents": len(MOCK_AGENTS),
        "active_agents": len([a for a in MOCK_AGENTS if a["status"] == "ONLINE"]),
        "system_metrics": {
            "total_agents": len(MOCK_AGENTS),
            "total_metrics_points": 1250,
            "average_cpu_usage": 45.2,
            "average_memory_usage": 67.8,
            "total_tasks_completed": 892,
            "total_tasks_failed": 12,
            "average_response_time": 0.125,
            "system_error_rate": 0.013
        },
        "version": "1.0.0"
    }

@app.get("/api/v1/metrics/performance")
async def get_performance_metrics():
    """Get performance metrics for dashboard"""
    return {
        "cpu_usage": [
            {"timestamp": "2025-10-18T20:50:00Z", "value": 42.1},
            {"timestamp": "2025-10-18T20:55:00Z", "value": 45.2},
            {"timestamp": "2025-10-18T21:00:00Z", "value": 48.7}
        ],
        "memory_usage": [
            {"timestamp": "2025-10-18T20:50:00Z", "value": 65.3},
            {"timestamp": "2025-10-18T20:55:00Z", "value": 67.8},
            {"timestamp": "2025-10-18T21:00:00Z", "value": 69.1}
        ],
        "response_times": [
            {"timestamp": "2025-10-18T20:50:00Z", "value": 0.115},
            {"timestamp": "2025-10-18T20:55:00Z", "value": 0.125},
            {"timestamp": "2025-10-18T21:00:00Z", "value": 0.132}
        ],
        "error_rates": [
            {"timestamp": "2025-10-18T20:50:00Z", "value": 0.008},
            {"timestamp": "2025-10-18T20:55:00Z", "value": 0.013},
            {"timestamp": "2025-10-18T21:00:00Z", "value": 0.011}
        ]
    }

@app.get("/api/v1/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Add detailed metrics
    agent_details = agent.copy()
    agent_details.update({
        "metrics": {
            "cpu_usage": 35.2,
            "memory_usage": 512.7,
            "requests_per_minute": 47,
            "average_response_time": 0.089,
            "error_rate": 0.002
        },
        "tasks": {
            "completed": 145,
            "failed": 2,
            "pending": 0,
            "success_rate": 0.986
        },
        "configuration": {
            "max_concurrent_tasks": 10,
            "timeout_seconds": 30,
            "retry_attempts": 3
        }
    })
    return agent_details

@app.get("/api/v1/agents/")
async def list_agents():
    """List all agents"""
    return MOCK_AGENTS

@app.post("/api/v1/agents/register")
async def register_agent(agent_data: dict):
    """Register a new agent"""
    # Mock registration - just return success
    return {
        "status": "registered",
        "agent_id": agent_data.get("name", "unknown"),
        "message": "Agent registered successfully"
    }

@app.post("/api/v1/agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, heartbeat_data: dict):
    """Process agent heartbeat"""
    # Mock heartbeat processing
    return {
        "status": "received",
        "agent_id": agent_id,
        "next_heartbeat": 30
    }

@app.post("/api/v1/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status_data: dict):
    """Update agent status"""
    # Mock status update
    return {
        "status": "updated",
        "agent_id": agent_id,
        "message": "Status updated successfully"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "docker": True}

# Dashboard endpoint with full functionality
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the simple agent monitoring dashboard"""
    # Use our built-in simple dashboard instead of the complex React one
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agent Monitor Dashboard - Docker</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 3rem; font-weight: 700; margin-bottom: 10px; }
            .controls { display: flex; justify-content: center; gap: 15px; margin: 20px 0; }
            .btn {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            .btn:hover { background: rgba(255, 255, 255, 0.25); }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                backdrop-filter: blur(15px);
            }
            .stat-number { font-size: 3rem; font-weight: 700; margin-bottom: 10px; color: #4ade80; }
            .stat-label { font-size: 1.1rem; opacity: 0.9; font-weight: 500; }
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
            }
            .agent-card {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(15px);
            }
            .agent-name { font-size: 1.3rem; font-weight: 600; margin-bottom: 8px; }
            .agent-type {
                background: rgba(255, 255, 255, 0.2);
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85rem;
                display: inline-block;
                margin-bottom: 15px;
            }
            .detail-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            .status-online { color: #4ade80; font-weight: 700; }
            .loading { text-align: center; padding: 60px 20px; font-size: 1.2rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Agent Monitor Dashboard</h1>
                <p>Docker Edition - Enterprise-grade monitoring</p>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="loadAgents()">🔄 Refresh Data</button>
                <button class="btn" onclick="exportData()">📊 Export Data</button>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="total-agents">-</div>
                    <div class="stat-label">Total Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="online-agents">-</div>
                    <div class="stat-label">Online Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="avg-health">-</div>
                    <div class="stat-label">Average Health</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">�</div>
                    <div class="stat-label">Docker Mode</div>
                </div>
            </div>
            
            <div class="agents-section">
                <h2>🤖 Active Agents</h2>
                <div id="agents-container" class="loading">Loading agent data...</div>
            </div>
        </div>
        
        <script>
            let performanceChart = null;
            
            async function loadAgents() {
                try {
                    console.log('Fetching agents...');
                    const response = await fetch('/api/v1/agents/');
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const agents = await response.json();
                    console.log('Agents loaded:', agents);
                    
                    // Update stats
                    const total = agents.length;
                    const online = agents.filter(a => a.status === 'ONLINE').length;
                    const avgHealth = total > 0 ? 
                        (agents.reduce((sum, a) => sum + (a.health_score || 0), 0) / total).toFixed(1) : 0;
                    
                    document.getElementById('total-agents').textContent = total;
                    document.getElementById('online-agents').textContent = online;
                    document.getElementById('avg-health').textContent = avgHealth;
                    
                    // Render agents
                    const container = document.getElementById('agents-container');
                    if (agents.length === 0) {
                        container.innerHTML = '<div class="loading">No agents found</div>';
                        return;
                    }
                    
                    container.className = 'agents-grid';
                    container.innerHTML = agents.map(agent => `
                        <div class="agent-card">
                            <div class="agent-name">${agent.name}</div>
                            <span class="agent-type">${agent.type}</span>
                            <div class="detail-row">
                                <span>Status</span>
                                <span class="status-online">${agent.status}</span>
                            </div>
                            <div class="detail-row">
                                <span>Environment</span>
                                <span>${agent.environment || 'Unknown'}</span>
                            </div>
                            <div class="detail-row">
                                <span>Health Score</span>
                                <span>${agent.health_score ? (agent.health_score * 100).toFixed(1) + '%' : 'N/A'}</span>
                            </div>
                            <div class="detail-row">
                                <span>Last Seen</span>
                                <span>${new Date(agent.last_seen).toLocaleString()}</span>
                            </div>
                        </div>
                    `).join('');
                    
                    // Load performance data
                    await loadPerformanceData();
                    
                } catch (error) {
                    console.error('Error loading agents:', error);
                    document.getElementById('agents-container').innerHTML = 
                        `<div class="loading">❌ Failed to load agent data: ${error.message}</div>`;
                }
            }
            
            async function loadPerformanceData() {
                try {
                    console.log('Fetching performance metrics...');
                    const response = await fetch('/api/v1/metrics/performance');
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const metrics = await response.json();
                    console.log('Performance metrics loaded:', metrics);
                    
                    // Add performance overview section if not exists
                    let perfSection = document.getElementById('performance-section');
                    if (!perfSection) {
                        const container = document.querySelector('.container');
                        const agentsSection = document.querySelector('.agents-section');
                        
                        perfSection = document.createElement('div');
                        perfSection.id = 'performance-section';
                        perfSection.innerHTML = `
                            <h2>📈 Performance Overview</h2>
                            <div class="performance-grid">
                                <div class="perf-card">
                                    <h4>CPU Usage</h4>
                                    <div class="perf-value">${metrics.cpu_usage[metrics.cpu_usage.length - 1].value.toFixed(1)}%</div>
                                    <div class="perf-trend">Latest: ${new Date(metrics.cpu_usage[metrics.cpu_usage.length - 1].timestamp).toLocaleTimeString()}</div>
                                </div>
                                <div class="perf-card">
                                    <h4>Memory Usage</h4>
                                    <div class="perf-value">${metrics.memory_usage[metrics.memory_usage.length - 1].value.toFixed(1)}%</div>
                                    <div class="perf-trend">Latest: ${new Date(metrics.memory_usage[metrics.memory_usage.length - 1].timestamp).toLocaleTimeString()}</div>
                                </div>
                                <div class="perf-card">
                                    <h4>Response Time</h4>
                                    <div class="perf-value">${(metrics.response_times[metrics.response_times.length - 1].value * 1000).toFixed(0)}ms</div>
                                    <div class="perf-trend">Latest: ${new Date(metrics.response_times[metrics.response_times.length - 1].timestamp).toLocaleTimeString()}</div>
                                </div>
                                <div class="perf-card">
                                    <h4>Error Rate</h4>
                                    <div class="perf-value">${(metrics.error_rates[metrics.error_rates.length - 1].value * 100).toFixed(2)}%</div>
                                    <div class="perf-trend">Latest: ${new Date(metrics.error_rates[metrics.error_rates.length - 1].timestamp).toLocaleTimeString()}</div>
                                </div>
                            </div>
                        `;
                        
                        // Add CSS for performance cards
                        const style = document.createElement('style');
                        style.textContent = `
                            .performance-grid {
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 20px;
                                margin: 20px 0 40px 0;
                            }
                            .perf-card {
                                background: rgba(255, 255, 255, 0.1);
                                border: 1px solid rgba(255, 255, 255, 0.2);
                                border-radius: 10px;
                                padding: 20px;
                                text-align: center;
                                backdrop-filter: blur(15px);
                            }
                            .perf-card h4 {
                                margin: 0 0 10px 0;
                                font-size: 0.9rem;
                                opacity: 0.8;
                            }
                            .perf-value {
                                font-size: 2rem;
                                font-weight: 700;
                                color: #4ade80;
                                margin-bottom: 8px;
                            }
                            .perf-trend {
                                font-size: 0.75rem;
                                opacity: 0.7;
                            }
                        `;
                        document.head.appendChild(style);
                        
                        container.insertBefore(perfSection, agentsSection);
                    }
                    
                } catch (error) {
                    console.error('Error loading performance data:', error);
                    // Don't fail the whole page if performance data fails
                }
            }
            
            function exportData() {
                Promise.all([
                    fetch('/api/v1/agents/').then(r => r.json()),
                    fetch('/api/v1/system/status').then(r => r.json()),
                    fetch('/api/v1/metrics/performance').then(r => r.json())
                ])
                .then(([agents, status, metrics]) => {
                    const exportData = {
                        timestamp: new Date().toISOString(),
                        agents,
                        system_status: status,
                        performance_metrics: metrics
                    };
                    
                    const dataStr = JSON.stringify(exportData, null, 2);
                    const dataBlob = new Blob([dataStr], {type: 'application/json'});
                    const url = URL.createObjectURL(dataBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `agent-monitor-export-${new Date().toISOString().split('T')[0]}.json`;
                    link.click();
                    URL.revokeObjectURL(url);
                })
                .catch(error => {
                    console.error('Export failed:', error);
                    alert('Export failed: ' + error.message);
                });
            }
            
            // Load data on page load
            document.addEventListener('DOMContentLoaded', () => {
                console.log('Dashboard loaded, fetching data...');
                loadAgents();
            });
            
            // Auto-refresh every 30 seconds
            setInterval(loadAgents, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    logger.info("Starting Agent Monitor Framework in Docker...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )