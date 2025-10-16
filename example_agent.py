"""
Example Agent - Demonstrates how to use the Agent Monitor Client.
"""

import asyncio
import random
import time
from src.agents.client import AgentMonitorClient, AgentConfig
from src.models import AgentType, DeploymentType


async def simulate_work_task():
    """Simulate some work being done by the agent"""
    # Simulate variable work time
    work_time = random.uniform(0.1, 2.0)
    await asyncio.sleep(work_time)
    
    # Simulate occasional failures
    if random.random() < 0.1:  # 10% failure rate
        raise Exception("Simulated task failure")
    
    return work_time * 1000  # Return response time in milliseconds


async def main():
    """Main function to run the example agent"""
    
    # Configure the agent
    config = AgentConfig(
        monitor_url="http://localhost:8000",
        agent_name="Example AI Agent",
        agent_type=AgentType.LLM_AGENT,
        deployment_type=DeploymentType.LOCAL,
        environment="development",
        version="1.0.0",
        description="An example agent for testing the monitoring framework",
        tags=["example", "test", "ai"]
    )
    
    # Create monitoring client
    client = AgentMonitorClient(config)
    
    try:
        # Register with the monitoring system
        print("Registering agent...")
        if not await client.register():
            print("Failed to register agent")
            return
        
        print(f"Agent registered with ID: {client.agent_id}")
        
        # Start monitoring
        print("Starting monitoring...")
        await client.start_monitoring()
        
        # Register custom metrics
        def get_custom_metric():
            return random.uniform(0, 100)
        
        client.register_custom_metric("custom_score", get_custom_metric)
        
        # Simulate agent work
        print("Starting agent work simulation...")
        task_count = 0
        
        while True:
            try:
                # Simulate pending tasks
                pending_tasks = random.randint(0, 5)
                client.set_pending_tasks(pending_tasks)
                
                # Perform a task
                start_time = time.time()
                response_time = await simulate_work_task()
                
                # Record successful task
                client.record_task_completed(response_time)
                task_count += 1
                
                print(f"Completed task {task_count} in {response_time:.1f}ms")
                
                # Wait before next task
                await asyncio.sleep(random.uniform(1, 5))
                
            except Exception as e:
                # Record failed task
                client.record_task_failed()
                print(f"Task failed: {e}")
                
                # Wait before retrying
                await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        print("\nShutting down agent...")
    
    finally:
        # Stop monitoring
        await client.stop_monitoring()
        print("Agent stopped")


if __name__ == "__main__":
    asyncio.run(main())