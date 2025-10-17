# Agent Monitor Framework - System Block Diagram

## 🏗️ **System Architecture Block Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            AGENT MONITOR FRAMEWORK                                  │
│                              (localhost:8000)                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────────────────────────────────────────────────┐    ┌─────────────────┐
│                 │    │                                                             │    │                 │
│   EXTERNAL      │    │                    FASTAPI SERVER                          │    │   WEB BROWSER   │
│    AGENTS       │    │                                                             │    │    DASHBOARD    │
│                 │    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │    │                 │
│  ┌───────────┐  │    │  │                 │  │                 │  │             │ │    │  ┌───────────┐  │
│  │Web Server │  │◄──►│  │   API ROUTES    │  │  CORE SERVICES  │  │ DATABASE    │ │◄──►│  │ React UI  │  │
│  │   Agent   │  │    │  │                 │  │                 │  │ CONNECTION  │ │    │  │Dashboard  │  │
│  └───────────┘  │    │  │ /api/v1/agents  │  │ Agent Registry  │  │             │ │    │  └───────────┘  │
│                 │    │  │ /dashboard      │  │ Metrics         │  │ PostgreSQL  │ │    │                 │
│  ┌───────────┐  │    │  │ /health         │  │ Collector       │  │ AsyncPG     │ │    │  ┌───────────┐  │
│  │Database   │  │    │  │                 │  │                 │  │ Driver      │ │    │  │   HTTP    │  │
│  │ Monitor   │  │    │  └─────────────────┘  └─────────────────┘  └─────────────┘ │    │  │ Requests  │  │
│  └───────────┘  │    │           │                    │                    │      │    │  └───────────┘  │
│                 │    │           ▼                    ▼                    ▼      │    │                 │
│  ┌───────────┐  │    └─────────────────────────────────────────────────────────────┘    └─────────────────┘
│  │API Gateway│  │                          │                    │                    │  
│  │   Agent   │  │                          │                    │                    │  
│  └───────────┘  │                          ▼                    ▼                    ▼  
│                 │              ┌─────────────────────────────────────────────────────────┐
│  ┌───────────┐  │              │                                                         │
│  │Cache      │  │              │                  POSTGRESQL DATABASE                   │
│  │ Monitor   │  │              │                    (localhost:5432)                    │
│  └───────────┘  │              │                                                         │
│                 │              │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  ┌───────────┐  │              │  │   agents    │  │agent_configs│  │ alert_rules │   │
│  │Security   │  │              │  │   TABLE     │  │   TABLE     │  │   TABLE     │   │
│  │ Scanner   │  │              │  │             │  │             │  │             │   │
│  └───────────┘  │              │  │ • id        │  │ • agent_id  │  │ • rule_id   │   │
│                 │              │  │ • name      │  │ • key       │  │ • condition │   │
│  ┌───────────┐  │              │  │ • type      │  │ • value     │  │ • threshold │   │
│  │Log        │  │              │  │ • host      │  │             │  │             │   │
│  │Processor  │  │              │  │ • port      │  └─────────────┘  └─────────────┘   │
│  └───────────┘  │              │  │ • status    │                                     │
│                 │              │  │ • metadata  │  ┌─────────────┐  ┌─────────────┐   │
└─────────────────┘              │  │ • heartbeat │  │agent_metrics│  │alert_instances│ │
                                │  └─────────────┘  │   TABLE     │  │   TABLE     │   │
                                │                   │ (FUTURE)    │  │             │   │
                                │                   │             │  │ • alert_id  │   │
                                │                   │ • cpu_usage │  │ • agent_id  │   │
                                │                   │ • memory    │  │ • severity  │   │
                                │                   │ • timestamp │  │ • status    │   │
                                │                   └─────────────┘  └─────────────┘   │
                                └─────────────────────────────────────────────────────────┘
```

## 📊 **Data Flow Arrows**

### **1. Agent Registration Flow**
```
External Agents ──POST /register──► FastAPI ──Agent Registry──► PostgreSQL
                                                               └─► agents table
```

### **2. Dashboard Data Flow**
```
Web Browser ──GET /dashboard──► FastAPI ──serve HTML──► React Dashboard
     ▲                                                         │
     │                                                         │
     └──JSON response──◄ FastAPI ◄──Agent Registry──◄ PostgreSQL
                                                    └─► SELECT * FROM agents
```

### **3. Future Metrics Flow** *(Not Yet Implemented)*
```
External Agents ──POST /metrics──► FastAPI ──Metrics Collector──► PostgreSQL
                                                                 └─► agent_metrics table
```

## 🔧 **Component Details**

### **EXTERNAL AGENTS** (Left Side)
- **Purpose**: Services/systems being monitored
- **Examples**: Web servers, databases, APIs, caches
- **Communication**: HTTP REST API calls to monitoring server
- **Current State**: Can register, no metrics push yet

### **FASTAPI SERVER** (Center)
- **API Routes**: Handle incoming requests from agents and dashboard
- **Core Services**: Business logic for agent management and metrics
- **Database Connection**: Async PostgreSQL connection with SQLAlchemy ORM
- **Current State**: Fully functional with agent registry

### **POSTGRESQL DATABASE** (Bottom)
- **agents table**: Main agent information (name, status, host, etc.)
- **agent_configs table**: Configuration key-value pairs per agent
- **alert_rules table**: Alert condition definitions
- **agent_metrics table**: Time-series performance data (FUTURE)
- **alert_instances table**: Active/resolved alerts
- **Current State**: Schema created, agents table populated

### **WEB BROWSER DASHBOARD** (Right Side)
- **React UI**: Modern dashboard with multiple views
- **HTTP Requests**: Fetches data via REST API calls
- **Real-time Display**: Shows agent status, metadata, mock metrics
- **Current State**: Functional with real database integration

## 🚦 **Current Status**

### ✅ **WORKING NOW**
1. **Agent Registration**: Agents can register via API → stored in PostgreSQL
2. **Dashboard Display**: Browser loads dashboard → fetches real agent data
3. **Database Persistence**: Agent data survives server restarts
4. **Status Tracking**: Shows online/offline/error/maintenance states

### ❌ **NOT YET IMPLEMENTED**
1. **Metrics Collection**: Agents don't push CPU/memory/performance data
2. **Real-time Updates**: Dashboard doesn't auto-refresh
3. **Heartbeat System**: No periodic status updates from agents
4. **Alert Generation**: No automatic alerts when agents go offline

## 🎯 **Key Data Structures**

### **Agent Registration Data**
```json
{
  "id": "uuid-12345",
  "name": "Web Server Alpha",
  "type": "api_agent",
  "host": "web-01.company.com", 
  "port": 8080,
  "status": "online",
  "environment": "production",
  "metadata": {
    "region": "us-east-1",
    "team": "platform"
  }
}
```

### **Dashboard API Response**
```json
{
  "agents": [
    {
      "id": "uuid-12345",
      "name": "Web Server Alpha",
      "status": "online",
      "last_heartbeat": "2025-10-16T23:45:00Z",
      "host": "web-01.company.com",
      "port": 8080
    }
  ]
}
```

This block diagram shows exactly how data flows from external agents through the FastAPI server to PostgreSQL database and back to the dashboard. The system is currently a working **Agent Registry** that can be extended to full **Metrics Monitoring**.