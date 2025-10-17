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

## 🌐 **Distributed System Architecture - 4 Main Systems**

### **System 1: Dashboard UX System** 
```
┌─────────────────────────────────────────────────────────────┐
│                   DASHBOARD UX SYSTEM                      │
│                  (User Access Layer)                       │
├─────────────────────────────────────────────────────────────┤
│  🖥️  Web Browser (Any Machine)                             │
│     • URL: http://monitoring-server:8000/dashboard         │
│     • React-based Single Page Application                  │
│     • Real-time data visualization                         │
│     • Agent management interface                           │
│                                                             │
│  📱 Mobile/Tablet Support                                  │
│     • Responsive design for mobile access                  │
│     • Same dashboard accessible from anywhere              │
│                                                             │
│  🔐 Multi-user Access (Future)                            │
│     • Role-based access control                           │
│     • User authentication and sessions                     │
└─────────────────────────────────────────────────────────────┘
```

### **System 2: PostgreSQL Database System**
```
┌─────────────────────────────────────────────────────────────┐
│                 POSTGRESQL DATABASE SYSTEM                 │
│                  (Data Persistence Layer)                  │
├─────────────────────────────────────────────────────────────┤
│  🗄️  Primary Database Server                              │
│     • Host: localhost:5432 (or dedicated DB server)       │
│     • Database: postgres                                   │
│     • User: postgres with password authentication         │
│                                                             │
│  📊 Data Storage:                                          │
│     • Agent registry and metadata                         │
│     • Configuration and settings                          │
│     • Alert rules and instances                           │
│     • Performance metrics (future)                        │
│     • Audit logs and user data                            │
│                                                             │
│  🔄 Database Features:                                     │
│     • ACID compliance for data integrity                  │
│     • Async connections via asyncpg                       │
│     • JSON support for flexible metadata                  │
│     • Indexing for fast queries                           │
└─────────────────────────────────────────────────────────────┘
```

### **System 3: Agent Monitor Framework (Central Hub)**
```
┌─────────────────────────────────────────────────────────────┐
│              AGENT MONITOR FRAMEWORK                        │
│                 (Central Hub System)                        │
├─────────────────────────────────────────────────────────────┤
│  🚀 FastAPI Application Server                            │
│     • Host: monitoring-server:8000                        │
│     • REST API endpoints for all operations               │
│     • Async request handling                              │
│     • CORS enabled for web dashboard access               │
│                                                             │
│  🔧 Core Services:                                         │
│     • Agent Registry (registration/discovery)             │
│     • Metrics Collector (performance data)                │
│     • Alert Manager (threshold monitoring)                │
│     • Configuration Manager (settings)                    │
│                                                             │
│  📡 Communication Protocols:                              │
│     • HTTP/HTTPS REST API                                 │
│     • JSON data exchange format                           │
│     • WebSocket support (future real-time)               │
└─────────────────────────────────────────────────────────────┘
```

### **System 4: Multiple Distributed Agents**
```
┌─────────────────────────────────────────────────────────────┐
│                DISTRIBUTED AGENTS SYSTEM                   │
│               (Monitoring Endpoints)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🖥️  Production Server 1 (web-01.company.com)            │
│     • Web Server Agent                                     │
│     • Monitors: HTTP responses, SSL certs, performance    │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
│  🗄️  Database Server (db-monitor-01.company.com)         │
│     • Database Monitor Agent                              │
│     • Monitors: Query performance, connections, storage   │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
│  🔒 API Gateway (api-01.company.com)                      │
│     • API Gateway Agent                                    │
│     • Monitors: Request routing, auth, rate limiting      │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
│  💾 Cache Server (cache-01.company.com)                   │
│     • Cache Monitor Agent                                  │
│     • Monitors: Memory usage, hit rates, evictions       │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
│  🔍 Security Server (security-01.company.com)             │
│     • Security Scanner Agent                              │
│     • Monitors: Vulnerabilities, compliance, threats     │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
│  📊 Log Server (logs-01.company.com)                      │
│     • Log Processor Agent                                  │
│     • Monitors: Log parsing, pattern detection, alerts   │
│     • Reports to: monitoring-server:8000                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 **Inter-System Communication & Data Flow**

## 🚨 **CRITICAL ARCHITECTURE PRINCIPLE: REST API ONLY**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ALL EXTERNAL  │    │   AGENT MONITOR │    │   POSTGRESQL    │
│     SYSTEMS     │────┤    FRAMEWORK    │────┤    DATABASE     │
│                 │    │   (REST APIs)   │    │   (PRIVATE)     │
│ • Agents        │    │                 │    │                 │
│ • Dashboard     │    │ ONLY ENTRY      │    │ NO DIRECT       │
│ • Mobile Apps   │    │ POINT FOR       │    │ EXTERNAL        │
│ • CLI Tools     │    │ DATA ACCESS     │    │ ACCESS          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   HTTP/HTTPS              FastAPI Server          Internal SQL
   REST APIs               • Authentication        • asyncpg driver
   JSON Data               • Validation            • Connection pool
                          • Business Logic         • Private network
```

