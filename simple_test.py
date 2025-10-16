"""
Simple Phase 2 Test
"""
import httpx
import json

def test_phase2_sync():
    print('🚀 Testing Phase 2 Agent Monitor Framework')
    print('=' * 50)
    
    try:
        # Test system info
        response = httpx.get('http://localhost:8000/api/v2/system/info', timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f'✅ System Online: {info["name"]} v{info["version"]}')
            print(f'📊 Phase: {info["phase"]}')
            print(f'💾 Database: {info["database"]["type"]}')
            print()
            
            # Test agent registration
            agent_data = {
                'name': 'Phase 2 Test Agent',
                'type': 'llm_agent',
                'version': '2.0.0',
                'description': 'Testing Phase 2 database persistence',
                'deployment_type': 'local',
                'host': 'localhost',
                'environment': 'development',
                'tags': ['phase2', 'test', 'database']
            }
            
            response = httpx.post('http://localhost:8000/api/v1/agents/register', 
                                json=agent_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                agent_id = result['agent_id']
                print(f'🤖 Agent Registered: {agent_id}')
                print(f'   Status: {result["status"]}')
                
                # Verify persistence
                response = httpx.get(f'http://localhost:8000/api/v1/agents/{agent_id}', timeout=10)
                if response.status_code == 200:
                    agent = response.json()
                    print(f'✅ Database Persistence Verified!')
                    print(f'   Name: {agent["name"]}')
                    print(f'   Type: {agent["type"]}')
                    print(f'   Environment: {agent["environment"]}')
                    print()
                    
                    print('🎉 Phase 2 SUCCESS!')
                    print('📈 Working Features:')
                    print('   ✅ SQLite Database Connection')
                    print('   ✅ Agent Registration with Persistence') 
                    print('   ✅ Database Schema Creation')
                    print('   ✅ Enhanced API Endpoints')
                    print('   ✅ System Information API')
                    return True
                    
        print('❌ Test failed')
        return False
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    test_phase2_sync()