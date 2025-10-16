
"""
Agent Monitor Framework - Main FastAPI Application
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.config import settings
from src.api.agents import router as agents_router
from src.api.metrics import router as metrics_router
from src.api.health import router as health_router
from src.core.agent_registry import agent_registry
from src.core.metrics_collector import metrics_collector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.logging.level.upper()),
    format=settings.logging.format,
    filename=settings.logging.file_path
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Agent Monitor Framework...")
    
    # Initialize components
    # TODO: Initialize database connections
    # TODO: Initialize Redis connection
    # TODO: Initialize InfluxDB connection
    
    logger.info("Agent Monitor Framework started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Monitor Framework...")
    
    # Cleanup resources
    # TODO: Close database connections
    # TODO: Cancel background tasks
    
    logger.info("Agent Monitor Framework shut down complete")


# Create FastAPI application
app = FastAPI(
    title="Agent Monitor Framework",
    description="A comprehensive monitoring framework for AI/ML agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(metrics_router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic info"""
    return """
    <html>
        <head>
            <title>Agent Monitor Framework</title>
        </head>
        <body>
            <h1>Agent Monitor Framework</h1>
            <p>A comprehensive monitoring framework for AI/ML agents</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/redoc">ReDoc Documentation</a></li>
                <li><a href="/api/v1/agents">Agents API</a></li>
                <li><a href="/api/v1/metrics">Metrics API</a></li>
                <li><a href="/api/v1/health">Health API</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/api/v1/system/status")
async def system_status():
    """Get system status"""
    try:
        agents = await agent_registry.get_all_agents()
        active_agents = await agent_registry.get_active_agents()
        system_metrics = await metrics_collector.get_system_metrics_summary()
        
        return {
            "status": "healthy",
            "timestamp": "2025-10-15T00:00:00Z",  # Will be replaced with actual timestamp
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "system_metrics": system_metrics,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


def main():
    """Main entry point"""
    logger.info("Starting Agent Monitor Framework...")
    
    uvicorn.run(
        "main:app",
        host=settings.monitoring.host,
        port=settings.monitoring.port,
        reload=settings.monitoring.debug,
        log_level=settings.logging.level.lower()
    )


if __name__ == "__main__":
    main()
