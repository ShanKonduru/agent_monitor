"""
Enhanced Agent Monitor Framework - Phase 2 Application
Includes database persistence, advanced features, and production-ready components.
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# Import existing Phase 1 components
from src.config import settings
from src.api.agents import router as agents_router
from src.api.metrics import router as metrics_router  
from src.api.health import router as health_router
from src.core.agent_registry import agent_registry, AgentRegistry
from src.core.metrics_collector import metrics_collector

# Import new Phase 2 components
from src.database.connection import init_database, cleanup_database, db_manager
from src.database.influx_client import influx_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Agent Monitor Framework Phase 2...")
    
    try:
        # Initialize database connections
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize agent registry with database manager
        import src.core.agent_registry as registry_module
        registry_module.agent_registry = AgentRegistry(db_manager)
        logger.info("Agent registry initialized with database persistence")
        
        # Initialize InfluxDB client
        await influx_client.initialize()
        logger.info("InfluxDB client initialized")
        
        # Core services are ready
        logger.info("Core services ready")
        
        logger.info("Agent Monitor Framework Phase 2 started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Monitor Framework...")
    
    try:
        # Core services cleanup handled automatically
        await cleanup_database()
        logger.info("Agent Monitor Framework shut down complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Agent Monitor Framework",
    description="Production-ready agent monitoring and management platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agents_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

# Add root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Monitor Framework</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c3e50; }
            .card { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .status { color: #27ae60; font-weight: bold; }
            .link { color: #3498db; text-decoration: none; }
            .link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1 class="header">🚀 Agent Monitor Framework - Phase 2</h1>
        <div class="card">
            <p class="status">✅ System Status: Online</p>
            <p><strong>Version:</strong> 2.0.0</p>
            <p><strong>Features:</strong> Database Persistence, Real-time Monitoring, Advanced Analytics</p>
        </div>
        
        <div class="card">
            <h3>🔗 Quick Links</h3>
            <ul>
                <li><a href="/docs" class="link">📚 API Documentation</a></li>
                <li><a href="/api/v1/system/status" class="link">📊 System Status</a></li>
                <li><a href="/api/v1/agents" class="link">🤖 List Agents</a></li>
                <li><a href="/api/v1/system/health" class="link">💓 Health Check</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>🎯 Key Features</h3>
            <ul>
                <li>✅ <strong>Agent Registration & Management</strong></li>
                <li>✅ <strong>Real-time Metrics Collection</strong></li>
                <li>✅ <strong>Database Persistence (SQLite/PostgreSQL)</strong></li>
                <li>✅ <strong>Time-series Data Storage (InfluxDB)</strong></li>
                <li>✅ <strong>Health Monitoring & Alerting</strong></li>
                <li>✅ <strong>RESTful API Interface</strong></li>
                <li>✅ <strong>Interactive Documentation</strong></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>📈 Coming Soon</h3>
            <ul>
                <li>🔲 Web Dashboard Interface</li>
                <li>🔲 Advanced Alerting System</li>
                <li>🔲 Multi-Agent Orchestration</li>
                <li>🔲 User Authentication & RBAC</li>
                <li>🔲 Historical Analytics</li>
            </ul>
        </div>
    </body>
    </html>
    """

# Enhanced system information endpoint
@app.get("/api/v2/system/info")
async def system_info():
    """Get detailed system information"""
    return {
        "name": "Agent Monitor Framework",
        "version": "2.0.0",
        "phase": "Phase 2 - Database Persistence",
        "features": {
            "agent_registry": True,
            "metrics_collection": True,
            "database_persistence": True,
            "time_series_storage": True,
            "health_monitoring": True,
            "api_documentation": True,
            "web_dashboard": False,  # Coming in Phase 2.2
            "advanced_alerting": False,  # Coming in Phase 2.3
            "user_authentication": False  # Coming in Phase 2.4
        },
        "database": {
            "type": "SQLite" if settings.database.postgres_url.startswith("sqlite") else "PostgreSQL",
            "url": settings.database.postgres_url.split("://")[0] + "://***",
            "status": "connected"
        },
        "time_series": {
            "type": "InfluxDB",
            "url": settings.database.influxdb_url,
            "status": "available" if influx_client.client else "unavailable"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    print("🚀 Agent Monitor Framework - Phase 2")
    print("=" * 50)
    print("Features: Database Persistence, Enhanced APIs, Production Ready")
    print(f"Environment: {settings.monitoring.environment if hasattr(settings.monitoring, 'environment') else 'development'}")
    print(f"Log Level: {settings.logging.level}")
    print(f"Database: {settings.database.postgres_url.split('://')[0]}")
    print("=" * 50)
    
    uvicorn.run(
        "main_v2:app", 
        host=settings.monitoring.host, 
        port=settings.monitoring.port, 
        reload=True,  # Enable for development
        log_level="info"
    )