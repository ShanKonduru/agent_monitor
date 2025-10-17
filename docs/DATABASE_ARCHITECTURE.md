# Database Architecture - Agent Monitor Framework

## Overview

The Agent Monitor Framework uses a **three-tier database architecture** implementing the **Hot/Warm/Cold storage pattern** for optimal performance, scalability, and cost efficiency.

## Database Stack

### 🔴 Redis (Hot Storage) - Port 6379
**Role**: In-Memory Cache & Real-Time Data Store

**Primary Use Cases:**
- **Real-time Data Caching**: Cache frequently accessed agent status and metrics for ultra-fast dashboard responses (<1ms)
- **Session Management**: Store user sessions and authentication tokens
- **Rate Limiting**: Implement API rate limiting for agent endpoints to prevent abuse
- **Pub/Sub Messaging**: Real-time notifications between components (alerts, status changes)
- **Temporary Data Storage**: Queue metrics before batch processing to InfluxDB
- **Live Dashboard Data**: Current agent status, latest metrics, active alerts

**Performance Benefits:**
- Sub-millisecond response times for dashboard queries
- Handles thousands of concurrent dashboard requests
- Instant updates for live monitoring displays
- Memory-efficient storage of only recent/hot data

**Data Retention**: Last 5-10 minutes of metrics, current session data

### 🟠 InfluxDB (Warm Storage) - Port 8086
**Role**: Time Series Database for Historical Metrics

**Primary Use Cases:**
- **Historical Metrics Storage**: Long-term storage of CPU, memory, disk, network metrics
- **Time Series Analysis**: Track performance trends over days/weeks/months
- **Alerting Data**: Store alert history and threshold violations
- **Performance Analytics**: Generate reports on agent performance patterns
- **Data Retention**: Automatic cleanup based on configured retention policies (30 days default)
- **Downsampling**: Reduce data granularity over time (1min → 5min → 1hour → 1day)

**Key Features:**
- **Time Series Optimized**: Designed specifically for timestamped metrics data
- **High Compression**: Efficiently stores millions of metric points
- **Fast Aggregations**: Quick averages, percentiles, min/max calculations
- **Built-in Functions**: Statistical analysis functions for monitoring
- **Automatic Retention**: Configurable data expiration policies

**Data Retention**: 30 days of detailed metrics, longer for aggregated data

### 🟢 PostgreSQL (Cold Storage) - Port 5432
**Role**: Primary Relational Database for Configuration & Metadata

**Primary Use Cases:**
- **Agent Registration**: Agent profiles, configurations, and metadata
- **User Management**: User accounts, permissions, and authentication
- **Configuration Settings**: System settings, thresholds, alert rules
- **Alert Definitions**: Alert rules, notification settings
- **Audit Logs**: System events, user actions, configuration changes
- **Relationships**: Foreign keys between agents, users, groups, etc.

**Data Types**: Structured data requiring ACID transactions and complex relationships

## Architecture Pattern: Hot/Warm/Cold Storage

```mermaid
graph TB
    subgraph "Agent Monitor Framework Database Architecture"
        subgraph "Hot Storage (Redis)"
            R1[Current Agent Status]
            R2[Live Metrics - Last 5min]
            R3[Active Sessions]
            R4[Rate Limiting Counters]
            R5[Real-time Alerts]
        end
        
        subgraph "Warm Storage (InfluxDB)"
            I1[Historical Metrics - 30 days]
            I2[Performance Trends]
            I3[Alert History]
            I4[Downsampled Data]
            I5[Analytics Queries]
        end
        
        subgraph "Cold Storage (PostgreSQL)"
            P1[Agent Configurations]
            P2[User Accounts]
            P3[Alert Rules]
            P4[System Settings]
            P5[Audit Logs]
        end
    end

    subgraph "Data Flow"
        AGENT[Agent] -->|Metrics| API[FastAPI]
        API -->|Store Recent| R1
        API -->|Store Historical| I1
        API -->|Store Config| P1
        
        DASH[Dashboard] -->|Get Live Data| R1
        DASH -->|Get Trends| I1
        DASH -->|Get Config| P1
    end

    classDef hotBox fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    classDef warmBox fill:#ffa726,stroke:#ef6c00,stroke-width:2px,color:#fff
    classDef coldBox fill:#66bb6a,stroke:#388e3c,stroke-width:2px,color:#fff
    
    class R1,R2,R3,R4,R5 hotBox
    class I1,I2,I3,I4,I5 warmBox
    class P1,P2,P3,P4,P5 coldBox
```

