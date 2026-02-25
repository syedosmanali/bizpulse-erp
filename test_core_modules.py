#!/usr/bin/env python3
"""
Test script to verify Core Setup & Control modules
"""
import requests
import sys
from urllib.parse import urljoin

# Base URL - update this to your server URL
BASE_URL = 'http://127.0.0.1:5000'

def test_route(url, expected_status=200):
    """Test a single route"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {url} - OK ({response.status_code})")
            return True
        else:
            print(f"❌ {url} - Failed (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {url} - Error: {str(e)}")
        return False

def test_api_route(url, expected_status=200):
    """Test an API route"""
    try:
        response = requests.post(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {url} - OK ({response.status_code})")
            return True
        else:
            print(f"❌ {url} - Failed (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {url} - Error: {str(e)}")
        return False

def main():
    print("Testing Core Setup & Control Modules...\n")
    
    # Test frontend routes
    frontend_routes = [
        '/erp/company-profile',
        '/erp/gst-details',
        '/erp/invoice-numbering',
        '/erp/financial-year',
        '/erp/invoice-templates',
        '/erp/terms-conditions'
    ]
    
    print("=== Testing Frontend Routes ===")
    frontend_success = 0
    for route in frontend_routes:
        url = urljoin(BASE_URL, route)
        if test_route(url):
            frontend_success += 1
    
    print(f"\nFrontend Routes: {frontend_success}/{len(frontend_routes)} passed")
    
    # Test API routes
    api_routes = [
        '/api/erp/logout'
    ]
    
    print("\n=== Testing API Routes ===")
    api_success = 0
    for route in api_routes:
        url = urljoin(BASE_URL, route)
        if test_api_route(url, 200):  # POST request expected to return 200
            api_success += 1
    
    print(f"\nAPI Routes: {api_success}/{len(api_routes)} passed")
    
    # Overall result
    total_success = frontend_success + api_success
    total_routes = len(frontend_routes) + len(api_routes)
    
    print(f"\n=== Overall Result ===")
    print(f"Total: {total_success}/{total_routes} routes working")
    
    if total_success == total_routes:
        print("🎉 All tests passed! Core Setup & Control modules are ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the server and routes.")
        return 1

if __name__ == '__main__':
    sys.exit(main())