#!/usr/bin/env python3
"""
Test script to diagnose and fix POS billing issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import get_db_connection
from modules.billing.service import BillingService
import json

def test_database_connection():
    """Test database connection and required tables"""
    print("=== Testing Database Connection ===")
    try:
        conn = get_db_connection()
        print("✅ Database connection successful")
        
        # Check required tables
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('bills', 'bill_items', 'products', 'customers')
        """).fetchall()
        
        table_names = [t[0] for t in tables]
        print(f"✅ Found tables: {table_names}")
        
        # Check if required tables exist
        required_tables = ['bills', 'bill_items', 'products']
        missing_tables = [t for t in required_tables if t not in table_names]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All required tables present")
            
        # Check sample data
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"📊 Products in database: {product_count}")
        
        if product_count == 0:
            print("⚠️  No products found - adding sample data")
            # Add sample product
            conn.execute("""
                INSERT INTO products (id, name, price, stock, category, is_active, created_at)
                VALUES ('prod_001', 'Test Product', 100.0, 50, 'Test', 1, datetime('now'))
            """)
            conn.commit()
            print("✅ Added sample product")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_billing_service():
    """Test billing service functionality"""
    print("\n=== Testing Billing Service ===")
    try:
        billing_service = BillingService()
        print("✅ Billing service initialized")
        
        # Test data
        test_data = {
            "items": [
                {
                    "product_id": "prod_001",
                    "product_name": "Test Product",
                    "quantity": 2,
                    "unit_price": 100.0,
                    "total_price": 200.0
                }
            ],
            "subtotal": 200.0,
            "tax_amount": 36.0,  # 18% GST
            "discount_amount": 0.0,
            "total_amount": 236.0,
            "gst_rate": 18,
            "payment_method": "cash",
            "customer_name": "Walk-in Customer"
        }
        
        print("📝 Test data:", json.dumps(test_data, indent=2))
        
        # Test bill creation
        result = billing_service.create_bill(test_data)
        print(f"📝 Bill creation result: {result}")
        
        if result['success']:
            print("✅ Bill created successfully!")
            print(f"   Bill ID: {result.get('bill_id')}")
            print(f"   Bill Number: {result.get('bill_number')}")
            return True
        else:
            print(f"❌ Bill creation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Billing service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting POS Billing Diagnostics\n")
    
    # Test 1: Database connection
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n❌ Database issues found. Cannot proceed with billing tests.")
        return
    
    # Test 2: Billing service
    billing_ok = test_billing_service()
    
    print("\n" + "="*50)
    if db_ok and billing_ok:
        print("🎉 ALL TESTS PASSED! POS Billing should work correctly.")
        print("\n✅ Database: Connected and ready")
        print("✅ Billing Service: Working properly")
        print("✅ Sample Bill: Created successfully")
        print("\n💡 Next steps:")
        print("   1. Update POS frontend to call real API endpoints")
        print("   2. Ensure products are properly loaded in frontend")
        print("   3. Test end-to-end billing flow")
    else:
        print("❌ Some tests failed. Check the errors above.")
        if not billing_ok:
            print("\n🔧 Common fixes:")
            print("   - Check database schema")
            print("   - Verify table relationships")
            print("   - Ensure proper data types")

if __name__ == "__main__":
    main()