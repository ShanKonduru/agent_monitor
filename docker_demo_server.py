#!/usr/bin/env python3
"""
Docker Demo Server - Live data from real agents with PostgreSQL
No Redis, InfluxDB, or complex dependencies - just pure agent monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncpg
import asyncio
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docker Demo Agent Monitor API")

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

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_monitor:agent_monitor_password@localhost:5432/agent_monitor")

class AgentDatabase:
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            await self.create_tables()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            # Continue without database for demo
            pass
    
    async def create_tables(self):
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    last_seen TIMESTAMP WITH TIME ZONE,
                    environment VARCHAR(100),
                    health_score FLOAT,
                    version VARCHAR(50),
                    description TEXT,
                    cpu_usage FLOAT DEFAULT 0,
                    memory_usage FLOAT DEFAULT 0,
                    response_time INTEGER DEFAULT 0,
                    requests_per_minute INTEGER DEFAULT 0,
                    error_rate FLOAT DEFAULT 0,
                    deployment_info JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id SERIAL PRIMARY KEY,
                    agent_id VARCHAR(255) REFERENCES agents(id),
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    cpu_usage FLOAT,
                    memory_usage FLOAT,
                    response_time INTEGER,
                    requests_per_minute INTEGER,
                    error_rate FLOAT,
                    custom_metrics JSONB
                )
            """)
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        if not self.pool:
            return []
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM agents 
                ORDER BY last_seen DESC
            """)
            
            agents = []
            for row in rows:
                agent = dict(row)
                agent['last_seen'] = agent['last_seen'].isoformat() if agent['last_seen'] else None
                agent['created_at'] = agent['created_at'].isoformat() if agent['created_at'] else None
                agent['updated_at'] = agent['updated_at'].isoformat() if agent['updated_at'] else None
                agents.append(agent)
            
            return agents
    
    async def get_agent_trends(self, agent_id: str) -> List[Dict[str, Any]]:
        if not self.pool:
            return []
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM agent_metrics 
                WHERE agent_id = $1 
                ORDER BY timestamp DESC 
                LIMIT 24
            """, agent_id)
            
            trends = []
            for row in rows:
                trend = dict(row)
                trend['timestamp'] = trend['timestamp'].isoformat()
                trends.append(trend)
            
            return trends

# Global database instance
db = AgentDatabase()

@app.on_event("startup")
async def startup_event():
    await db.initialize()
    logger.info("🚀 Docker Demo Server started successfully!")

@app.get("/")
async def root():
    return {"message": "🐳 Docker Demo Agent Monitor", "status": "online"}

@app.get("/api/v1/agents/")
async def get_agents():
    """Get all registered agents from database"""
    agents = await db.get_agents()
    
    # Add computed metrics for display
    for agent in agents:
        # Add deployment info if it exists
        if agent.get('deployment_info'):
            agent['deployment'] = agent['deployment_info']
        
        # Ensure all required fields exist
        agent.setdefault('cpu_usage', 45.2)
        agent.setdefault('memory_usage', 67.8)
        agent.setdefault('response_time', 234)
        agent.setdefault('requests_per_minute', 1250)
        agent.setdefault('error_rate', 0.02)
        
    return agents

@app.get("/api/v1/agents/{agent_id}")
async def get_agent_detail(agent_id: str):
    """Get detailed information for a specific agent"""
    agents = await db.get_agents()
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@app.get("/api/v1/agents/{agent_id}/trends")
async def get_agent_trends(agent_id: str):
    """Get 24-hour trend data for specific agent"""
    trends = await db.get_agent_trends(agent_id)
    
    return {
        "agent_id": agent_id,
        "timeframe": "24h",
        "trends": trends
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get overall system status"""
    agents = await db.get_agents()
    
    online_agents = len([a for a in agents if a['status'] == 'ONLINE'])
    total_agents = len(agents)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_agents": total_agents,
        "online_agents": online_agents,
        "database_connected": db.pool is not None
    }

@app.get("/api/v1/system/deployment-map")
async def get_deployment_map():
    """Get deployment map showing which agents are running on which hosts"""
    agents = await db.get_agents()
    deployment_map = {}
    
    for agent in agents:
        if agent.get('deployment_info'):
            deployment = agent['deployment_info']
            host = deployment.get('host', f"container-{agent['id']}")
            
            if host not in deployment_map:
                deployment_map[host] = {
                    "host": host,
                    "host_ip": deployment.get('host_ip', '172.18.0.x'),
                    "region": deployment.get('region', 'docker-local'),
                    "deployment_type": deployment.get('deployment_type', 'docker'),
                    "cluster": deployment.get('cluster', 'docker-compose'),
                    "agents": []
                }
            
            deployment_map[host]["agents"].append({
                "id": agent['id'],
                "name": agent['name'],
                "type": agent['type'],
                "status": agent['status'],
                "container_id": deployment.get('container_id', f"container-{agent['id'][:8]}")
            })
    
    return {
        "total_hosts": len(deployment_map),
        "total_agents": len(agents),
        "deployment_map": list(deployment_map.values())
    }

@app.get("/dashboard")
async def get_dashboard():
    """Serve the main dashboard"""
    return FileResponse("web/pulseguard-enterprise-dashboard.html")

@app.post("/api/v1/agents/{agent_id}/register")
async def register_agent(agent_id: str, agent_data: dict):
    """Register or update an agent"""
    if not db.pool:
        return {"status": "accepted", "note": "Database not available"}
    
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agents (
                    id, name, type, status, last_seen, environment, 
                    health_score, version, description, deployment_info
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    status = EXCLUDED.status,
                    last_seen = EXCLUDED.last_seen,
                    environment = EXCLUDED.environment,
                    health_score = EXCLUDED.health_score,
                    version = EXCLUDED.version,
                    description = EXCLUDED.description,
                    deployment_info = EXCLUDED.deployment_info,
                    updated_at = NOW()
            """, 
                agent_id,
                agent_data.get('name', 'Unknown Agent'),
                agent_data.get('type', 'UNKNOWN'),
                agent_data.get('status', 'ONLINE'),
                datetime.now(timezone.utc),
                agent_data.get('environment', 'docker'),
                agent_data.get('health_score', 0.95),
                agent_data.get('version', '1.0.0'),
                agent_data.get('description', ''),
                json.dumps(agent_data.get('deployment', {}))
            )
        
        return {"status": "registered", "agent_id": agent_id}
    except Exception as e:
        logger.error(f"Failed to register agent {agent_id}: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🐳 Starting Docker Demo Server...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📡 API: http://localhost:8000/api/v1/agents/")
    print("🗄️ Database: PostgreSQL")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )