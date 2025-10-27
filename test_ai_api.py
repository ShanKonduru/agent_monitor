"""
API Testing Script for Phase 6.1 AI Providers
Tests the REST API endpoints directly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all AI provider API endpoints"""
    
    print("🌐 Testing AI Provider API Endpoints")
    print("=" * 40)
    
    # Test 1: Get available providers
    print("\n1️⃣ Testing GET /api/v1/ai/providers")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ai/providers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Providers: {data.get('providers', [])}")
            print(f"🏠 Default: {data.get('default_provider')}")
            print(f"💚 Health: {data.get('health_status', {})}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Get all models
    print("\n2️⃣ Testing GET /api/v1/ai/models")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ai/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', {})
            for provider, model_list in models.items():
                print(f"📦 {provider}: {len(model_list)} models")
                if model_list:
                    print(f"  🤖 Example: {model_list[0].get('name', 'Unknown')}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Health check
    print("\n3️⃣ Testing GET /api/v1/ai/health")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ai/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data.get('health_status', {})}")
            print(f"🕐 Last Check: {data.get('last_check', 'Unknown')}")
            print(f"💚 Healthy: {data.get('healthy_providers', [])}")
            print(f"💔 Unhealthy: {data.get('unhealthy_providers', [])}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 4: Get statistics
    print("\n4️⃣ Testing GET /api/v1/ai/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ai/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            for provider, provider_stats in stats.items():
                print(f"📊 {provider}:")
                print(f"  📈 Requests: {provider_stats.get('requests', 0)}")
                print(f"  ✅ Success Rate: {provider_stats.get('success_rate', 0):.2%}")
                print(f"  ⚡ Avg Latency: {provider_stats.get('avg_latency', 0):.0f}ms")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 5: AI Completion
    print("\n5️⃣ Testing POST /api/v1/ai/complete")
    try:
        payload = {
            "prompt": "Hello! Respond with 'API Test Successful'",
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ai/complete",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Completion successful!")
            print(f"🤖 Model: {data.get('model', 'Unknown')}")
            print(f"🏢 Provider: {data.get('provider', 'Unknown')}")
            print(f"💬 Response: {data.get('content', '')[:100]}")
            print(f"📊 Tokens: {data.get('tokens_used', 0)}")
            print(f"⚡ Latency: {data.get('latency_ms', 0)}ms")
            print(f"💰 Cost: ${data.get('cost', 0):.4f}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_dashboard_access():
    """Test dashboard access"""
    print("\n🌐 Testing Dashboard Access")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")

def wait_for_server():
    """Wait for server to be ready"""
    print("⏳ Waiting for server to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        
        print(f"⏳ Waiting... ({i+1}/30)")
        time.sleep(1)
    
    print("❌ Server not ready after 30 seconds")
    return False

if __name__ == "__main__":
    print("🧪 AI Provider API Test Suite")
    print("Testing Phase 6.1 REST API endpoints\n")
    
    if wait_for_server():
        test_dashboard_access()
        test_api_endpoints()
        print("\n🎉 API TESTING COMPLETED!")
    else:
        print("\n❌ Cannot test - server not accessible")
        print("Make sure containers are running: docker-compose up -d")