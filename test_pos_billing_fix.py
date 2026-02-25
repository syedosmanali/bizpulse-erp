#!/usr/bin/env python3
"""
Test script to diagnose and fix POS billing issues with PostgreSQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import get_db_connection, get_db_type
from modules.billing.service import BillingService
import json

def test_database_connection():
    """Test database connection and required tables"""
    print("=== Testing Database Connection ===")
    try:
        conn = get_db_connection()
        db_type = get_db_type()
        print(f"✅ Database connection successful ({db_type.upper()})")
        
        # Check required tables using PostgreSQL syntax
        if db_type == 'postgresql':
            tables_query = """
                SELECT tablename FROM pg_tables 
                WHERE tablename IN ('bills', 'bill_items', 'products', 'customers')
                AND schemaname = 'public'
            """
        else:
            tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('bills', 'bill_items', 'products', 'customers')
            """
        
        tables = conn.execute(tables_query).fetchall()
        
        if db_type == 'postgresql':
            table_names = [t['tablename'] for t in tables]
        else:
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
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()
        count = product_count['count'] if db_type == 'postgresql' else product_count[0]
        print(f"📊 Products in database: {count}")
        
        if count == 0:
            print("⚠️  No products found - adding sample data")
            # Add sample product
            if db_type == 'postgresql':
                conn.execute("""
                    INSERT INTO products (id, name, price, stock, category, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, ('prod_001', 'Test Product', 100.0, 50, 'Test', True))
            else:
                conn.execute("""
                    INSERT INTO products (id, name, price, stock, category, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, ('prod_001', 'Test Product', 100.0, 50, 'Test', 1))
            conn.commit()
            print("✅ Added sample product")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_billing_service():
    """Test billing service functionality"""
    print("\n=== Testing Billing Service ===")
    try:
        billing_service = BillingService()
        print("✅ Billing service initialized")
        
        # Get real product data
        conn = get_db_connection()
        db_type = get_db_type()
        if db_type == 'postgresql':
            product = conn.execute("SELECT id, name, price FROM products WHERE is_active = TRUE LIMIT 1").fetchone()
        else:
            product = conn.execute("SELECT id, name, price FROM products WHERE is_active = 1 LIMIT 1").fetchone()
        conn.close()
        
        if not product:
            print("❌ No active products found in database")
            return False
            
        product_dict = dict(product) if db_type == 'postgresql' else dict(product)
        product_id = product_dict['id']
        product_name = product_dict['name']
        unit_price = float(product_dict['price'])
        quantity = 2
        total_price = unit_price * quantity
        
        print(f"📝 Using real product: {product_name} (ID: {product_id})")
        
        # Test data with real product
        test_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                }
            ],
            "subtotal": total_price,
            "tax_amount": total_price * 0.18,  # 18% GST
            "discount_amount": 0.0,
            "total_amount": total_price * 1.18,
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

def test_pos_frontend_data():
    """Test if POS frontend can fetch products"""
    print("\n=== Testing POS Frontend Data ===")
    try:
        conn = get_db_connection()
        db_type = get_db_type()
        
        # Fetch products for frontend
        if db_type == 'postgresql':
            products = conn.execute("""
                SELECT id, name, price, stock, category 
                FROM products 
                WHERE is_active = TRUE 
                ORDER BY name
            """).fetchall()
        else:
            products = conn.execute("""
                SELECT id, name, price, stock, category 
                FROM products 
                WHERE is_active = 1 
                ORDER BY name
            """).fetchall()
        
        print(f"📊 Products available for POS: {len(products)}")
        for product in products[:5]:  # Show first 5
            prod_dict = dict(product) if db_type == 'postgresql' else dict(product)
            print(f"   - {prod_dict['name']}: ₹{prod_dict['price']} (Stock: {prod_dict['stock']})")
        
        conn.close()
        return len(products) > 0
        
    except Exception as e:
        print(f"❌ POS data test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting POS Billing Diagnostics (PostgreSQL)\n")
    
    # Test 1: Database connection
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n❌ Database issues found. Cannot proceed with billing tests.")
        return
    
    # Test 2: POS frontend data
    pos_data_ok = test_pos_frontend_data()
    
    # Test 3: Billing service
    billing_ok = test_billing_service()
    
    print("\n" + "="*50)
    if db_ok and billing_ok and pos_data_ok:
        print("🎉 ALL TESTS PASSED! POS Billing should work correctly.")
        print("\n✅ Database: Connected and ready")
        print("✅ Products: Available for POS")
        print("✅ Billing Service: Working properly")
        print("✅ Sample Bill: Created successfully")
        print("\n💡 Next steps:")
        print("   1. Update POS frontend to call real API endpoints")
        print("   2. Ensure frontend is fetching real products")
        print("   3. Test end-to-end billing flow")
    else:
        print("❌ Some tests failed. Check the errors above.")
        if not pos_data_ok:
            print("\n🔧 Fix POS data issues:")
            print("   - Check if products table has data")
            print("   - Verify is_active column values")
        if not billing_ok:
            print("\n🔧 Fix billing service issues:")
            print("   - Check database schema")
            print("   - Verify table relationships")
            print("   - Ensure proper data types")

if __name__ == "__main__":
    main()