"""Test the API endpoint directly"""
import requests
import json

# Test with Tasleem credentials
url = "http://localhost:5000/api/auth/unified-login"

test_cases = [
    {
        "name": "Tasleem with username",
        "data": {
            "loginId": "tasleem",
            "password": "Tasleem@123"
        }
    },
    {
        "name": "Tasleem with email",
        "data": {
            "loginId": "tasleem@gmail.com",
            "password": "Tasleem@123"
        }
    },
    {
        "name": "BizPulse admin",
        "data": {
            "loginId": "bizpulse.erp@gmail.com",
            "password": "BizPulse@2024!"
        }
    }
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {test['name']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            url,
            json=test['data'],
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
