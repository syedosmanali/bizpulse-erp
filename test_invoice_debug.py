#!/usr/bin/env python3
"""
Debug invoice routes with error handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_invoice_debug():
    """Test invoice routes with debug info"""
    
    print("🧪 Testing Invoice Routes with Debug")
    print("=" * 50)
    
    with app.test_client() as client:
        
        # Test 1: Invoice test route
        print("📋 Testing /retail/invoices-test route...")
        response = client.get('/retail/invoices-test')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Invoice test route: Working")
        else:
            print(f"❌ Invoice test route failed: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
        
        # Test 2: Invoice main route with error handling
        print("\n📋 Testing /retail/invoices route with error handling...")
        response = client.get('/retail/invoices')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if "Invoice Template Error" in content:
                print("❌ Template error detected:")
                print(content[:500] + "..." if len(content) > 500 else content)
            else:
                print("✅ Invoice main route: Working")
        else:
            print(f"❌ Invoice main route failed: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
        
        # Test 3: Invoice detail route with error handling
        print("\n📋 Testing /retail/invoice/test-id route with error handling...")
        response = client.get('/retail/invoice/test-id')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if "Invoice Detail Template Error" in content:
                print("❌ Template error detected:")
                print(content[:500] + "..." if len(content) > 500 else content)
            else:
                print("✅ Invoice detail route: Working")
        else:
            print(f"❌ Invoice detail route failed: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_invoice_debug()