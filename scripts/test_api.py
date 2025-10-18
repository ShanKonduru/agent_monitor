import requests
import json

def test_api():
    """Test API endpoints"""
    try:
        print('Testing /api/v1/agents...')
        r = requests.get('http://localhost:8000/api/v1/agents')
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            agents = r.json()
            print(f'Found {len(agents)} agents')
            for agent in agents[:3]:
                print(f'  - {agent.get("name", "Unknown")} ({agent.get("status", "Unknown")})')
        else:
            print(f'Error: {r.text}')
    except requests.exceptions.ConnectionError:
        print('Error: Server not running. Start server first with: 004_run.bat server')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_api()