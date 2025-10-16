"""
Live Demo of the Agent Monitor Framework
"""
import asyncio
import httpx
import time
from datetime import datetime

print('🔥 Agent Monitor Framework - Live Demo!')
print('=' * 60)

async def test_connection():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://0.0.0.0:8000/')
            if response.status_code == 200:
                print('✅ Server is running!')
                print(f'Response: {response.json()}')
                return True
        except Exception as e:
            print(f'❌ Connection failed: {e}')
            return False
    return False

async def demo():
    # Test connection first
    print('🔍 Testing connection to monitoring server...')
    if not await test_connection():
        print('❌ Please start the monitoring server first')
        return
    
    async with httpx.AsyncClient() as client:
        print()
        print('🤖 Registering Demo Agent...')
        
        # Register agent
        agent_data = {
            'name': 'Live Demo Agent',
            'type': 'llm_agent',
            'version': '1.0.0',
            'description': 'Demonstrating the monitoring framework',
            'deployment_type': 'local',
            'host': 'localhost',
            'environment': 'demo',
            'tags': ['demo', 'live']
        }
        
        try:
            response = await client.post('http://0.0.0.0:8000/api/v1/agents/register', json=agent_data)
            if response.status_code == 200:
                result = response.json()
                agent_id = result['agent_id']
                print(f'✅ Agent registered successfully!')
                print(f'🆔 Agent ID: {agent_id}')
                print(f'📋 Status: {result["status"]}')
                
                # Send some metrics
                print()
                print('📊 Sending performance metrics...')
                
                for i in range(3):
                    metrics = {
                        'agent_id': agent_id,
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'resource_metrics': {
                            'cpu_usage_percent': 30 + i * 10,
                            'memory_usage_percent': 40 + i * 5
                        },
                        'performance_metrics': {
                            'tasks_completed': 10 + i * 5,
                            'tasks_failed': i,
                            'average_response_time_ms': 200 + i * 50
                        }
                    }
                    
                    response = await client.post(f'http://0.0.0.0:8000/api/v1/agents/{agent_id}/metrics', json=metrics)
                    if response.status_code == 200:
                        cpu = metrics["resource_metrics"]["cpu_usage_percent"]
                        print(f'  ✅ Metrics batch {i+1} sent (CPU: {cpu}%)')
                    else:
                        print(f'  ❌ Metrics batch {i+1} failed')
                    
                    # Send heartbeat
                    response = await client.post(f'http://0.0.0.0:8000/api/v1/agents/{agent_id}/heartbeat')
                    if response.status_code == 200:
                        print(f'  💓 Heartbeat {i+1} sent')
                    
                    await asyncio.sleep(1)
                
                print()
                print('🎉 Demo Complete!')
                print('📊 Key features demonstrated:')
                print('   ✅ Agent registration with the monitoring system')
                print('   📈 Real-time metrics collection and submission')
                print('   💓 Heartbeat monitoring for agent health')
                print('   🔗 RESTful API communication')
                print()
                print('🌐 You can view the API documentation at:')
                print('   http://0.0.0.0:8000/docs')
                print('   http://0.0.0.0:8000/api/v2/system/info (Phase 2 info)')
                
            else:
                print(f'❌ Registration failed: {response.status_code}')
                
        except Exception as e:
            print(f'❌ Demo error: {e}')

if __name__ == "__main__":
    asyncio.run(demo())