"""
Demo Agent - Shows the Agent Monitor Framework in action!
"""
import asyncio
import random
import time
import json
import httpx
from datetime import datetime

class DemoAgent:
    """A simple demo agent that shows monitoring in action"""
    
    def __init__(self):
        self.agent_id = None
        self.monitor_url = "http://127.0.0.1:8000"
        self.is_running = False
        self.task_count = 0
        self.failed_tasks = 0
        self.start_time = time.time()
        
    async def register(self):
        """Register with the monitoring system"""
        registration_data = {
            "name": "Demo AI Agent",
            "type": "llm_agent",
            "version": "1.0.0",
            "description": "A demo agent showing the monitoring framework",
            "deployment_type": "local",
            "host": "localhost",
            "environment": "demo",
            "tags": ["demo", "example", "ai"]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.monitor_url}/api/v1/agents/register",
                    json=registration_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.agent_id = result["agent_id"]
                    print(f"✅ Agent registered! ID: {self.agent_id}")
                    print(f"📋 Status: {result['status']}")
                    print(f"💬 Message: {result['message']}")
                    return True
                else:
                    print(f"❌ Registration failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Registration error: {e}")
                return False
    
    async def send_heartbeat(self):
        """Send heartbeat to monitoring system"""
        if not self.agent_id:
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.monitor_url}/api/v1/agents/{self.agent_id}/heartbeat",
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception:
                return False
    
    async def send_metrics(self):
        """Send performance metrics"""
        if not self.agent_id:
            return False
        
        # Calculate current metrics
        uptime = time.time() - self.start_time
        cpu_usage = random.uniform(20, 80)  # Simulate CPU usage
        memory_usage = random.uniform(30, 70)  # Simulate memory usage
        
        metrics_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "resource_metrics": {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_bytes": int(1024*1024*500),  # 500MB
                "memory_usage_percent": memory_usage,
                "disk_usage_bytes": int(1024*1024*1024*5),  # 5GB
                "disk_io_read_bytes": random.randint(1000, 10000),
                "disk_io_write_bytes": random.randint(1000, 10000),
                "network_io_rx_bytes": random.randint(5000, 50000),
                "network_io_tx_bytes": random.randint(5000, 50000)
            },
            "performance_metrics": {
                "tasks_completed": self.task_count,
                "tasks_failed": self.failed_tasks,
                "tasks_pending": random.randint(0, 5),
                "average_response_time_ms": random.uniform(100, 500),
                "throughput_per_second": self.task_count / max(1, uptime),
                "error_rate": self.failed_tasks / max(1, self.task_count + self.failed_tasks),
                "success_rate": self.task_count / max(1, self.task_count + self.failed_tasks),
                "uptime_seconds": int(uptime)
            },
            "ai_metrics": {
                "model_inference_time_ms": random.uniform(50, 200),
                "model_accuracy": random.uniform(0.85, 0.98),
                "confidence_score": random.uniform(0.7, 0.95),
                "tokens_processed": random.randint(100, 1000),
                "tokens_per_second": random.uniform(50, 200),
                "context_length": random.randint(500, 2000),
                "api_calls_made": random.randint(1, 10),
                "api_call_latency_ms": random.uniform(20, 100)
            },
            "custom_metrics": {
                "demo_score": random.uniform(0, 100),
                "user_satisfaction": random.uniform(0.8, 1.0)
            },
            "health_checks": {
                "connectivity": True,
                "model_loaded": True,
                "api_responsive": True
            },
            "alerts": []
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.monitor_url}/api/v1/agents/{self.agent_id}/metrics",
                    json=metrics_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"⚠️ Metrics send failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"⚠️ Metrics error: {e}")
                return False
    
    async def simulate_work(self):
        """Simulate agent doing work"""
        work_types = ["Text Generation", "Image Analysis", "Data Processing", "API Call", "Model Inference"]
        
        work_type = random.choice(work_types)
        work_time = random.uniform(0.5, 3.0)  # 0.5 to 3 seconds
        
        print(f"🔄 Performing: {work_type}")
        await asyncio.sleep(work_time)
        
        # Simulate occasional failures (10% chance)
        if random.random() < 0.1:
            self.failed_tasks += 1
            print(f"❌ Task failed: {work_type} (failure rate: {self.failed_tasks}/{self.task_count + self.failed_tasks})")
        else:
            self.task_count += 1
            print(f"✅ Task completed: {work_type} in {work_time:.1f}s (total: {self.task_count})")
    
    async def run_demo(self):
        """Run the demo agent"""
        print("🚀 Starting Demo Agent for Agent Monitor Framework")
        print("=" * 60)
        
        # Register with monitoring system
        if not await self.register():
            print("❌ Failed to register. Make sure the monitoring server is running!")
            return
        
        print()
        self.is_running = True
        heartbeat_counter = 0
        metrics_counter = 0
        
        try:
            while self.is_running:
                # Perform work
                await self.simulate_work()
                
                # Send heartbeat every 15 seconds
                heartbeat_counter += 1
                if heartbeat_counter >= 5:  # Every 5 tasks
                    heartbeat_ok = await self.send_heartbeat()
                    if heartbeat_ok:
                        print("💓 Heartbeat sent successfully")
                    else:
                        print("⚠️ Heartbeat failed")
                    heartbeat_counter = 0
                
                # Send metrics every 30 seconds
                metrics_counter += 1
                if metrics_counter >= 8:  # Every 8 tasks
                    metrics_ok = await self.send_metrics()
                    if metrics_ok:
                        print("📊 Metrics sent successfully")
                        print(f"📈 Current stats: {self.task_count} completed, {self.failed_tasks} failed")
                    else:
                        print("⚠️ Metrics send failed")
                    metrics_counter = 0
                
                # Wait between tasks
                await asyncio.sleep(random.uniform(2, 5))
                
        except KeyboardInterrupt:
            print("\n🛑 Demo stopped by user")
        except Exception as e:
            print(f"❌ Demo error: {e}")
        
        self.is_running = False
        print(f"\n📋 Final Stats:")
        print(f"   ✅ Tasks Completed: {self.task_count}")
        print(f"   ❌ Tasks Failed: {self.failed_tasks}")
        print(f"   ⏱️ Running Time: {time.time() - self.start_time:.1f} seconds")
        print(f"\n🎉 Demo Complete! Check the monitoring dashboard at:")
        print(f"   📊 API: {self.monitor_url}/docs")
        print(f"   📈 System Status: {self.monitor_url}/api/v1/system/status")

async def main():
    agent = DemoAgent()
    await agent.run_demo()

if __name__ == "__main__":
    print("🔥 Agent Monitor Framework - Live Demo!")
    print("Make sure the monitoring server is running on http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the demo\n")
    
    asyncio.run(main())