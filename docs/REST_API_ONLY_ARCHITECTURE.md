# REST API Only Architecture - Agent Monitor Framework

## 🚨 **CRITICAL: ALL Database Access via REST APIs ONLY**

### ❌ **What is NOT Allowed**
```
❌ Direct Database Connections:
   Agent ──X──► PostgreSQL Database  (FORBIDDEN)
   Dashboard ──X──► PostgreSQL Database  (FORBIDDEN) 
   External Tools ──X──► PostgreSQL Database  (FORBIDDEN)
```

### ✅ **What IS Allowed**  
```
✅ REST API Only:
   Agent ──HTTP──► FastAPI Server ──SQL──► PostgreSQL Database
   Dashboard ──HTTP──► FastAPI Server ──SQL──► PostgreSQL Database
   External Tools ──HTTP──► FastAPI Server ──SQL──► PostgreSQL Database
```

## 🏗️ **Architecture Layers**

### **Layer 1: External Systems** (Agents, Dashboard, Tools)
- **Access Method**: HTTP/HTTPS REST API calls only
- **Data Format**: JSON requests and responses
- **Authentication**: API keys, tokens (future)
- **No Database Knowledge**: Don't know database exists

### **Layer 2: Agent Monitor Framework** (FastAPI Server)
- **Role**: Single gateway to all data
- **Responsibilities**:
  - API endpoint handling
  - Data validation and sanitization
  - Business logic enforcement
  - Authentication and authorization
  - Rate limiting and security
- **Database Access**: ONLY this layer talks to PostgreSQL

### **Layer 3: PostgreSQL Database** (Private Data Store)
- **Access**: Internal to Agent Monitor Framework only
- **Network**: Private/localhost connections only
- **Credentials**: Known only to Framework application
- **No External Access**: Firewall blocked from external systems

## 📊 **Data Flow Examples**

### **Agent Registration Flow**
```
1. Agent ──POST /api/v1/agents/register──► FastAPI Server
2. FastAPI Server validates JSON data
3. FastAPI Server ──INSERT INTO agents──► PostgreSQL  
4. PostgreSQL returns success
5. FastAPI Server ──HTTP 200 + agent_id──► Agent
```

### **Dashboard Data Retrieval Flow**
```
1. Dashboard ──GET /api/v1/agents──► FastAPI Server
2. FastAPI Server ──SELECT * FROM agents──► PostgreSQL
3. PostgreSQL returns agent records  
4. FastAPI Server converts to JSON
5. FastAPI Server ──HTTP 200 + JSON──► Dashboard
```

### **Agent Metrics Submission Flow (Future)**
```
1. Agent ──POST /api/v1/agents/{id}/metrics──► FastAPI Server
2. FastAPI Server validates metrics data
3. FastAPI Server ──INSERT INTO agent_metrics──► PostgreSQL
4. PostgreSQL stores metrics
5. FastAPI Server ──HTTP 200──► Agent
```

## 🔒 **Security Benefits**

### **Database Security**
- ✅ Database credentials never shared with external systems
- ✅ Database can be firewalled from internet access
- ✅ SQL injection attacks prevented by ORM
- ✅ Database schema changes don't break external systems

### **API Security**  
- ✅ Centralized authentication and authorization
- ✅ Rate limiting to prevent abuse
- ✅ Input validation and sanitization
- ✅ Audit logging of all data access
- ✅ API versioning for backward compatibility

### **Network Security**
- ✅ Only HTTP/HTTPS ports (80/443) need to be open
- ✅ Database port (5432) can be private/localhost only
- ✅ TLS encryption for all external communication
- ✅ No need to manage database firewall rules for agents

## 🎯 **Current Implementation**

### **Available REST API Endpoints**
```
✅ POST /api/v1/agents/register     - Agent registration
✅ GET  /api/v1/agents              - List all agents  
✅ GET  /api/v1/agents/{id}         - Get specific agent
✅ GET  /dashboard                  - Web dashboard
✅ GET  /health                     - Health check

🚧 Future Endpoints:
   POST /api/v1/agents/{id}/heartbeat  - Status updates
   POST /api/v1/agents/{id}/metrics    - Performance data
   GET  /api/v1/metrics                - Metrics queries
   POST /api/v1/alerts                 - Alert management
```

### **Database Tables (Private - API Access Only)**
```
✅ agents              - Agent registration data
✅ agent_configurations - Agent config key-value pairs  
✅ agent_tags          - Agent categorization
✅ alert_rules         - Alert condition definitions
✅ alert_instances     - Active/resolved alerts

🚧 Future Tables:
   agent_metrics       - Performance time-series data
   user_sessions       - Dashboard user management
   audit_logs          - API access logging
```

## 📱 **Client Examples**

### **Agent Registration (Python)**
```python
import requests

# Agent registers via REST API
response = requests.post('http://monitoring.company.com:8000/api/v1/agents/register', 
    json={
        "name": "Web Server 01",
        "type": "api_agent", 
        "host": "web-01.company.com",
        "port": 8080,
        "environment": "production"
    }
)
agent_id = response.json()["agent_id"]
```

### **Dashboard Data Fetch (JavaScript)**
```javascript
// Dashboard fetches data via REST API
const response = await fetch('http://monitoring.company.com:8000/api/v1/agents');
const agents = await response.json();
console.log(agents);
```

### **Command Line Tool (curl)**
```bash
# CLI tool queries via REST API
curl -X GET http://monitoring.company.com:8000/api/v1/agents \
     -H "Accept: application/json"
```

## 🎉 **Summary**

The Agent Monitor Framework uses a **REST API-only architecture** where:

1. **All external systems** (agents, dashboard, tools) access data ONLY via HTTP REST APIs
2. **Agent Monitor Framework** is the single gateway that handles all database operations
3. **PostgreSQL database** is completely private and isolated from external access
4. **Security, validation, and business logic** are centralized in the API layer
5. **Scalability and maintainability** are improved through clear separation of concerns

This architecture ensures security, scalability, and maintainability while providing a clean interface for all external systems to interact with the monitoring data.