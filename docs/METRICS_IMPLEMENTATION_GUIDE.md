## Implementation Guide: Adding Real Metrics Collection

### 🎯 **Goal**: Extend system so agents push real monitoring data to database

---

## **Phase 1: Add Metrics API Endpoints**

### 1. Create Metrics Database Table
```sql
-- Add to database/models.py
class AgentMetrics(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agents.id"))
    timestamp = Column(DateTime(timezone=True), default=func.now())
    cpu_usage = Column(Float)  # percentage
    memory_usage = Column(Float)  # percentage  
    response_time = Column(Float)  # milliseconds
    requests_per_minute = Column(Integer)
    error_rate = Column(Float)  # percentage
    custom_metrics = Column(JSON)  # flexible metrics storage
```

### 2. Add Metrics API Endpoints
```python
# Add to api/agents.py
@router.post("/{agent_id}/metrics")
async def submit_metrics(agent_id: str, metrics: AgentMetricsData):
    """Agents submit performance metrics"""
    try:
        # Store metrics in database
        metric_record = AgentMetrics(
            agent_id=agent_id,
            cpu_usage=metrics.cpu_usage,
            memory_usage=metrics.memory_usage,
            response_time=metrics.response_time,
            # ... other metrics
        )
        # Save to database
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store metrics")

@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str, hours: int = 24):
    """Dashboard gets agent metrics for charts"""
    # Query last N hours of metrics for agent
    # Return time-series data for charts
```

---

## **Phase 2: Agent-Side Implementation**

### 3. Agent Metrics Collection Script
```python
# Example: agent_metrics_client.py (runs on each monitored server)
import psutil
import requests
import time
from datetime import datetime

class AgentMetricsClient:
    def __init__(self, agent_id, monitor_server_url):
        self.agent_id = agent_id
        self.server_url = monitor_server_url
        
    def collect_system_metrics(self):
        """Collect real system metrics"""
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": self.get_network_io(),
            "response_time": self.measure_response_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def send_metrics(self, metrics):
        """Send metrics to monitor server"""
        url = f"{self.server_url}/api/v1/agents/{self.agent_id}/metrics"
        response = requests.post(url, json=metrics)
        return response.status_code == 200
    
    def run_continuous_monitoring(self, interval_seconds=60):
        """Run continuous metrics collection"""
        while True:
            try:
                metrics = self.collect_system_metrics()
                success = self.send_metrics(metrics)
                print(f"Metrics sent: {success} at {metrics['timestamp']}")
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            time.sleep(interval_seconds)

# Usage on each monitored server:
if __name__ == "__main__":
    client = AgentMetricsClient(
        agent_id="web-server-01",
        monitor_server_url="http://localhost:8000"
    )
    client.run_continuous_monitoring(interval_seconds=30)
```

---

## **Phase 3: Dashboard Real-Time Updates**

### 4. Update Dashboard to Use Real Metrics
```javascript
// In dashboard.html - replace mock metrics with real API calls
const fetchAgentMetrics = async (agentId) => {
    try {
        const response = await axios.get(
            `${API_BASE_URL}/agents/${agentId}/metrics?hours=24`
        );
        return response.data.metrics;
    } catch (error) {
        console.error(`Failed to fetch metrics for ${agentId}:`, error);
        return [];
    }
};

const updateDashboardWithRealMetrics = async () => {
    // Get all agents
    const agents = await fetchAgents();
    
    // Fetch metrics for each agent
    const agentMetrics = {};
    for (const agent of agents) {
        agentMetrics[agent.id] = await fetchAgentMetrics(agent.id);
    }
    
    // Update charts with real data
    updateCharts(agentMetrics);
    setAgents(agents.map(agent => ({
        ...agent,
        metrics: agentMetrics[agent.id] || []
    })));
};
```

---

## **Phase 4: Deployment Strategy**

### 5. Deploy Monitoring Agents
```bash
# On each server you want to monitor:

# 1. Install monitoring agent
pip install psutil requests

# 2. Configure agent
cat > /etc/agent-monitor/config.json << EOF
{
  "agent_id": "web-server-01",
  "monitor_server": "http://monitoring.company.com:8000",
  "metrics_interval": 30,
  "heartbeat_interval": 60
}
EOF

# 3. Start as service
python agent_metrics_client.py --config /etc/agent-monitor/config.json
```

---

## **Current vs Future Architecture**

### **CURRENT (What We Have)**
```
Agents → [Registration Only] → PostgreSQL → Dashboard
         POST /register              SELECT agents
```

### **FUTURE (With Metrics)**
```
Agents → [Registration + Metrics] → PostgreSQL → Dashboard
         POST /register              INSERT metrics
         POST /metrics               SELECT metrics + agents
         POST /heartbeat
```

---

## **Quick Implementation Steps**

### **For Testing (30 minutes)**
1. Add `AgentMetrics` table to `models.py`
2. Add metrics endpoints to `api/agents.py`
3. Create simple metrics sender script
4. Test with one dummy agent

### **For Production (2-3 hours)**
1. Implement full metrics collection
2. Add dashboard real-time updates
3. Create agent deployment scripts
4. Add error handling and retries

### **Advanced Features (Future)**
1. Alert rules based on metrics thresholds
2. Metrics aggregation and historical analysis
3. Custom metrics and dashboards
4. Distributed monitoring coordination

Would you like me to implement any specific part of this metrics collection system?