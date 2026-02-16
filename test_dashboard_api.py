import requests
import json

def test_dashboard_api():
    """Test the dashboard API endpoint"""
    print("=== TESTING DASHBOARD API ===")
    
    try:
        response = requests.get('http://localhost:5000/api/dashboard/stats', timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_dashboard_api()