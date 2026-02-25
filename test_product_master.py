#!/usr/bin/env python3
"""
Simple test to verify product master route works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_product_master_route():
    """Test the product master route directly"""
    print("🚀 Testing Product Master Route\n")
    
    try:
        with app.test_client() as client:
            # Test the route
            response = client.get('/erp/products')
            print(f"Status Code: {response.status_code}")
            print(f"Response Type: {response.content_type}")
            
            if response.status_code == 200:
                print("✅ Product Master route is working!")
                print("Content Length:", len(response.data))
                if len(response.data) > 0:
                    print("✅ Page content loaded successfully")
                return True
            else:
                print(f"❌ Route returned error: {response.status_code}")
                print("Response:", response.data.decode('utf-8')[:200] + "..." if len(response.data) > 200 else response.data.decode('utf-8'))
                return False
                
    except Exception as e:
        print(f"❌ Error testing route: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Product Master Route Test")
    print("=" * 40)
    
    success = test_product_master_route()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 TEST PASSED: Product Master route is working correctly!")
    else:
        print("❌ TEST FAILED: Product Master route has issues")
        sys.exit(1)

if __name__ == "__main__":
    main()