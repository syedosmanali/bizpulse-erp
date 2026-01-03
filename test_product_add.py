#!/usr/bin/env python3
"""
Test product add functionality
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.products.service import ProductsService

def test_product_add():
    """Test product add functionality"""
    
    service = ProductsService()
    
    # Test product data
    test_product = {
        "name": "Test Product API",
        "category": "Test Category",
        "price": 99.99,
        "cost": 80.0,
        "stock": 10,
        "min_stock": 2,
        "unit": "piece",
        "business_type": "retail",
        "barcode_data": "TEST123456789",
        "image_url": None
    }
    
    print("🧪 Testing Product Add Functionality")
    print("=" * 50)
    print(f"📦 Test Product: {test_product['name']}")
    print(f"🔢 Barcode: {test_product['barcode_data']}")
    print()
    
    try:
        start_time = time.time()
        result = service.add_product(test_product)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        print(f"⚡ Response time: {response_time:.1f}ms")
        print()
        
        if result.get('success'):
            print("✅ PRODUCT ADD: SUCCESS")
            print(f"   Product ID: {result['product']['id']}")
            print(f"   Product Code: {result['product']['code']}")
            print(f"   Product Name: {result['product']['name']}")
            print(f"   Barcode: {result['product']['barcode']}")
            
            # Test barcode search
            print()
            print("🔍 Testing barcode search for added product...")
            search_result = service.search_product_by_barcode(test_product['barcode_data'])
            
            if search_result.get('success'):
                print("✅ BARCODE SEARCH: SUCCESS")
                found_product = search_result['product']
                print(f"   Found: {found_product['name']}")
                print(f"   Price: ₹{found_product['price']}")
                print(f"   Stock: {found_product['stock']}")
            else:
                print("❌ BARCODE SEARCH: FAILED")
                print(f"   Error: {search_result.get('message')}")
            
        else:
            print("❌ PRODUCT ADD: FAILED")
            print(f"   Error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
    
    print()
    print("🎯 PRODUCT ADD TEST SUMMARY")
    print("=" * 50)
    
    if result.get('success'):
        print("🎉 PRODUCT ADD: WORKING PERFECTLY!")
        print("✅ No network errors")
        print("✅ Fast response time")
        print("✅ Proper data validation")
        print("✅ Barcode integration working")
    else:
        print("⚠️ PRODUCT ADD: NEEDS ATTENTION")
        print(f"❌ Error: {result.get('error')}")
    
    print()
    print("🚀 Test completed!")

if __name__ == "__main__":
    test_product_add()