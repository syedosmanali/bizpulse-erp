"""
Quick fix for product list display issue
Verifies database and checks for any issues
"""

import sqlite3

def check_products():
    """Check if products exist and are accessible"""
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    print("🔍 Checking Product List...")
    print("=" * 60)
    
    # Check total products
    cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
    total = cursor.fetchone()[0]
    print(f"✅ Total Active Products: {total}")
    
    # Check products by user
    cursor.execute("""
        SELECT user_id, COUNT(*) as count 
        FROM products 
        WHERE is_active = 1 
        GROUP BY user_id
    """)
    
    print("\n📊 Products by User:")
    for row in cursor.fetchall():
        user_id = row[0] or 'NULL'
        count = row[1]
        print(f"  User ID: {user_id} → {count} products")
    
    # Show sample products
    print("\n📦 Sample Products:")
    cursor.execute("""
        SELECT id, code, name, category, price, stock, user_id 
        FROM products 
        WHERE is_active = 1 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  • {row[2]} (Code: {row[1]}, Stock: {row[5]}, User: {row[6] or 'NULL'})")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Database check complete!")
    print("\n💡 If products are not showing:")
    print("  1. Clear browser cache (Ctrl+Shift+Delete)")
    print("  2. Hard refresh page (Ctrl+F5)")
    print("  3. Check browser console (F12) for errors")
    print("  4. Restart Flask app")

if __name__ == '__main__':
    check_products()
