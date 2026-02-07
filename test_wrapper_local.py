"""
Test the wrapper locally with the exact INSERT statement from products service
"""
from modules.shared.database import get_db_connection
from datetime import datetime

def test_product_insert():
    """Test product INSERT with is_active = 1"""
    
    conn = get_db_connection()
    
    try:
        # Exact INSERT from products service
        conn.execute("""INSERT INTO products (
                id, code, name, category, price, cost, stock, min_stock, 
                unit, business_type, barcode_data, barcode_image, image_url, expiry_date, 
                supplier, description, bill_receipt_photo, last_stock_update, is_active, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            'test-product-123',
            'TEST001',
            'Test Product',
            'Test Category',
            99.99,
            50.00,
            100,
            10,
            'piece',
            'retail',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            datetime.now().isoformat(),
            1,  # is_active - should be converted to True
            'test-user-id'
        ))
        
        conn.commit()
        print("✅ Product INSERT successful!")
        
        # Verify
        result = conn.execute("SELECT * FROM products WHERE id = ?", ('test-product-123',)).fetchone()
        if result:
            print(f"   Product: {result['name']}")
            print(f"   is_active: {result['is_active']} (type: {type(result['is_active'])})")
        
        # Cleanup
        conn.execute("DELETE FROM products WHERE id = ?", ('test-product-123',))
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_product_insert()
