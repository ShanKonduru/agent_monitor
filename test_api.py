import requests
import json

try:
    # Test the agents API endpoint
    response = requests.get('http://localhost:8001/api/v1/agents')
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"Number of agents returned: {len(agents)}")
        print(f"Agents data: {json.dumps(agents, indent=2)}")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Error making request: {e}")