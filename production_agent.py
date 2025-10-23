"""
Production AI Agent - Simulates real-world AI workloads in containers
"""

import asyncio
import random
import time
import os
import json
import logging
from datetime import datetime
from src.agents.client import AgentMonitorClient, AgentConfig
from src.models import AgentType, DeploymentType

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class ProductionAgent:
    """A production-ready agent for container deployment"""
    
    def __init__(self, agent_name: str, agent_type: AgentType, workload_type: str = "standard"):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.workload_type = workload_type
        self.client = None
        self.task_count = 0
        self.is_running = False
        
    async def initialize(self):
        """Initialize the agent with monitoring"""
        config = AgentConfig(
            monitor_url=os.getenv('MONITOR_URL', 'http://localhost:8000'),
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            deployment_type=DeploymentType.DOCKER,
            environment=os.getenv('AGENT_ENVIRONMENT', 'production'),
            version=os.getenv('AGENT_VERSION', '1.0.0'),
            description=f"Production {self.workload_type} agent running in container",
            tags=["production", "container", self.workload_type, "docker"]
        )
        
        self.client = AgentMonitorClient(config)
        
        # Register with monitoring system
        logger.info(f"Registering {self.agent_name}...")
        if not await self.client.register():
            logger.error("Failed to register agent")
            return False
            
        logger.info(f"Agent registered with ID: {self.client.agent_id}")
        
        # Start monitoring
        await self.client.start_monitoring()
        
        # Register custom metrics based on workload type
        self._register_custom_metrics()
        
        return True
    
    def _register_custom_metrics(self):
        """Register workload-specific custom metrics"""
        if self.workload_type == "llm":
            # LLM-specific metrics
            def get_token_count():
                return random.randint(50, 2000)
            
            def get_model_accuracy():
                return random.uniform(0.85, 0.99)
            
            def get_tokens_per_second():
                return random.uniform(10.0, 100.0)
            
            def get_model_inference_time():
                return random.uniform(50.0, 500.0)  # ms
            
            def get_context_length():
                return random.randint(512, 4096)
            
            def get_api_call_latency():
                return random.uniform(20.0, 200.0)  # ms
                
            self.client.register_custom_metric("tokens_processed", get_token_count)
            self.client.register_custom_metric("model_accuracy", get_model_accuracy)
            self.client.register_custom_metric("tokens_per_second", get_tokens_per_second)
            self.client.register_custom_metric("model_inference_time_ms", get_model_inference_time)
            self.client.register_custom_metric("context_length", get_context_length)
            self.client.register_custom_metric("api_call_latency_ms", get_api_call_latency)
            
        elif self.workload_type == "api":
            # API-specific metrics
            def get_request_rate():
                return random.uniform(10, 100)
                
            def get_cache_hit_ratio():
                return random.uniform(0.6, 0.9)
                
            self.client.register_custom_metric("requests_per_minute", get_request_rate)
            self.client.register_custom_metric("cache_hit_ratio", get_cache_hit_ratio)
            
        elif self.workload_type == "data":
            # Data processing metrics
            def get_records_processed():
                return random.randint(100, 10000)
                
            def get_processing_throughput():
                return random.uniform(50, 500)
                
            self.client.register_custom_metric("records_per_batch", get_records_processed)
            self.client.register_custom_metric("throughput_mbps", get_processing_throughput)
    
    async def simulate_workload(self):
        """Simulate workload based on agent type"""
        if self.workload_type == "llm":
            return await self._simulate_llm_workload()
        elif self.workload_type == "api":
            return await self._simulate_api_workload()
        elif self.workload_type == "data":
            return await self._simulate_data_workload()
        else:
            return await self._simulate_standard_workload()
    
    async def _simulate_llm_workload(self):
        """Simulate LLM processing"""
        # Simulate variable token processing time
        tokens = random.randint(50, 2000)
        processing_time = tokens * random.uniform(0.001, 0.005)  # Time per token
        await asyncio.sleep(processing_time)
        
        # Simulate occasional model loading delays
        if random.random() < 0.05:  # 5% chance of model reload
            await asyncio.sleep(random.uniform(2, 5))
            
        return processing_time * 1000
    
    async def _simulate_api_workload(self):
        """Simulate API request processing"""
        # Simulate request processing
        processing_time = random.uniform(0.05, 0.5)
        await asyncio.sleep(processing_time)
        
        # Simulate database queries
        if random.random() < 0.3:  # 30% require DB access
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
        return processing_time * 1000
    
    async def _simulate_data_workload(self):
        """Simulate data processing"""
        # Simulate batch processing
        batch_size = random.randint(100, 1000)
        processing_time = batch_size * random.uniform(0.0001, 0.001)
        await asyncio.sleep(processing_time)
        
        # Simulate I/O operations
        if random.random() < 0.4:  # 40% require file I/O
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
        return processing_time * 1000
    
    async def _simulate_standard_workload(self):
        """Simulate standard processing"""
        processing_time = random.uniform(0.1, 2.0)
        await asyncio.sleep(processing_time)
        return processing_time * 1000
    
    async def run(self):
        """Main agent loop"""
        self.is_running = True
        logger.info(f"Starting {self.agent_name} with {self.workload_type} workload...")
        
        while self.is_running:
            try:
                # Set pending tasks
                pending_tasks = random.randint(0, 10)
                self.client.set_pending_tasks(pending_tasks)
                
                # Process a task
                start_time = time.time()
                response_time = await self.simulate_workload()
                
                # Record successful task
                self.client.record_task_completed(response_time)
                self.task_count += 1
                
                if self.task_count % 50 == 0:  # Log every 50 tasks
                    logger.info(f"Completed {self.task_count} tasks (last: {response_time:.1f}ms)")
                
                # Wait before next task (simulate realistic workload)
                wait_time = self._get_wait_time()
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                # Record failed task
                self.client.record_task_failed()
                logger.error(f"Task failed: {e}")
                await asyncio.sleep(random.uniform(1, 3))
    
    def _get_wait_time(self):
        """Get wait time based on workload type"""
        if self.workload_type == "llm":
            return random.uniform(2, 8)  # LLMs process slower
        elif self.workload_type == "api":
            return random.uniform(0.1, 1)  # APIs are fast
        elif self.workload_type == "data":
            return random.uniform(1, 5)  # Batch processing
        else:
            return random.uniform(1, 3)
    
    async def stop(self):
        """Stop the agent gracefully"""
        self.is_running = False
        if self.client:
            await self.client.stop_monitoring()
        logger.info(f"Agent stopped after processing {self.task_count} tasks")


async def main():
    """Main function to run the production agent"""
    
    # Get configuration from environment
    agent_name = os.getenv('AGENT_NAME', 'Production Agent')
    agent_type_str = os.getenv('AGENT_TYPE', 'llm_agent')
    workload_type = os.getenv('WORKLOAD_TYPE', 'standard')
    
    # Map string to enum
    agent_type_map = {
        'llm_agent': AgentType.LLM_AGENT,
        'api_agent': AgentType.API_AGENT,
        'monitor_agent': AgentType.MONITOR_AGENT,
        'data_agent': AgentType.DATA_AGENT
    }
    
    agent_type = agent_type_map.get(agent_type_str, AgentType.LLM_AGENT)
    
    # Create and initialize agent
    agent = ProductionAgent(agent_name, agent_type, workload_type)
    
    try:
        if await agent.initialize():
            await agent.run()
        else:
            logger.error("Failed to initialize agent")
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())