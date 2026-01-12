#!/usr/bin/env python3
"""
Test Stock Update API
====================

This script tests the stock update API endpoint directly.
"""

import requests
import json

def test_stock_update():
    """Test the stock update API"""
    
    print("🧪 TESTING STOCK UPDATE API")
    print("=" * 40)
    
    # Test data
    base_url = "http://localhost:5000"
    
    # First, let's try to get products (this will fail due to auth, but we can see the error)
    print("1. Testing products API (should fail - no auth)...")
    try:
        response = requests.get(f"{base_url}/api/products")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test stock update API directly (should also fail due to auth)
    print("\n2. Testing stock update API (should fail - no auth)...")
    product_id = "52ebdc27-ed31-4669-a8be-7f4d3e040f14"  # Basmati Rice from the list
    new_stock = 30
    
    try:
        response = requests.put(
            f"{base_url}/api/products/{product_id}/stock",
            json={"stock": new_stock},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API TEST COMPLETE")
    print("=" * 40)
    print("📝 NOTES:")
    print("   - Both APIs require authentication")
    print("   - Need to login through web interface first")
    print("   - Then test through browser console")

if __name__ == '__main__':
    test_stock_update()