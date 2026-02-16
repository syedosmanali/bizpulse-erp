import requests
import json

def debug_dashboard_stats():
    """Debug the dashboard stats endpoint"""
    print("=== DEBUGGING DASHBOARD STATS ===\n")
    
    try:
        # Test the endpoint directly
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2, default=str)}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Response: {response.text[:500]}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard_stats()