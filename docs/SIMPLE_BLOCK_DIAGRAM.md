# System Block Diagram - Agent Monitor Framework

## 📐 Simple System Overview

```
    EXTERNAL SYSTEMS          MONITORING SERVER           DATABASE            USER INTERFACE
    (Being Monitored)         (localhost:8000)         (PostgreSQL)           (Web Browser)

┌─────────────────────┐    ┌───────────────────────┐    ┌─────────────┐    ┌─────────────────┐
│                     │    │                       │    │             │    │                 │
│  🌐 Web Server      │────┤                       │    │             │    │                 │
│  🗄️  Database       │────┤     FastAPI Server    │────┤ PostgreSQL  │────┤   Dashboard     │
│  🔒 API Gateway     │────┤                       │    │  Database   │    │   (React UI)    │
│  💾 Cache Server    │────┤   • REST API          │    │             │    │                 │
│  🔍 Security Scan   │────┤   • Agent Registry    │    │ Tables:     │    │ Views:          │
│  📊 Log Processor   │    │   • Metrics Store     │    │ • agents    │    │ • Agent List    │
│                     │    │                       │    │ • configs   │    │ • Metrics       │
└─────────────────────┘    └───────────────────────┘    │ • alerts    │    │ • Alerts        │
                                                        │             │    │ • Settings      │
                                                        └─────────────┘    └─────────────────┘
```

## 🔄 Data Flow Process

### Step 1: Agent Registration
```
External System  →  POST /api/v1/agents/register  →  FastAPI  →  PostgreSQL
    (Agent)                                         Server      agents table
```

### Step 2: Dashboard Loading  
```
Web Browser  →  GET /dashboard  →  FastAPI  →  Serve dashboard.html
                                   Server
```

### Step 3: Data Retrieval
```
Dashboard  →  GET /api/v1/agents  →  FastAPI  →  Query PostgreSQL  →  Return JSON
  (AJAX)                            Server        agents table
```

## 🏗️ Component Breakdown

| Component | Purpose | Status |
|-----------|---------|--------|
| **External Agents** | Systems being monitored | ✅ Can register |
| **FastAPI Server** | Central monitoring hub | ✅ Fully working |
| **PostgreSQL DB** | Data persistence | ✅ Schema created |
| **React Dashboard** | Web interface | ✅ Shows real data |

## 📊 Current Database Tables

```
agents
├── id (UUID)
├── name  
├── type (api_agent, monitor_agent, etc.)
├── host
├── port
├── status (online, offline, error, maintenance)
├── environment (production, staging)
├── metadata (JSON)
└── last_heartbeat

agent_configurations
├── agent_id (FK)
├── config_key
└── config_value

alert_rules  
├── rule_id
├── condition
└── threshold
```

## 🎯 What Works Right Now

1. **✅ Agent Registration**: External systems can register as monitored agents
2. **✅ Data Storage**: Agent info stored persistently in PostgreSQL  
3. **✅ Dashboard Display**: Web interface shows real agent data from database
4. **✅ Status Tracking**: Agents have online/offline/error/maintenance states

## 🚧 What's Not Implemented Yet

1. **❌ Metrics Push**: Agents don't send CPU/memory/performance data
2. **❌ Real-time Updates**: Dashboard doesn't auto-refresh
3. **❌ Heartbeat System**: No periodic "I'm alive" signals from agents
4. **❌ Alert Generation**: No automatic alerts when agents have issues

## 🧪 How to Test Current System

### Test Database:
```bash
python test_agents_db.py
# Shows: 6 dummy agents in PostgreSQL
```

### Test API:
```bash
curl http://localhost:8000/api/v1/agents/
# Returns: JSON list of registered agents
```

### Test Dashboard:
```
Open: http://localhost:8000/dashboard
# Shows: Live dashboard with real agent data
```

This is a **working agent registry system** that can be extended to full monitoring capabilities!