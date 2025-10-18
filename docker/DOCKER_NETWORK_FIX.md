# Docker Desktop Network Configuration Guide

## Issue: TLS Handshake Timeout with Docker Registry

You're experiencing network connectivity issues with Docker Hub. Here's how to fix it:

### Immediate Solutions

#### 1. **Docker Desktop Settings**
1. Open **Docker Desktop**
2. Click the **Settings** gear icon
3. Go to **Resources** → **Network**
4. Try these DNS settings:
   ```
   8.8.8.8
   8.8.4.4
   ```
   OR
   ```
   1.1.1.1
   1.0.0.1
   ```

#### 2. **Proxy Configuration**
Your Docker shows proxy settings: `http.docker.internal:3128`

1. In Docker Desktop → **Settings** → **Resources** → **Proxies**
2. Try **DISABLING** proxy temporarily:
   - Uncheck "Use proxy server"
   - Apply & Restart Docker
3. If you need proxy, ensure these URLs are in bypass list:
   ```
   registry-1.docker.io
   docker.io
   *.docker.io
   ```

#### 3. **Windows Network Reset**
```cmd
# Run as Administrator
ipconfig /flushdns
netsh winsock reset
netsh int ip reset
# Restart computer
```

### Alternative: Use Pre-built Images

#### Option A: Import from Another Machine
If you have access to another machine with Docker:
```bash
# On working machine
docker pull python:3.11-slim
docker save python:3.11-slim > python-image.tar

# Transfer file to your machine
docker load < python-image.tar
```

#### Option B: Use Docker Desktop's Extension Feature
1. Open Docker Desktop
2. Go to **Extensions**
3. Look for Python development extensions

### Test Connectivity
```bash
# Test basic connectivity
ping registry-1.docker.io
curl -I https://registry-1.docker.io

# Test Docker without proxy
docker --config /tmp pull hello-world
```

### Immediate Workaround: Run Locally

While fixing Docker, you can still demonstrate the container concept locally:

1. **Run the demo locally first**:
   ```bash
   .\demo_container_agents.bat
   ```

2. **Once Docker is fixed**, use these commands:
   ```bash
   # Build agent image
   docker build -f Dockerfile.alpine -t agent-monitor-agent .
   
   # Run multiple containers
   docker run -d --name llm-agent-1 -e AGENT_NAME="LLM Agent 1" agent-monitor-agent
   docker run -d --name api-agent-1 -e AGENT_NAME="API Agent 1" agent-monitor-agent
   ```

### Corporate Network Specific

If you're on a corporate network:

1. **Contact IT** about Docker registry access
2. **Use internal registry** if available
3. **VPN configuration** might be blocking Docker Hub

### Manual Docker Desktop Reset

If all else fails:
1. **Docker Desktop** → **Settings** → **Reset**
2. Choose **"Reset to factory defaults"**
3. Restart and try again

Would you like me to create a local container simulation while we fix the Docker connectivity issue?