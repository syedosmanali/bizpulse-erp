#!/usr/bin/env python3
"""
Quick test to diagnose mobile dashboard loading issue
"""

import requests
import json

def test_mobile_dashboard_apis():
    """Test the APIs that mobile dashboard calls"""
    
    base_url = "http://localhost:5000"  # Adjust if different
    
    print("🔍 Testing Mobile Dashboard APIs...")
    print("=" * 50)
    
    # Test APIs that mobile dashboard calls
    endpoints = [
        "/api/products",
        "/api/customers", 
        "/api/sales/summary"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Success: {len(data)} items returned")
                else:
                    print(f"   ✅ Success: {type(data)} returned")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Server not running on {base_url}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Diagnosis:")
    print("If all APIs return 200 OK, the issue is in the mobile app JavaScript")
    print("If APIs fail, the issue is in the Flask server")
    print("\n💡 Common fixes:")
    print("1. Make sure server is running: python app.py")
    print("2. Check if mobile and server are on same network")
    print("3. Check browser console for JavaScript errors")

if __name__ == "__main__":
    test_mobile_dashboard_apis()