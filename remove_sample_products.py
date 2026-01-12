"""
Remove ONLY sample products (the 55 duplicated ones)
Keep manually added products
"""

import sqlite3
from datetime import datetime

DB_PATH = 'billing.db'

def remove_sample_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("REMOVING SAMPLE PRODUCTS ONLY")
    print("=" * 80)
    
    # Sample product names that were duplicated
    sample_product_names = [
        'Rice 1kg', 'Dal 500g', 'Oil 1L', 'Sugar 1kg', 'Tea 250g', 'Ata',
        'Rice (1kg)', 'Wheat Flour (1kg)', 'Sugar (1kg)', 'Tea Powder (250g)',
        'Cooking Oil (1L)', 'Milk (1L)', 'Bread', 'Eggs (12 pcs)', 'Onions (1kg)',
        'Potatoes (1kg)', 'Biscuits', 'Namkeen', 'Premium Basmati Rice (with Image)',
        'coco cola', 'Tomatoes (1kg)', 'Garlic (250g)', 'Ginger (250g)',
        'Green Chili (100g)', 'Coriander (bunch)', 'Mint (bunch)', 'Spinach (bunch)',
        'Cabbage (1pc)', 'Cauliflower (1pc)', 'Carrot (1kg)', 'Beans (500g)',
        'Peas (500g)', 'Capsicum (500g)', 'Cucumber (1kg)', 'Bottle Gourd (1kg)',
        'Ridge Gourd (1kg)', 'Bitter Gourd (500g)', 'Pumpkin (1kg)', 'Brinjal (500g)',
        'Okra (500g)', 'Radish (1kg)', 'Beetroot (1kg)', 'Sweet Potato (1kg)',
        'Lemon (250g)', 'Coconut (1pc)', 'Banana (dozen)', 'Apple (1kg)',
        'Orange (1kg)', 'Grapes (500g)', 'Mango (1kg)', 'Papaya (1kg)',
        'Watermelon (1pc)', 'Pineapple (1pc)', 'Pomegranate (1kg)', 'Guava (1kg)'
    ]
    
    # Get all products
    cursor.execute('SELECT id, name, code, user_id, created_at FROM products WHERE is_active = 1')
    all_products = cursor.fetchall()
    
    print(f"\n📦 Total products in database: {len(all_products)}")
    
    # Identify sample products
    sample_products = []
    manual_products = []
    
    for product in all_products:
        product_id, name, code, user_id, created_at = product
        
        # Check if it's a sample product
        is_sample = False
        
        # Method 1: Check if name matches sample names
        if name in sample_product_names:
            is_sample = True
        
        # Method 2: Check if code contains user_id (duplicated products)
        if code and user_id and user_id in code:
            is_sample = True
        
        # Method 3: Check if code starts with common patterns
        if code and (code.startswith('P00') or code.startswith('00') or code.startswith('p00')):
            is_sample = True
        
        if is_sample:
            sample_products.append(product)
        else:
            manual_products.append(product)
    
    print(f"\n🔍 Analysis:")
    print(f"   Sample products (to delete): {len(sample_products)}")
    print(f"   Manual products (to keep): {len(manual_products)}")
    
    if len(manual_products) > 0:
        print(f"\n✅ Manual products that will be KEPT:")
        for product in manual_products[:10]:  # Show first 10
            print(f"   - {product[1]} (Code: {product[2]}, User: {product[3][:20] if product[3] else 'NULL'})")
        if len(manual_products) > 10:
            print(f"   ... and {len(manual_products) - 10} more")
    
    if len(sample_products) > 0:
        print(f"\n🗑️  Sample products that will be DELETED:")
        # Group by user_id
        by_user = {}
        for product in sample_products:
            user_id = product[3] if product[3] else 'NULL'
            if user_id not in by_user:
                by_user[user_id] = []
            by_user[user_id].append(product)
        
        for user_id, products in by_user.items():
            print(f"   User {user_id[:20]}: {len(products)} sample products")
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input(f"Delete {len(sample_products)} sample products? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled. No products deleted.")
        conn.close()
        return
    
    # Delete sample products
    deleted_count = 0
    for product in sample_products:
        product_id = product[0]
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        deleted_count += 1
    
    conn.commit()
    
    print(f"\n✅ Deleted {deleted_count} sample products")
    
    # Verify final state
    cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    remaining = cursor.fetchone()[0]
    
    print(f"✅ Remaining products: {remaining}")
    
    # Show products by user
    print("\n📊 Products by user after cleanup:")
    cursor.execute('SELECT user_id, COUNT(*) FROM products WHERE is_active = 1 GROUP BY user_id')
    for row in cursor.fetchall():
        user_id = row[0][:30] if row[0] else 'NULL'
        count = row[1]
        print(f"   {user_id:30} : {count} products")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("SAMPLE PRODUCTS REMOVAL COMPLETE!")
    print("=" * 80)

if __name__ == '__main__':
    remove_sample_products()
