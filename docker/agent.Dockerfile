# Agent Dockerfile - For running monitored agents in containers
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source code
COPY src/ ./src/
COPY web/ ./web/
COPY *.py ./

# Create non-root user and data directory
RUN useradd --create-home --shell /bin/bash agent && \
    mkdir -p /app/data && \
    chown -R agent:agent /app
USER agent

# Environment variables for agent configuration
ENV PYTHONPATH=/app
ENV MONITOR_URL=http://monitor:8000
ENV AGENT_ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; import sys; from src.agents.client import AgentMonitorClient; sys.exit(0)" || exit 1

# Default command - can be overridden
CMD ["python", "example_agent.py"]