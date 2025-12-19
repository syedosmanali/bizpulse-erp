#!/usr/bin/env python3
"""
Quick test to verify employee permissions system
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_employee_permissions():
    print("🧪 Testing Employee Permissions System...")
    
    # Test 1: Create a test employee (as business owner)
    print("\n1. Testing employee creation...")
    
    # First login as business owner (you'll need to create one first)
    # For now, let's test the permission API directly
    
    # Test 2: Check if staff permissions API works
    print("\n2. Testing staff permissions API...")
    
    try:
        # Test getting permissions for a user
        response = requests.get(f"{BASE_URL}/api/staff-permissions/test-user-id")
        print(f"Staff permissions API status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing API: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_employee_permissions()