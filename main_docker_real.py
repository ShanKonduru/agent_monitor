"""
Real Agent Monitor Framework for Docker - Main FastAPI Application with SQLite
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

# Add current directory to Python path for Docker
sys.path.insert(0, '/app')
sys.path.insert(0, '.')

# Set environment variables for Docker compatibility  
os.environ.setdefault('REDIS_URL', '')  # Disable Redis
os.environ.setdefault('INFLUXDB_URL', '')  # Disable InfluxDB
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('LOG_FILE', '')  # Log to console

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from src.config import settings
    from src.api.agents import router as agents_router, set_agent_registry
    from src.api.metrics import router as metrics_router
    from src.api.health import router as health_router, set_agent_registry as set_health_agent_registry
    from src.core.agent_registry import AgentRegistry
    from src.core.metrics_collector import metrics_collector
    from src.database.connection import DatabaseManager
    HAS_FULL_COMPONENTS = True
except ImportError as e:
    logger.error(f"Could not import some components: {e}")
    HAS_FULL_COMPONENTS = False

# Global instances
db_manager = None
agent_registry = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager, agent_registry
    
    # Startup
    logger.info("Starting Agent Monitor Framework in Docker...")
    
    if HAS_FULL_COMPONENTS:
        # Initialize components
        try:
            db_manager = DatabaseManager()
            await db_manager.initialize()
            logger.info("Database manager initialized successfully")
            
            # Create database tables
            await db_manager.create_tables()
            logger.info("Database tables created successfully")
            
            # Initialize agent registry
            agent_registry = AgentRegistry(db_manager)
            set_agent_registry(agent_registry)
            set_health_agent_registry(agent_registry)
            
            # Metrics collector is ready (no initialization needed)
            logger.info("Metrics collector ready")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            # Continue with basic functionality
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Monitor Framework...")
    if db_manager:
        await db_manager.close()


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

# Mount static files
if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

# Include API routers if available
if HAS_FULL_COMPONENTS:
    try:
        app.include_router(agents_router, prefix="/api/v1/agents")
        app.include_router(metrics_router, prefix="/api/v1")
        app.include_router(health_router, prefix="/api/v1")
        logger.info("API routers included successfully")
    except Exception as e:
        logger.warning(f"Could not include some routers: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Agent Monitor Framework",
        "version": "1.0.0",
        "status": "running",
        "docker": True,
        "mode": "real"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "docker": True,
        "mode": "real",
        "components": {
            "database": db_manager is not None,
            "agent_registry": agent_registry is not None,
            "metrics_collector": True
        }
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    # Try to serve the real dashboard from web directory (prioritize the large React dashboard)
    dashboard_paths = [
        "web/dashboard.html",  # The real 159KB React dashboard we worked on
        "web/dashboard-offline.html",
        "web/simple-dashboard.html"
    ]
    
    for path in dashboard_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Serving dashboard from {path}")
                return content
            except Exception as e:
                logger.warning(f"Could not serve {path}: {e}")
                continue
    
    # Fallback to a basic dashboard
    logger.warning("No dashboard files found, serving basic fallback")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Monitor - Docker Real</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Agent Monitor Framework - Docker Real Edition</h1>
        <p>Dashboard files not found. Available endpoints:</p>
        <ul>
            <li><a href="/docs">API Documentation</a></li>
            <li><a href="/api/v1/agents/">Agents API</a></li>
            <li><a href="/api/v1/system/status">System Status</a></li>
        </ul>
    </body>
    </html>
    """


if __name__ == "__main__":
    logger.info("Starting Agent Monitor Framework (Real Docker Version)...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )