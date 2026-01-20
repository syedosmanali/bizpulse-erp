"""
Test permissions API endpoint
"""

import requests
import json

# Test the permissions endpoint
url = "http://localhost:5000/api/user-management/permissions"

try:
    print("🧪 Testing permissions API endpoint...")
    print(f"URL: {url}")
    
    # Make request
    response = requests.get(url, timeout=5)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"\n✅ Response Data:")
        print(json.dumps(data, indent=2))
    except:
        print(f"\n❌ Response Text:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server. Is it running?")
except Exception as e:
    print(f"❌ Error: {e}")
