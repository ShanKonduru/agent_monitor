"""
Simple test to check if our monitoring system is working
"""
import subprocess
import sys
import json

# Test system status endpoint
try:
    result = subprocess.run([
        sys.executable, "-c", 
        """
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8000/api/v1/system/status")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("API Response:")
                print(f"  - Status: healthy")
                print(f"  - Total Agents: {data.get('total_agents', 0)}")
                print(f"  - Active Agents: {data.get('active_agents', 0)}")
                print("✅ Agent Monitor Framework is working!")
            else:
                print(f"❌ Server returned {response.status_code}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

asyncio.run(test())
        """
    ], capture_output=True, text=True, timeout=10)
    
    print("API Test Results:")
    print("=" * 40)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
        
except Exception as e:
    print(f"Test failed: {e}")

print("\n🔧 If the API is working, let's start an example agent!")