"""
Docker Container Integration Test for Phase 6.1
Tests AI providers within Docker environment
"""

import time
import requests
import docker
import subprocess

def check_docker_status():
    """Check Docker container status"""
    print("🐳 Checking Docker Container Status...")
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        # Check for monitor container
        if 'agent_monitor-monitor-1' in result.stdout:
            if 'Up' in result.stdout:
                print("✅ Monitor container is running")
                return True
            else:
                print("⚠️  Monitor container exists but may be restarting")
                return False
        else:
            print("❌ Monitor container not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Docker status: {e}")
        return False

def check_container_logs():
    """Check container logs for AI provider initialization"""
    print("\n📋 Checking Container Logs...")
    
    try:
        result = subprocess.run(['docker', 'logs', 'agent_monitor-monitor-1', '--tail', '20'], 
                              capture_output=True, text=True)
        
        logs = result.stdout
        if "AI Provider Manager initialized" in logs:
            print("✅ AI Provider Manager initialized in container")
            return True
        elif "AI Providers router included successfully" in logs:
            print("✅ AI Providers router loaded in container")
            return True
        else:
            print("⚠️  AI Provider initialization not found in logs")
            print("Recent logs:")
            print(logs[-500:])  # Show last 500 characters
            return False
            
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints when containers are ready"""
    print("\n🌐 Testing AI Provider API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("⏳ Waiting for API server...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready!")
                break
        except:
            pass
        time.sleep(1)
        print(f"⏳ Waiting... ({i+1}/30)")
    else:
        print("❌ API server not ready after 30 seconds")
        return False
    
    # Test AI provider endpoints
    endpoints = [
        ("/api/v1/ai/providers", "GET", "Provider List"),
        ("/api/v1/ai/health", "GET", "Health Check"),
        ("/api/v1/ai/models", "GET", "Model List"),
        ("/api/v1/ai/stats", "GET", "Statistics"),
        ("/api/v1/ai/config", "GET", "Configuration")
    ]
    
    results = {}
    
    for endpoint, method, description in endpoints:
        print(f"\n🔍 Testing {description}: {method} {endpoint}")
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: SUCCESS")
                data = response.json()
                print(f"📊 Response keys: {list(data.keys())}")
                results[endpoint] = True
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                print(f"Error: {response.text[:200]}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"❌ {description}: {e}")
            results[endpoint] = False
    
    return results

def test_ai_completion_api():
    """Test AI completion through API"""
    print("\n💬 Testing AI Completion API...")
    
    base_url = "http://localhost:8000"
    
    payload = {
        "prompt": "Hello! Please respond with 'Docker API Test Successful'",
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai/complete",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Completion API working!")
            print(f"🤖 Model: {data.get('model', 'Unknown')}")
            print(f"🏢 Provider: {data.get('provider', 'Unknown')}")
            print(f"💬 Response: {data.get('content', '')[:100]}")
            print(f"📊 Tokens: {data.get('tokens_used', 0)}")
            print(f"⚡ Latency: {data.get('latency_ms', 0)}ms")
            return True
        else:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return False

def main():
    """Run comprehensive Docker integration test"""
    print("🚀 DOCKER INTEGRATION TEST FOR PHASE 6.1")
    print("=" * 50)
    
    # Step 1: Check Docker status
    docker_ok = check_docker_status()
    
    if not docker_ok:
        print("\n❌ Docker containers not ready")
        print("💡 Try running: docker-compose up -d")
        return
    
    # Step 2: Check logs
    logs_ok = check_container_logs()
    
    # Step 3: Test API endpoints
    api_results = test_api_endpoints()
    
    if any(api_results.values()):
        # Step 4: Test AI completion
        completion_ok = test_ai_completion_api()
    else:
        completion_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DOCKER INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    print(f"🐳 Docker Status: {'✅' if docker_ok else '❌'}")
    print(f"📋 Logs Check: {'✅' if logs_ok else '⚠️'}")
    
    if api_results:
        working_endpoints = sum(1 for result in api_results.values() if result)
        total_endpoints = len(api_results)
        print(f"🌐 API Endpoints: {working_endpoints}/{total_endpoints} working")
        
        for endpoint, result in api_results.items():
            emoji = "✅" if result else "❌"
            print(f"  {emoji} {endpoint}")
    
    print(f"💬 AI Completion: {'✅' if completion_ok else '❌'}")
    
    if docker_ok and any(api_results.values() if api_results else []):
        print("\n🎉 DOCKER INTEGRATION SUCCESSFUL!")
        print("Phase 6.1 AI Providers working in Docker containers!")
    else:
        print("\n⚠️  DOCKER INTEGRATION NEEDS ATTENTION")
        print("Check container logs and restart if needed")

if __name__ == "__main__":
    main()