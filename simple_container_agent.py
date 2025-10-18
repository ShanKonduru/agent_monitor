"""
Simple Container Demo Agent - Simplified for Docker demonstration
No external database dependencies - works with existing API
"""

import asyncio
import random
import time
import os
import logging
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class SimpleContainerAgent:
    """Simple agent for container demonstration"""
    
    def __init__(self):
        self.agent_name = os.getenv('AGENT_NAME', 'Container Demo Agent')
        self.agent_type = os.getenv('AGENT_TYPE', 'llm_agent')
        self.workload_type = os.getenv('WORKLOAD_TYPE', 'standard')
        self.monitor_url = os.getenv('MONITOR_URL', 'http://localhost:8000')
        self.environment = os.getenv('AGENT_ENVIRONMENT', 'container')
        self.agent_id = None
        self.task_count = 0
        self.is_running = False
        
    async def register(self):
        """Register with the monitoring system"""
        registration_data = {
            "name": self.agent_name,
            "type": self.agent_type,
            "version": os.getenv('AGENT_VERSION', '1.0.0'),
            "description": f"Container demo agent - {self.workload_type} workload",
            "deployment_type": os.getenv("AGENT_ENVIRONMENT", "DOCKER"),
            "host": f"container-{random.randint(1000, 9999)}",
            "environment": self.environment,
            "tags": ["container", "demo", self.workload_type, "docker"]
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.monitor_url}/api/v1/agents/register",
                    json=registration_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.agent_id = result["agent_id"]
                    logger.info(f"✅ {self.agent_name} registered! ID: {self.agent_id}")
                    return True
                else:
                    logger.error(f"Registration failed: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return False
    
    async def update_status(self, status: str = "running"):
        """Update agent status"""
        if not self.agent_id:
            return
            
        status_data = {
            "status": status,
            "tasks_completed": self.task_count,
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.monitor_url}/api/v1/agents/{self.agent_id}/status",
                    json=status_data
                )
                if response.status_code != 200:
                    logger.warning(f"Status update failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"Status update error: {e}")
    
    async def simulate_workload(self):
        """Simulate different types of workloads"""
        if self.workload_type == "llm":
            # LLM processing - longer tasks
            processing_time = random.uniform(2, 8)
            await asyncio.sleep(processing_time)
            logger.info(f"🤖 Processed LLM request in {processing_time:.1f}s")
            
        elif self.workload_type == "api":
            # API processing - fast tasks
            processing_time = random.uniform(0.1, 1.0)
            await asyncio.sleep(processing_time)
            logger.info(f"🌐 Handled API request in {processing_time:.1f}s")
            
        elif self.workload_type == "data":
            # Data processing - batch tasks
            processing_time = random.uniform(1, 5)
            await asyncio.sleep(processing_time)
            logger.info(f"📊 Processed data batch in {processing_time:.1f}s")
            
        else:
            # Standard processing
            processing_time = random.uniform(0.5, 3.0)
            await asyncio.sleep(processing_time)
            logger.info(f"⚙️ Completed task in {processing_time:.1f}s")
        
        return processing_time
    
    async def run(self):
        """Main agent loop"""
        logger.info(f"🚀 Starting {self.agent_name} ({self.workload_type} workload)")
        
        # Register with monitoring system
        if not await self.register():
            logger.error("Failed to register - exiting")
            return
        
        self.is_running = True
        await self.update_status("online")
        
        try:
            while self.is_running:
                # Simulate work
                await self.simulate_workload()
                self.task_count += 1
                
                # Update status periodically
                if self.task_count % 10 == 0:
                    await self.update_status("running")
                    logger.info(f"📈 Completed {self.task_count} tasks")
                
                # Wait before next task
                wait_time = self._get_wait_time()
                await asyncio.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.update_status("stopped")
            logger.info(f"🛑 {self.agent_name} stopped after {self.task_count} tasks")
    
    def _get_wait_time(self):
        """Get wait time based on workload type"""
        if self.workload_type == "llm":
            return random.uniform(3, 10)  # LLMs are slower
        elif self.workload_type == "api":
            return random.uniform(0.5, 2)  # APIs are fast
        elif self.workload_type == "data":
            return random.uniform(2, 6)   # Batch processing
        else:
            return random.uniform(1, 4)   # Standard

async def main():
    """Main function"""
    agent = SimpleContainerAgent()
    await agent.run()

if __name__ == "__main__":
    # Display container info
    print("🐳 Container Agent Starting...")
    print(f"Agent: {os.getenv('AGENT_NAME', 'Container Demo Agent')}")
    print(f"Type: {os.getenv('AGENT_TYPE', 'llm_agent')}")
    print(f"Workload: {os.getenv('WORKLOAD_TYPE', 'standard')}")
    print(f"Monitor: {os.getenv('MONITOR_URL', 'http://localhost:8000')}")
    print("=" * 50)
    
    asyncio.run(main())