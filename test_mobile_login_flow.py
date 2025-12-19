#!/usr/bin/env python3
"""
Test mobile login flow to debug issues
"""

import requests
import json

def test_mobile_login_flow():
    """Test the complete mobile login flow"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Mobile Login Flow...")
    print("=" * 50)
    
    # Test 1: Check if mobile login page loads
    try:
        print("\n1. Testing mobile login page...")
        response = requests.get(f"{base_url}/mobile-simple", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Mobile login page loads successfully")
        else:
            print(f"   ❌ Mobile login page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error loading mobile login page: {e}")
    
    # Test 2: Test login API
    try:
        print("\n2. Testing login API...")
        login_data = {
            "loginId": "demo",
            "password": "demo123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/unified-login",
            json=login_data,
            timeout=5
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login API works successfully")
            print(f"   User: {data.get('user', {}).get('name', 'Unknown')}")
            
            # Get session cookies
            session_cookies = response.cookies
            
            # Test 3: Check if mobile dashboard loads after login
            print("\n3. Testing mobile dashboard access...")
            dashboard_response = requests.get(
                f"{base_url}/mobile-dashboard",
                cookies=session_cookies,
                timeout=5
            )
            
            print(f"   Status: {dashboard_response.status_code}")
            if dashboard_response.status_code == 200:
                print("   ✅ Mobile dashboard loads successfully after login")
            elif dashboard_response.status_code == 302:
                print("   🔄 Redirected (probably to login) - session issue")
            else:
                print(f"   ❌ Mobile dashboard failed: {dashboard_response.status_code}")
                
        else:
            print(f"   ❌ Login API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error testing login API: {e}")
    
    # Test 4: Check mobile dashboard API
    try:
        print("\n4. Testing mobile dashboard API...")
        response = requests.get(f"{base_url}/api/mobile/dashboard", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Mobile dashboard API works")
            print(f"   Products: {data.get('products_count', 0)}")
            print(f"   Customers: {data.get('customers_count', 0)}")
        else:
            print(f"   ❌ Mobile dashboard API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing dashboard API: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Diagnosis:")
    print("If all tests pass, the issue might be in browser JavaScript")
    print("If login API fails, check server logs")
    print("If dashboard access fails, check authentication")
    
    print("\n💡 Quick fixes to try:")
    print("1. Clear browser cache and cookies")
    print("2. Check browser console for JavaScript errors")
    print("3. Make sure server is running: python app.py")
    print("4. Try incognito/private browsing mode")

if __name__ == "__main__":
    test_mobile_login_flow()