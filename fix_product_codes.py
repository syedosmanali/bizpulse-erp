#!/usr/bin/env python3
"""
Fix product codes to be sequential numbers only
"""

import sqlite3

def fix_product_codes():
    """Update all product codes to sequential numbers"""
    
    try:
        conn = sqlite3.connect('billing.db')
        cursor = conn.cursor()
        
        # Get all active products ordered by creation date
        cursor.execute("""
            SELECT id FROM products 
            WHERE is_active = 1 
            ORDER BY created_at ASC
        """)
        
        products = cursor.fetchall()
        
        # Update each product with sequential number
        for index, (product_id,) in enumerate(products, start=1):
            cursor.execute("""
                UPDATE products 
                SET code = ? 
                WHERE id = ?
            """, (str(index), product_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully updated {len(products)} products with sequential codes (1-{len(products)})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Fixing product codes to sequential numbers...")
    print("=" * 50)
    fix_product_codes()
