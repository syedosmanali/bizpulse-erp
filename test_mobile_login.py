#!/usr/bin/env python3
"""
Test script to verify mobile ERP login functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_mobile_login():
    """Test the mobile login flow"""
    print("🧪 Testing Mobile ERP Login Flow...")
    
    # Test 1: Check if user-info returns 401 when not logged in
    print("\n1. Testing user-info without login...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/user-info")
        if response.status_code == 401:
            print("✅ Correctly returns 401 when not authenticated")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test login with demo credentials
    print("\n2. Testing login with demo credentials...")
    try:
        login_data = {
            "loginId": "bizpulse.erp@gmail.com",
            "password": "demo123"
        }
        
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/unified-login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("✅ Login successful")
            data = response.json()
            print(f"   User: {data.get('user', {}).get('name')}")
            print(f"   Type: {data.get('user', {}).get('type')}")
            
            # Test 3: Check user-info after login
            print("\n3. Testing user-info after login...")
            user_response = session.get(f"{BASE_URL}/api/auth/user-info")
            if user_response.status_code == 200:
                print("✅ User-info works after login")
                user_data = user_response.json()
                print(f"   User ID: {user_data.get('user_id')}")
                print(f"   User Type: {user_data.get('user_type')}")
            else:
                print(f"❌ User-info failed: {user_response.status_code}")
                print(f"Response: {user_response.text}")
            
            # Test 4: Test API endpoints that dashboard calls
            print("\n4. Testing dashboard API endpoints...")
            
            # Test products endpoint
            products_response = session.get(f"{BASE_URL}/api/products")
            if products_response.status_code == 200:
                products = products_response.json()
                print(f"✅ Products API works: {len(products)} products")
            else:
                print(f"❌ Products API failed: {products_response.status_code}")
            
            # Test customers endpoint
            customers_response = session.get(f"{BASE_URL}/api/customers")
            if customers_response.status_code == 200:
                customers = customers_response.json()
                print(f"✅ Customers API works: {len(customers)} customers")
            else:
                print(f"❌ Customers API failed: {customers_response.status_code}")
            
            # Test sales summary endpoint
            sales_response = session.get(f"{BASE_URL}/api/sales/summary")
            if sales_response.status_code == 200:
                sales = sales_response.json()
                print(f"✅ Sales Summary API works")
                print(f"   Today's sales: {sales.get('today', {}).get('total', 0)}")
            else:
                print(f"❌ Sales Summary API failed: {sales_response.status_code}")
            
            # Test 5: Test logout
            print("\n5. Testing logout...")
            logout_response = session.post(f"{BASE_URL}/api/auth/logout")
            if logout_response.status_code == 200:
                print("✅ Logout successful")
                
                # Verify session is cleared
                user_check = session.get(f"{BASE_URL}/api/auth/user-info")
                if user_check.status_code == 401:
                    print("✅ Session properly cleared after logout")
                else:
                    print(f"❌ Session not cleared: {user_check.status_code}")
            else:
                print(f"❌ Logout failed: {logout_response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_mobile_login()