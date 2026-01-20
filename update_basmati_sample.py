"""
Update Basmati Rice Premium product with sample data
"""

import sqlite3
from datetime import datetime

def update_basmati_product():
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    # Sample bill receipt image URL (using a sample invoice/receipt image)
    sample_bill_url = "https://images.unsplash.com/photo-1554224311-beee415c201f?w=500"
    
    # Find Basmati Rice Premium product
    cursor.execute("SELECT id, name, code FROM products WHERE name LIKE '%Basmati%Rice%Premium%' LIMIT 1")
    product = cursor.fetchone()
    
    if product:
        product_id = product[0]
        print(f'Found product: {product[1]} (Code: {product[2]})')
        
        # Update with sample data
        cursor.execute("""
            UPDATE products 
            SET supplier = 'Ali Traders',
                description = 'Premium quality Basmati rice, aged for 2 years. Long grain, aromatic, perfect for biryani and pulao.',
                bill_receipt_photo = ?,
                last_stock_update = ?
            WHERE id = ?
        """, (sample_bill_url, datetime.now().isoformat(), product_id))
        
        conn.commit()
        print(f'✅ Updated {product[1]} with sample data')
        print(f'   - Supplier: Ali Traders')
        print(f'   - Description: Added')
        print(f'   - Bill Receipt: {sample_bill_url}')
        print(f'   - Last Stock Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    else:
        print('❌ Basmati Rice Premium product not found')
        print('\nAvailable products:')
        cursor.execute("SELECT name, code FROM products LIMIT 10")
        for row in cursor.fetchall():
            print(f'  - {row[0]} ({row[1]})')
    
    conn.close()

if __name__ == '__main__':
    update_basmati_product()
