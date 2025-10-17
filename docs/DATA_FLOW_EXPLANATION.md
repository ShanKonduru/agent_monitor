## Agent Monitor Framework - Data Flow Diagram

### 📊 **Current System Data Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │    FastAPI      │    │   PostgreSQL    │    │   Web Browser   │
│    Agents       │    │   Application   │    │    Database     │    │   Dashboard     │
│                 │    │  (localhost:    │    │  (localhost:    │    │                 │
│ • Web Server    │    │     8000)       │    │     5432)       │    │                 │
│ • DB Monitor    │    │                 │    │                 │    │                 │
│ • API Gateway   │    │                 │    │                 │    │                 │
│ • Cache Monitor │    │                 │    │                 │    │                 │
│ • Security Scan │    │                 │    │                 │    │                 │
│ • Log Processor │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ STEP 1: │             │ STEP 2: │             │ STEP 3: │             │ STEP 4: │
    │Register │             │ Process │             │  Store  │             │ Display │
    │ Agent   │             │Request  │             │  Data   │             │  Data   │
    └─────────┘             └─────────┘             └─────────┘             └─────────┘
```

### 🔄 **Step-by-Step Data Flow**

#### **STEP 1: Agent Registration** 
```
Agent → POST /api/v1/agents/register → FastAPI
```
**Data Sent:**
```json
{
  "name": "Web Server Alpha",
  "type": "api_agent", 
  "host": "web-01.company.com",
  "port": 8080,
  "environment": "production",
  "metadata": {
    "region": "us-east-1",
    "team": "platform"
  }
}
```

#### **STEP 2: API Processing**
```
FastAPI → Agent Registry → Database Operations
```
**What Happens:**
- Validates agent data
- Generates unique UUID
- Creates database record
- Sets status to "ONLINE"
- Records registration timestamp

#### **STEP 3: Database Storage**
```
Agent Registry → INSERT INTO agents → PostgreSQL
```
**Database Record:**
```sql
INSERT INTO agents (
  id, name, type, host, port, status, 
  environment, agent_metadata, created_at
) VALUES (
  'uuid-12345', 'Web Server Alpha', 'api_agent',
  'web-01.company.com', 8080, 'online',
  'production', '{"region":"us-east-1"}', NOW()
);
```

#### **STEP 4: Dashboard Display**
```
Browser → GET /api/v1/agents → Agent Registry → SELECT FROM agents → PostgreSQL
```
**API Response:**
```json
{
  "agents": [
    {
      "id": "uuid-12345",
      "name": "Web Server Alpha", 
      "status": "online",
      "host": "web-01.company.com",
      "port": 8080,
      "last_heartbeat": "2025-10-16T23:45:00Z"
    }
  ]
}
```

### 📋 **Current Database Tables**

```
┌─────────────────┐
│     agents      │ ← Main agent information
├─────────────────┤
│ • id (UUID)     │
│ • name          │
│ • type          │
│ • host          │
│ • port          │
│ • status        │
│ • environment   │
│ • metadata      │
│ • last_heartbeat│
│ • created_at    │
└─────────────────┘
         │
         ├── agent_configurations (key-value config)
         ├── agent_tags (categorization)
         ├── alert_instances (active alerts)
         └── alert_rules (alert definitions)
```

### 🚀 **What's Working Now**

✅ **Completed Data Flow:**
1. **Agent Registration**: External agents can register via API
2. **Database Storage**: Agent data persisted in PostgreSQL
3. **Dashboard Fetch**: Web dashboard reads real data from database
4. **Status Display**: Shows agent status, metadata, heartbeat times

### 🔄 **What's Missing (Future Implementation)**

❌ **Not Yet Implemented:**
1. **Metrics Push**: Agents don't yet push performance data (CPU, memory, etc.)
2. **Real-time Updates**: Dashboard doesn't auto-refresh
3. **Heartbeat Mechanism**: Agents don't send periodic heartbeats
4. **Alert Generation**: No automatic alerts based on agent status

### 🎯 **How to Test Current System**

1. **View Database Data:**
   ```bash
   python test_agents_db.py  # Shows 6 dummy agents in database
   ```

2. **Test API:**
   ```bash
   curl http://localhost:8000/api/v1/agents/  # Gets agent list
   ```

3. **View Dashboard:**
   ```
   Open: http://localhost:8000/dashboard  # Shows real agent data
   ```

The system currently works as a **Agent Registry** where agents register once and their status is stored in PostgreSQL. The dashboard reads this real data and displays it with mock performance metrics for visualization purposes.