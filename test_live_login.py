"""
Test live login API on deployed Render app
"""

import requests
import json

# Render URL
BASE_URL = "https://bizpulse-erp-1.onrender.com"

def test_login():
    print("🧪 Testing login API on live server...")
    print("=" * 60)
    
    # Login credentials
    login_data = {
        "loginId": "bizpulse.erp@gmail.com",
        "password": "admin123"
    }
    
    try:
        # Make login request
        response = requests.post(
            f"{BASE_URL}/api/auth/unified-login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ LOGIN SUCCESS!")
            print("🎉 App is working perfectly!")
        else:
            print("\n❌ LOGIN FAILED!")
            print("Error:", response.json().get('message'))
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Server might be starting up")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
