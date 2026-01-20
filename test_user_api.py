"""
Test User Management API
Quick test to verify API endpoints are working
"""

import requests
import json

def test_api():
    """Test the user management API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing User Management API...")
    print("=" * 40)
    
    # Test 1: Get users
    try:
        print("1. Testing GET /api/user-management/users")
        response = requests.get(f"{base_url}/api/user-management/users", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                users = data.get('users', [])
                print(f"   Users found: {len(users)}")
                for user in users:
                    print(f"     - {user.get('full_name')} ({user.get('username')})")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   HTTP Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 2: Get roles
    try:
        print("2. Testing GET /api/user-management/roles")
        response = requests.get(f"{base_url}/api/user-management/roles", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                roles = data.get('roles', [])
                print(f"   Roles found: {len(roles)}")
                for role in roles:
                    print(f"     - {role.get('display_name')} ({role.get('role_name')})")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   HTTP Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 3: Initialize system
    try:
        print("3. Testing POST /api/user-management/initialize")
        response = requests.post(f"{base_url}/api/user-management/initialize", 
                               headers={'Content-Type': 'application/json'}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   HTTP Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_api()