**🔒 Security & Access Control:**
- ✅ **Agents**: Access database ONLY via REST APIs (`/api/v1/agents/*`)
- ✅ **Dashboard**: Access database ONLY via REST APIs (`/api/v1/*`)
- ✅ **Database**: PRIVATE - accessible only to Agent Monitor Framework
- ✅ **All data validation, authentication, and business logic in API layer**
- ❌ **NO direct database connections from external systems**
- ❌ **NO database credentials shared with agents or dashboards**

### **1. Agent-to-Hub Communication**
```
Distributed Agents ──HTTP POST──► Agent Monitor Framework
                                          │
Multiple Machines                         ▼
• web-01.company.com              PostgreSQL Database
• db-monitor-01.company.com       • Store agent data
• api-01.company.com              • Persist metrics
• cache-01.company.com            • Log activities
• security-01.company.com
• logs-01.company.com
```

**Communication Details:**
- **Protocol**: HTTP/HTTPS REST API
- **Format**: JSON payloads
- **Frequency**: 
  - Registration: Once on startup
  - Heartbeat: Every 60 seconds
  - Metrics: Every 30 seconds (future)
- **Network**: Cross-internet, VPN, or internal network
- **Security**: API keys, TLS encryption (future)

### **2. Hub-to-Database Communication** *(INTERNAL ONLY)*
```
Agent Monitor Framework ──SQL/AsyncPG──► PostgreSQL Database
    (INTERNAL CONNECTION)                         │
                                                  ▼
Local/Remote Server                       • localhost:5432
• localhost:8000                          • db.company.com:5432
• monitoring.company.com:8000             (PRIVATE - NO EXTERNAL ACCESS)
```

**Communication Details:**
- **Protocol**: PostgreSQL wire protocol via asyncpg *(INTERNAL ONLY)*
- **Connection**: Async connection pooling *(FRAMEWORK ONLY)*
- **Operations**: INSERT, UPDATE, SELECT, DELETE *(FRAMEWORK ONLY)*
- **Transactions**: ACID compliant database operations
- **Security**: Password authentication, SSL connections
- **⚠️ IMPORTANT**: Database is NOT directly accessible to external systems!

### **3. Dashboard-to-Hub Communication**
```
Dashboard UX ──HTTP GET/POST──► Agent Monitor Framework
                                       │
Any Web Browser                        ▼
• Employee laptop              Read from PostgreSQL
• Mobile device                • Agent status
• Tablet                       • Metrics data
• Desktop workstation          • Alert information
```

**Communication Details:**
- **Protocol**: HTTP/HTTPS + AJAX/Fetch API
- **Format**: JSON responses, HTML pages
- **Access**: Web browser from any network location
- **Real-time**: Polling (current), WebSocket (future)
- **Security**: Session management, CORS policies

