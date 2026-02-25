#!/usr/bin/env python3
"""
Test script to verify ERP routes are working
"""

import requests
import sys

def test_route(url, description):
    """Test a route and return status"""
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ {description}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False

def main():
    base_url = "http://localhost:5000"
    
    print("🚀 Testing ERP Routes\n")
    
    routes = [
        ("/erp/pos-billing", "POS Billing"),
        ("/erp/products", "Product Master"),
        ("/erp/customers", "Customers"),
        ("/retail/dashboard", "Retail Dashboard"),
        ("/", "Home Page")
    ]
    
    results = []
    for route, description in routes:
        url = base_url + route
        success = test_route(url, description)
        results.append((description, success))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All routes are working correctly!")
    else:
        print("⚠️  Some routes have issues")
        sys.exit(1)

if __name__ == "__main__":
    main()