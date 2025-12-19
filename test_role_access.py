#!/usr/bin/env python3
"""
Test script to verify role-based access control
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_login_and_access():
    """Test login and access to protected modules"""
    
    print("🧪 Testing Role-Based Access Control")
    print("=" * 50)
    
    # Test 1: Super Admin Login (bizpulse.erp@gmail.com)
    print("\n1️⃣ Testing Super Admin Login...")
    
    session = requests.Session()
    login_data = {
        "loginId": "bizpulse.erp@gmail.com",
        "password": "demo123"
    }
    
    response = session.post(f"{BASE_URL}/api/auth/unified-login", json=login_data)
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Super Admin Login Success: {user_data['user']['name']}")
        print(f"   Is Super Admin: {user_data['user'].get('is_super_admin', False)}")
        
        # Test access to protected modules
        print("\n   Testing access to protected modules...")
        
        # Test WhatsApp Reports page
        whatsapp_response = session.get(f"{BASE_URL}/whatsapp-sender")
        if whatsapp_response.status_code == 200:
            print("   ✅ WhatsApp Reports: ACCESSIBLE")
        else:
            print(f"   ❌ WhatsApp Reports: BLOCKED ({whatsapp_response.status_code})")
        
        # Test Client Management page
        client_response = session.get(f"{BASE_URL}/client-management")
        if client_response.status_code == 200:
            print("   ✅ Client Management: ACCESSIBLE")
        else:
            print(f"   ❌ Client Management: BLOCKED ({client_response.status_code})")
            
    else:
        print(f"❌ Super Admin Login Failed: {response.status_code}")
    
    # Test 2: Regular Client Login (if any exists)
    print("\n2️⃣ Testing Regular Client Access...")
    
    # First create a test client
    client_data = {
        "company_name": "Test Company",
        "contact_email": "test@company.com",
        "username": "testuser123",
        "password": "testpass123"
    }
    
    create_response = session.post(f"{BASE_URL}/api/clients", json=client_data)
    if create_response.status_code == 200:
        print("✅ Test client created successfully")
        
        # Now try to login as client
        client_session = requests.Session()
        client_login_data = {
            "loginId": "testuser123",
            "password": "testpass123"
        }
        
        client_login_response = client_session.post(f"{BASE_URL}/api/auth/unified-login", json=client_login_data)
        if client_login_response.status_code == 200:
            client_user_data = client_login_response.json()
            print(f"✅ Client Login Success: {client_user_data['user']['name']}")
            print(f"   Is Super Admin: {client_user_data['user'].get('is_super_admin', False)}")
            
            # Test access to protected modules (should be blocked)
            print("\n   Testing access to protected modules...")
            
            # Test WhatsApp Reports page
            whatsapp_response = client_session.get(f"{BASE_URL}/whatsapp-sender")
            if whatsapp_response.status_code == 403:
                print("   ✅ WhatsApp Reports: PROPERLY BLOCKED")
            else:
                print(f"   ❌ WhatsApp Reports: SHOULD BE BLOCKED ({whatsapp_response.status_code})")
            
            # Test Client Management page
            client_response = client_session.get(f"{BASE_URL}/client-management")
            if client_response.status_code == 403:
                print("   ✅ Client Management: PROPERLY BLOCKED")
            else:
                print(f"   ❌ Client Management: SHOULD BE BLOCKED ({client_response.status_code})")
                
        else:
            print(f"❌ Client Login Failed: {client_login_response.status_code}")
    else:
        print(f"❌ Could not create test client: {create_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 Role-Based Access Control Test Complete!")

if __name__ == "__main__":
    test_login_and_access()