### **4. Complete Data Flow Cycle**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Agent     │    │   Central   │    │ PostgreSQL  │    │  Dashboard  │
│ (Remote)    │    │    Hub      │    │ Database    │    │    (Web)    │
│             │    │             │    │             │    │             │
│ Step 1: ────┼────► Step 2: ────┼────► Step 3: ────┼────► Step 4:     │
│ Send Data   │    │ Process &   │    │ Store Data  │    │ Display     │
│             │    │ Validate    │    │             │    │ Results     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ▲                                                           │
      │                                                           │
      └─────────────── Step 5: User Actions ─────────────────────┘
                     (Start/Stop/Configure Agents)
```

## 🌍 **Network Deployment Scenarios**

### **Scenario 1: Single Machine Development**
```
┌─────────────────────────────────────────┐
│          LOCALHOST DEVELOPMENT          │
├─────────────────────────────────────────┤
│ • Agent Monitor: localhost:8000         │
│ • PostgreSQL: localhost:5432           │
│ • Dashboard: localhost:8000/dashboard   │
│ • Test Agents: Simulated locally       │
└─────────────────────────────────────────┘
```

### **Scenario 2: Corporate Network Deployment**
```
┌─────────────────────────────────────────┐
│         CORPORATE NETWORK               │
├─────────────────────────────────────────┤
│ Hub Server: monitoring.corp.com:8000   │
│ Database: postgres.corp.com:5432       │
│ Agents: Various internal servers       │
│ Access: Employee workstations          │
└─────────────────────────────────────────┘
```

### **Scenario 3: Cloud/Multi-Region Deployment**
```
┌─────────────────────────────────────────┐
│          CLOUD DEPLOYMENT               │
├─────────────────────────────────────────┤
│ Hub: monitoring.cloud.com:8000         │
│ DB: RDS/CloudSQL managed database      │
│ Agents: EC2/GCE/Azure VMs globally    │
│ CDN: Global dashboard access           │
└─────────────────────────────────────────┘
```

## 📡 **Agent Deployment & Connection Process**

### **Agent Installation on Remote Machine:**
```bash
# 1. Install monitoring agent on target server
curl -O https://monitoring.company.com/install/agent-installer.sh
chmod +x agent-installer.sh
./agent-installer.sh --server=monitoring.company.com:8000

# 2. Agent configuration file created
cat /etc/agent-monitor/config.json
{
  "server_url": "https://monitoring.company.com:8000",
  "agent_type": "web_server",
  "reporting_interval": 30
}

# 3. Agent starts and registers automatically
systemctl start agent-monitor
systemctl enable agent-monitor
```

### **Agent Communication Flow: REST API ONLY**
```
Remote Agent Machine ──HTTP REST API──► Monitoring Server ──Internal SQL──► PostgreSQL

1. Agent Startup:
   POST /api/v1/agents/register      ┌─────────────────┐
   {agent_info...} ──────────────────┤ Agent Monitor   │──SQL──► PostgreSQL
                                     │ Framework       │         (Store agent)
                                     │ (Validates &    │
                                     │  Processes)     │
                                     └─────────────────┘

2. Periodic Heartbeat:
   POST /api/v1/agents/{id}/heartbeat ┌─────────────────┐
   {status: "alive"} ─────────────────┤ Agent Monitor   │──SQL──► PostgreSQL  
                                      │ Framework       │         (Update heartbeat)
                                      └─────────────────┘

3. Metrics Reporting (Future):
   POST /api/v1/agents/{id}/metrics   ┌─────────────────┐
   {cpu, memory, etc.} ───────────────┤ Agent Monitor   │──SQL──► PostgreSQL
                                      │ Framework       │         (Store metrics)
                                      └─────────────────┘
```

**🔑 Key Points:**
- ✅ Agents NEVER connect directly to PostgreSQL database
- ✅ All data goes through REST API validation and processing  
- ✅ Agent Monitor Framework handles ALL database operations
- ✅ Database credentials and connection details stay private
- ✅ API layer provides authentication, rate limiting, data validation

This distributed architecture allows monitoring agents deployed across multiple machines, data centers, cloud regions, or networks to report back to a central monitoring hub, with all data persisted in PostgreSQL and visualized through a web dashboard accessible from anywhere.