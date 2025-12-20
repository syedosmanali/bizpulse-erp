#!/usr/bin/env python3
"""
Test the retail billing fix using /api/bills endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_retail_billing_fix():
    """Test retail billing with /api/bills endpoint"""
    
    print("🧪 Testing Retail Billing Fix with /api/bills")
    print("=" * 50)
    
    # Test data matching mobile ERP format
    test_data = {
        "customer_id": None,
        "business_type": "retail",
        "subtotal": 100.0,
        "tax_amount": 18.0,
        "total_amount": 118.0,
        "payment_method": "cash",
        "items": [
            {
                "product_id": "test-product-1",
                "product_name": "Test Product",
                "quantity": 1,
                "unit_price": 100.0,
                "total_price": 100.0
            }
        ]
    }
    
    try:
        with app.test_client() as client:
            print("📤 Sending POST request to /api/bills")
            print(f"Data: {json.dumps(test_data, indent=2)}")
            
            response = client.post(
                '/api/bills',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.get_json()
                print("✅ SUCCESS! Bill created successfully!")
                print(f"📋 Bill ID: {result.get('bill_id')}")
                print(f"📋 Bill Number: {result.get('bill_number')}")
                print(f"✅ Message: {result.get('message')}")
                return True
            else:
                print("❌ FAILED! Bill creation failed!")
                try:
                    error_data = response.get_json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Raw response: {response.get_data(as_text=True)}")
                return False
                
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_items():
    """Test with multiple items"""
    
    print("\n🧪 Testing Multiple Items Bill")
    print("=" * 30)
    
    test_data = {
        "customer_id": None,
        "business_type": "retail", 
        "subtotal": 300.0,
        "tax_amount": 54.0,
        "total_amount": 354.0,
        "payment_method": "upi",
        "items": [
            {
                "product_id": "test-product-1",
                "product_name": "Product 1",
                "quantity": 2,
                "unit_price": 100.0,
                "total_price": 200.0
            },
            {
                "product_id": "test-product-2", 
                "product_name": "Product 2",
                "quantity": 1,
                "unit_price": 100.0,
                "total_price": 100.0
            }
        ]
    }
    
    try:
        with app.test_client() as client:
            response = client.post(
                '/api/bills',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            if response.status_code == 201:
                result = response.get_json()
                print("✅ Multiple items bill created!")
                print(f"📋 Bill Number: {result.get('bill_number')}")
                return True
            else:
                print("❌ Multiple items bill failed!")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Retail Billing Fix")
    print("=" * 60)
    
    success1 = test_retail_billing_fix()
    success2 = test_multiple_items()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! Retail billing is working with /api/bills!")
    else:
        print("\n💥 Some tests failed!")