#!/usr/bin/env python3
"""
Test script to verify client users and staff API endpoints
"""
import requests
import json

# Test client ID (amjad wholesale)
CLIENT_ID = "9e22bd60-2ef8-4c51-a5b2-bee00384d0ef"
BASE_URL = "http://localhost:5000"

def test_client_users():
    """Test getting client users"""
    print("🧪 Testing Client Users API...")
    try:
        response = requests.get(f"{BASE_URL}/api/clients/{CLIENT_ID}/users")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('users', []))} users")
            for user in data.get('users', []):
                print(f"   - {user['full_name']} ({user['username']}) - {user['role']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_client_staff():
    """Test getting client staff"""
    print("\n🧪 Testing Client Staff API...")
    try:
        response = requests.get(f"{BASE_URL}/api/clients/{CLIENT_ID}/staff")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('staff', []))} staff members")
            for staff in data.get('staff', []):
                print(f"   - {staff['name']} ({staff['username']}) - {staff['role']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing Client Users & Staff API Endpoints")
    print("=" * 50)
    
    test_client_users()
    test_client_staff()
    
    print("\n✅ Test completed!")