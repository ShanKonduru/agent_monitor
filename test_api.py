"""
Test script to verify the Agent Monitor Framework API is working.
"""
import asyncio
import httpx
import json

async def test_api():
    """Test the monitoring API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing Agent Monitor Framework API...")
        print("-" * 50)
        
        # Test 1: System Status
        try:
            response = await client.get(f"{base_url}/api/v1/system/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ System Status: HEALTHY")
                print(f"   - Total Agents: {data.get('total_agents', 0)}")
                print(f"   - Active Agents: {data.get('active_agents', 0)}")
                print(f"   - Version: {data.get('version', 'unknown')}")
            else:
                print(f"❌ System Status: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ System Status: CONNECTION ERROR - {e}")
            return False
        
        print()
        
        # Test 2: List Agents (should be empty initially)
        try:
            response = await client.get(f"{base_url}/api/v1/agents/")
            if response.status_code == 200:
                agents = response.json()
                print(f"✅ Agents List: SUCCESS ({len(agents)} agents)")
                if agents:
                    for agent in agents[:3]:  # Show first 3
                        print(f"   - {agent.get('name', 'Unknown')} [{agent.get('status', 'unknown')}]")
                else:
                    print("   - No agents registered yet")
            else:
                print(f"❌ Agents List: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ Agents List: ERROR - {e}")
        
        print()
        
        # Test 3: Health Endpoint
        try:
            response = await client.get(f"{base_url}/api/v1/health/")
            if response.status_code == 200:
                health = response.json()
                print("✅ System Health: SUCCESS")
                print(f"   - Status: {health.get('status', 'unknown')}")
                print(f"   - Health Score: {health.get('system_health_score', 0):.1%}")
            else:
                print(f"❌ System Health: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ System Health: ERROR - {e}")
        
        print()
        
        # Test 4: API Documentation
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ API Documentation: Available at http://localhost:8000/docs")
            else:
                print(f"❌ API Documentation: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ API Documentation: ERROR - {e}")
        
        print()
        print("🎉 API Test Complete!")
        print("📖 View full API docs at: http://localhost:8000/docs")
        print("🔧 Ready to register agents!")
        
        return True

if __name__ == "__main__":
    asyncio.run(test_api())