## Data Flow Architecture

### 1. Metrics Ingestion Flow
```
Agent → POST /api/v1/agents/{id}/metrics → FastAPI → {
    Redis: Store last 5min for dashboard
    InfluxDB: Store for historical analysis
    PostgreSQL: Update agent last_seen timestamp
}
```

### 2. Dashboard Query Flow
```
Dashboard Request → {
    Live Data: Redis (< 1ms response)
    Historical: InfluxDB (< 100ms response)
    Configuration: PostgreSQL (< 50ms response)
}
```

### 3. Alert Processing Flow
```
Metrics → Threshold Check → {
    Immediate: Redis notification
    History: InfluxDB storage
    Rules: PostgreSQL lookup
}
```

## Performance Characteristics

| Database | Access Time | Use Case | Retention |
|----------|-------------|----------|-----------|
| Redis | < 1ms | Real-time dashboard | 5-10 minutes |
| InfluxDB | < 100ms | Historical analysis | 30 days |
| PostgreSQL | < 50ms | Configuration queries | Permanent |

## Scalability Pattern

### Development Phase (Current)
```
PostgreSQL Only
├── Basic functionality ✅
├── Agent registration ✅
├── Simple metrics in memory ✅
└── Limited to ~10 agents
```

### Production Phase 1 (Next)
```
PostgreSQL + Redis
├── Real-time dashboard ⚡
├── Session management ✅
├── Rate limiting ✅
└── Scales to ~100 agents
```

### Production Phase 2 (Future)
```
PostgreSQL + Redis + InfluxDB
├── Historical analytics 📊
├── Trend analysis ✅
├── Long-term storage ✅
└── Scales to 1000+ agents
```

## Configuration

### Environment Variables
```env
# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/agent_monitor

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=optional_password

# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_influx_token
INFLUXDB_ORG=monitor
INFLUXDB_BUCKET=metrics
```

### Retention Policies
```python
# Default settings in src/config.py
metrics_retention_days: int = 30      # InfluxDB
logs_retention_days: int = 7          # PostgreSQL logs
redis_ttl_seconds: int = 300          # Redis cache
```

## Deployment Considerations

### Local Development
- **PostgreSQL**: Required for basic functionality
- **Redis**: Optional - falls back to in-memory storage
- **InfluxDB**: Optional - metrics stored temporarily in Python

### Production Environment
- **PostgreSQL**: Primary database with backup/replication
- **Redis**: Cluster setup for high availability
- **InfluxDB**: Configured with proper retention and downsampling

### Monitoring & Maintenance
- **PostgreSQL**: Regular backups, index optimization
- **Redis**: Memory usage monitoring, cluster health
- **InfluxDB**: Retention policy management, disk space monitoring

## Error Handling & Fallbacks

The system is designed with **graceful degradation**:

1. **No Redis**: Falls back to in-memory caching (reduced performance)
2. **No InfluxDB**: Metrics stored temporarily in Python memory
3. **PostgreSQL issues**: System stops (critical dependency)

## Security Considerations

- **PostgreSQL**: SSL connections, user permissions, row-level security
- **Redis**: Password authentication, network isolation
- **InfluxDB**: Token-based authentication, organization-level access

## Future Enhancements

1. **Database Sharding**: Distribute data across multiple PostgreSQL instances
2. **Redis Clustering**: High availability and automatic failover
3. **InfluxDB Federation**: Multiple InfluxDB instances for geographic distribution
4. **Read Replicas**: Separate read workloads from write operations
5. **Data Lake Integration**: Long-term archival to cloud storage

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**: Check Redis service status, network connectivity
2. **InfluxDB Timeout**: Verify InfluxDB is running, check resource usage
3. **PostgreSQL Slow Queries**: Review query plans, add indexes
4. **Memory Issues**: Monitor Redis memory usage, implement eviction policies

### Performance Tuning

1. **Redis**: Configure memory limits, enable compression
2. **InfluxDB**: Optimize shard duration, configure downsampling
3. **PostgreSQL**: Tune connection pooling, optimize queries

This architecture ensures the Agent Monitor Framework can scale from development to enterprise production environments while maintaining optimal performance and reliability.