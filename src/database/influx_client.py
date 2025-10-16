"""
InfluxDB client for storing and retrieving time-series metrics data.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from influxdb_client import Point
from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

from src.database.connection import db_manager
from src.models import AgentMetrics

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesQuery:
    """Query parameters for time-series data"""
    measurement: str
    start_time: datetime
    end_time: Optional[datetime] = None
    agent_id: Optional[str] = None
    fields: Optional[List[str]] = None
    aggregation: Optional[str] = None  # mean, max, min, sum, count
    window: Optional[str] = None  # 1m, 5m, 1h, etc.


class InfluxDBClient:
    """InfluxDB client for time-series operations"""
    
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        self.bucket = None
        self.org = None
    
    async def initialize(self):
        """Initialize InfluxDB client"""
        self.client = await db_manager.get_influx()
        if self.client:
            self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
            self.query_api = self.client.query_api()
            self.bucket = db_manager.influx_client.bucket if hasattr(db_manager, 'influx_client') else "metrics"
            self.org = db_manager.influx_client.org if hasattr(db_manager, 'influx_client') else "monitor"
            logger.info("InfluxDB client initialized")
        else:
            logger.warning("InfluxDB not available")
    
    async def write_agent_metrics(self, metrics: AgentMetrics) -> bool:
        """Write agent metrics to InfluxDB"""
        if not self.client or not self.write_api:
            logger.warning("InfluxDB not available for writing metrics")
            return False
        
        try:
            points = self._convert_metrics_to_points(metrics)
            await self.write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=points,
                write_precision=WritePrecision.S
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to write metrics to InfluxDB: {e}")
            return False
    
    def _convert_metrics_to_points(self, metrics: AgentMetrics) -> List[Point]:
        """Convert AgentMetrics to InfluxDB Points"""
        points = []
        timestamp = metrics.timestamp
        agent_id = metrics.agent_id
        
        # Resource metrics
        if metrics.resource_metrics:
            resource_point = Point("resource_metrics") \
                .tag("agent_id", agent_id) \
                .time(timestamp, WritePrecision.S)
            
            resource_data = metrics.resource_metrics.model_dump()
            for field, value in resource_data.items():
                if value is not None:
                    resource_point = resource_point.field(field, float(value))
            
            points.append(resource_point)
        
        # Performance metrics
        if metrics.performance_metrics:
            perf_point = Point("performance_metrics") \
                .tag("agent_id", agent_id) \
                .time(timestamp, WritePrecision.S)
            
            perf_data = metrics.performance_metrics.model_dump()
            for field, value in perf_data.items():
                if value is not None:
                    perf_point = perf_point.field(field, float(value))
            
            points.append(perf_point)
        
        # AI metrics
        if metrics.ai_metrics:
            ai_point = Point("ai_metrics") \
                .tag("agent_id", agent_id) \
                .time(timestamp, WritePrecision.S)
            
            ai_data = metrics.ai_metrics.model_dump()
            for field, value in ai_data.items():
                if value is not None:
                    ai_point = ai_point.field(field, float(value))
            
            points.append(ai_point)
        
        # Custom metrics
        if metrics.custom_metrics:
            custom_point = Point("custom_metrics") \
                .tag("agent_id", agent_id) \
                .time(timestamp, WritePrecision.S)
            
            for field, value in metrics.custom_metrics.items():
                if value is not None:
                    try:
                        custom_point = custom_point.field(field, float(value))
                    except (ValueError, TypeError):
                        # Skip non-numeric custom metrics
                        continue
            
            points.append(custom_point)
        
        return points
    
    async def query_agent_metrics(
        self, 
        query: TimeSeriesQuery
    ) -> List[Dict[str, Any]]:
        """Query time-series metrics data"""
        if not self.client or not self.query_api:
            logger.warning("InfluxDB not available for querying")
            return []
        
        try:
            flux_query = self._build_flux_query(query)
            tables = await self.query_api.query(flux_query, org=self.org)
            
            results = []
            for table in tables:
                for record in table.records:
                    results.append({
                        "time": record.get_time(),
                        "agent_id": record.values.get("agent_id"),
                        "measurement": record.get_measurement(),
                        "field": record.get_field(),
                        "value": record.get_value()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query InfluxDB: {e}")
            return []
    
    def _build_flux_query(self, query: TimeSeriesQuery) -> str:
        """Build Flux query from TimeSeriesQuery parameters"""
        # Base query
        flux_parts = [
            f'from(bucket: "{self.bucket}")',
            f'|> range(start: {self._format_time(query.start_time)}'
        ]
        
        if query.end_time:
            flux_parts[-1] += f', stop: {self._format_time(query.end_time)}'
        flux_parts[-1] += ')'
        
        # Filter by measurement
        flux_parts.append(f'|> filter(fn: (r) => r["_measurement"] == "{query.measurement}")')
        
        # Filter by agent_id
        if query.agent_id:
            flux_parts.append(f'|> filter(fn: (r) => r["agent_id"] == "{query.agent_id}")')
        
        # Filter by fields
        if query.fields:
            field_filter = " or ".join([f'r["_field"] == "{field}"' for field in query.fields])
            flux_parts.append(f'|> filter(fn: (r) => {field_filter})')
        
        # Aggregation
        if query.aggregation and query.window:
            flux_parts.append(f'|> aggregateWindow(every: {query.window}, fn: {query.aggregation}, createEmpty: false)')
        elif query.aggregation:
            flux_parts.append(f'|> {query.aggregation}()')
        
        # Sort by time
        flux_parts.append('|> sort(columns: ["_time"])')
        
        return '\n  '.join(flux_parts)
    
    def _format_time(self, dt: datetime) -> str:
        """Format datetime for Flux query"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    
    async def get_agent_metrics_summary(
        self, 
        agent_id: str, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get summary metrics for an agent over the specified time period"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        summary = {
            "agent_id": agent_id,
            "time_period": f"{hours}h",
            "resource_metrics": {},
            "performance_metrics": {},
            "ai_metrics": {}
        }
        
        # Query each metric type
        for measurement in ["resource_metrics", "performance_metrics", "ai_metrics"]:
            query = TimeSeriesQuery(
                measurement=measurement,
                start_time=start_time,
                end_time=end_time,
                agent_id=agent_id,
                aggregation="mean"
            )
            
            results = await self.query_agent_metrics(query)
            for result in results:
                field_name = result["field"]
                value = result["value"]
                summary[measurement][field_name] = value
        
        return summary
    
    async def get_system_overview(self, hours: int = 1) -> Dict[str, Any]:
        """Get system-wide metrics overview"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        overview = {
            "time_period": f"{hours}h",
            "total_agents": 0,
            "avg_cpu_usage": 0,
            "avg_memory_usage": 0,
            "total_tasks_completed": 0,
            "avg_response_time": 0,
            "error_rate": 0
        }
        
        # Count unique agents
        agent_query = TimeSeriesQuery(
            measurement="resource_metrics",
            start_time=start_time,
            end_time=end_time,
            fields=["cpu_usage_percent"]
        )
        
        results = await self.query_agent_metrics(agent_query)
        unique_agents = set()
        cpu_values = []
        
        for result in results:
            if result["agent_id"]:
                unique_agents.add(result["agent_id"])
            if result["value"] is not None:
                cpu_values.append(result["value"])
        
        overview["total_agents"] = len(unique_agents)
        if cpu_values:
            overview["avg_cpu_usage"] = sum(cpu_values) / len(cpu_values)
        
        # Similar queries for other metrics...
        # (Simplified for demo)
        
        return overview
    
    async def cleanup_old_data(self, days: int = 90):
        """Delete data older than specified days"""
        if not self.client:
            logger.warning("InfluxDB not available for cleanup")
            return
        
        try:
            delete_api = self.client.delete_api()
            start = "1970-01-01T00:00:00Z"
            stop = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            await delete_api.delete(start, stop, '_measurement="resource_metrics"', bucket=self.bucket, org=self.org)
            await delete_api.delete(start, stop, '_measurement="performance_metrics"', bucket=self.bucket, org=self.org)
            await delete_api.delete(start, stop, '_measurement="ai_metrics"', bucket=self.bucket, org=self.org)
            await delete_api.delete(start, stop, '_measurement="custom_metrics"', bucket=self.bucket, org=self.org)
            
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Global InfluxDB client instance
influx_client = InfluxDBClient()