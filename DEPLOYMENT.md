# PulseGuard Agent Monitor - Seamless Deployment

## 🚀 Quick Start (30 seconds)

**Option 1: Ultra-Simple (Recommended)**
```bash
# Just run this one file:
deploy_simple.bat
```

**Option 2: Full Control**
```bash
# Test first, then deploy:
test_deployment.bat
deploy_complete.bat
```

## 📋 What You Get

✅ **Complete Agent Monitor Dashboard** with AI/LLM metrics  
✅ **5 Mock Agents** (GPT-4, Claude-3, Llama-2, API Gateway, Data Agent)  
✅ **Real AI Metrics** (tokens/sec, model accuracy, inference times)  
✅ **REST APIs** for programmatic access  
✅ **Health monitoring** and status checks  

## 🎯 Access Points

Once deployed, access your dashboard at:

- **📊 Main Dashboard**: http://localhost:8000/dashboard
- **📡 API Endpoint**: http://localhost:8000/api/v1/agents/
- **🤖 AI Metrics**: http://localhost:8000/api/v1/system/ai-metrics
- **🏥 Health Check**: http://localhost:8000/api/v1/health

## 💡 Deployment Options

### Python Deploy (Fastest)
- ✅ No Docker required
- ✅ Instant startup
- ✅ Auto-installs dependencies
- ✅ Perfect for development

### Docker Deploy (Production)
- ✅ Containerized and isolated
- ✅ Production-ready
- ✅ Easy scaling
- ✅ Health checks included

## 🛠️ Files Overview

| File | Purpose |
|------|---------|
| `deploy_simple.bat` | One-click Python deployment |
| `deploy_complete.bat` | Full deployment menu with options |
| `test_deployment.bat` | Pre-deployment validation |
| `working_dashboard_server.py` | Main server application |
| `Dockerfile.simple` | Docker container definition |
| `docker-compose.simple.yml` | Docker orchestration |

## 🔧 Troubleshooting

**Issue**: Port 8000 already in use  
**Solution**: Run `deploy_complete.bat` → Option 4 (Stop All Services)

**Issue**: Python not found  
**Solution**: Install Python 3.11+ from python.org

**Issue**: Docker build fails  
**Solution**: Use Python deploy instead (Option 1)

## 🎉 Success Indicators

✅ Server starts with these messages:
```
🚀 Starting Working Dashboard Server...
📊 Dashboard: http://localhost:8000/dashboard
📡 API: http://localhost:8000/api/v1/agents/
INFO: Uvicorn running on http://0.0.0.0:8000
```

✅ Dashboard shows 5 agents with live metrics  
✅ API returns JSON data for agents  
✅ Health check returns "healthy" status  

## 🚦 Validation

Before deployment, run:
```bash
test_deployment.bat
```

This checks all requirements and tells you exactly what will work.

---

**That's it!** No more trial and error. No more back-and-forth. Just run one script and get your complete AI agent monitoring dashboard running.