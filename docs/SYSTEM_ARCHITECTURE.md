# Agent Monitor Framework - Architecture Overview

## Related Documentation

- **[Database Architecture](./DATABASE_ARCHITECTURE.md)** - Detailed explanation of Redis, InfluxDB, and PostgreSQL usage
- **[Data Flow Explanation](./DATA_FLOW_EXPLANATION.md)** - Complete data flow diagrams
- **[System Block Diagram](./SIMPLE_BLOCK_DIAGRAM.md)** - Simplified system overview

## System Architecture Diagram

```mermaid
graph TB
    %% External Agents
    subgraph "External Agents/Services"
        A1[Web Server Agent<br/>web-01.company.com:8080]
        A2[Database Monitor<br/>db-monitor-01.company.com:5432]
        A3[API Gateway<br/>api-01.company.com:443]
        A4[Cache Monitor<br/>cache-01.company.com:6379]
        A5[Security Scanner<br/>security-01.company.com:8443]
        A6[Log Processor<br/>logs-01.company.com:9200]
    end

    %% Agent Monitor Framework Core
    subgraph "Agent Monitor Framework (localhost:8000)"
        subgraph "FastAPI Application Layer"
            API["/api/v1/agents<br/>REST API Endpoints"]
            DASH["/dashboard<br/>Web Dashboard"]
            HEALTH["/health<br/>Health Check"]
        end

        subgraph "Core Services Layer"
            AR[Agent Registry<br/>agent_registry.py]
            MC[Metrics Collector<br/>metrics_collector.py]
        end

        subgraph "Database Layer"
            PG[(PostgreSQL Database<br/>localhost:5432)]
            subgraph "Database Tables"
                T1[agents table]
                T2[agent_configurations table]
                T3[agent_tags table]
                T4[alert_instances table]
                T5[alert_rules table]
            end
        end
    end

    %% Web Browser
    subgraph "User Interface"
        BROWSER[Web Browser<br/>Dashboard UI]
    end

    %% Data Flow Connections
    %% Agent Registration & Heartbeat
    A1 -->|POST /api/v1/agents/register<br/>Agent Registration| API
    A2 -->|POST /api/v1/agents/register<br/>Agent Registration| API
    A3 -->|POST /api/v1/agents/register<br/>Agent Registration| API
    A4 -->|POST /api/v1/agents/register<br/>Agent Registration| API
    A5 -->|POST /api/v1/agents/register<br/>Agent Registration| API
    A6 -->|POST /api/v1/agents/register<br/>Agent Registration| API

    %% Heartbeat & Metrics (Future Implementation)
    A1 -.->|POST /api/v1/agents/{id}/heartbeat<br/>Status Updates| API
    A2 -.->|POST /api/v1/agents/{id}/metrics<br/>Performance Data| API
    A3 -.->|POST /api/v1/agents/{id}/metrics<br/>Performance Data| API

    %% API to Core Services
    API --> AR
    API --> MC

    %% Core Services to Database
    AR -->|Agent CRUD Operations<br/>SQLAlchemy ORM| PG
    MC -.->|Store Metrics Data<br/>(Future Implementation)| PG

    %% Database Tables
    PG --> T1
    PG --> T2
    PG --> T3
    PG --> T4
    PG --> T5

    %% Dashboard Data Flow
    BROWSER -->|GET /dashboard<br/>Load Dashboard HTML| DASH
    BROWSER -->|GET /api/v1/agents<br/>Fetch Agent Data| API
    API -->|Query Agent Data<br/>via Agent Registry| AR
    AR -->|SELECT * FROM agents<br/>Read Agent Status| PG
    PG -->|Agent List + Metadata<br/>JSON Response| API
    API -->|JSON Agent Data<br/>+ Mock Metrics| BROWSER

    %% Styling
    classDef agentBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef coreBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dbBox fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef uiBox fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class A1,A2,A3,A4,A5,A6 agentBox
    class API,DASH,HEALTH,AR,MC coreBox
    class PG,T1,T2,T3,T4,T5 dbBox
    class BROWSER uiBox
```

## Data Flow Explanation

### 1. Agent Registration Flow
```
External Agent → POST /api/v1/agents/register → Agent Registry → PostgreSQL
```
- Agents send registration data (name, type, host, port, capabilities)
- Agent Registry validates and stores in `agents` table
- Returns unique agent ID and registration status

### 2. Agent Monitoring Flow (Current Implementation)
```
PostgreSQL ← Agent Registry ← GET /api/v1/agents ← Dashboard (Browser)
```
- Dashboard fetches agent list from API
- Agent Registry queries PostgreSQL `agents` table
- Returns agent status, metadata, and basic info
- **Note**: Metrics are currently mock data generated in dashboard

### 3. Future Metrics Collection Flow
```
External Agent → POST /api/v1/agents/{id}/metrics → Metrics Collector → PostgreSQL
```
- Agents will push performance metrics (CPU, memory, response time)
- Metrics Collector will store in dedicated metrics tables
- Dashboard will fetch real metrics instead of mock data

## Current Database Schema

### Main Tables
- **`agents`**: Core agent information (id, name, type, host, status, metadata)
- **`agent_configurations`**: Agent-specific configuration key-value pairs
- **`agent_tags`**: Agent categorization and filtering tags
- **`alert_instances`**: Active/resolved alerts for agents
- **`alert_rules`**: Alert threshold and condition definitions

### Key Fields in `agents` Table
```sql
id                  VARCHAR(36) PRIMARY KEY  -- UUID
name                VARCHAR(255)              -- Display name
type                ENUM                      -- api_agent, monitor_agent, etc.
host                VARCHAR(255)              -- Agent hostname
port                INTEGER                   -- Agent port
status              ENUM                      -- online, offline, error, maintenance
environment         VARCHAR(100)              -- production, staging, development
last_heartbeat      TIMESTAMP                 -- Last contact time
agent_metadata      JSON                      -- Custom metadata
```

## Technology Stack

### Backend
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for database operations
- **asyncpg**: Async PostgreSQL driver
- **PostgreSQL**: Primary data store

### Frontend
- **React 18**: Dashboard UI framework
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Styling framework
- **Chart.js**: Future metrics visualization

### Infrastructure
- **PostgreSQL**: Agent and metrics storage
- **Redis**: Session/cache storage (optional)
- **InfluxDB**: Time-series metrics (future)

## Current Implementation Status

✅ **Completed**:
- Agent registration API
- PostgreSQL database with schema
- Dashboard UI template
- Basic agent CRUD operations
- Real database integration

🔄 **In Progress**:
- Dashboard real-time data display
- Agent heartbeat mechanism

⏳ **Planned**:
- Metrics collection endpoints
- Real-time metrics dashboard
- Alert rule engine
- Agent grouping and orchestration