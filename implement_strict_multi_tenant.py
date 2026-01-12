"""
STRICT MULTI-TENANT DATA ISOLATION
Each client gets their OWN copy of data
NO data sharing between clients
"""

import sqlite3
from datetime import datetime

DB_PATH = 'billing.db'

def implement_strict_multi_tenant():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("IMPLEMENTING STRICT MULTI-TENANT DATA ISOLATION")
    print("=" * 80)
    
    # Get all active clients
    cursor.execute('SELECT id, username, company_name FROM clients WHERE is_active = 1')
    clients = cursor.fetchall()
    
    print(f"\n✅ Found {len(clients)} active clients:")
    for client in clients:
        print(f"   - {client[1]} ({client[2]}) - ID: {client[0]}")
    
    # Check current shared data
    print("\n📊 CURRENT SHARED DATA:")
    print("-" * 80)
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id IS NULL AND is_active = 1')
    shared_products = cursor.fetchone()[0]
    print(f"   📦 Shared products (user_id = NULL): {shared_products}")
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id IS NULL AND is_active = 1')
    shared_customers = cursor.fetchone()[0]
    print(f"   👥 Shared customers (user_id = NULL): {shared_customers}")
    
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id IS NULL')
    shared_bills = cursor.fetchone()[0]
    print(f"   🧾 Shared bills (business_owner_id = NULL): {shared_bills}")
    
    if shared_products == 0 and shared_customers == 0 and shared_bills == 0:
        print("\n✅ No shared data found. All data is already isolated.")
        
        # Show current distribution
        print("\n📊 CURRENT DATA DISTRIBUTION:")
        print("-" * 80)
        for client_id, username, company_name in clients:
            cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (client_id,))
            products = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id = ? AND is_active = 1', (client_id,))
            customers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', (client_id,))
            bills = cursor.fetchone()[0]
            
            print(f"\n   {username} ({company_name}):")
            print(f"      📦 Products: {products}")
            print(f"      👥 Customers: {customers}")
            print(f"      🧾 Bills: {bills}")
        
        conn.close()
        return
    
    # STRATEGY: Give each client their OWN COPY of shared products
    print("\n" + "=" * 80)
    print("CREATING SEPARATE DATA COPIES FOR EACH CLIENT")
    print("=" * 80)
    
    # Get all shared products
    cursor.execute('SELECT * FROM products WHERE user_id IS NULL AND is_active = 1')
    shared_products_list = cursor.fetchall()
    
    print(f"\n📦 Found {len(shared_products_list)} shared products to duplicate")
    
    # For each client, create their own copy of products
    for client_id, username, company_name in clients:
        print(f"\n🔧 Creating data for: {username} ({company_name})")
        
        # Check if client already has products
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (client_id,))
        existing_products = cursor.fetchone()[0]
        
        if existing_products > 0:
            print(f"   ℹ️  Client already has {existing_products} products. Skipping duplication.")
            continue
        
        # Create copies of shared products for this client
        products_created = 0
        for product in shared_products_list:
            # Generate new product ID for this client
            import uuid
            new_product_id = str(uuid.uuid4())
            
            # Insert product copy with client's user_id
            try:
                cursor.execute('''
                    INSERT INTO products (
                        id, code, name, category, price, cost, stock, min_stock, 
                        unit, business_type, is_active, gst_rate, barcode_data, 
                        barcode_image, image_url, user_id, expiry_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_product_id,
                    f"{product[1]}-{client_id[:8]}" if product[1] else f"P{new_product_id[:8]}",  # Unique code per client
                    product[2],  # name
                    product[3],  # category
                    product[4],  # price
                    product[5],  # cost
                    product[6],  # stock
                    product[7],  # min_stock
                    product[8],  # unit
                    product[9],  # business_type
                    product[10],  # is_active
                    product[12],  # gst_rate
                    None,  # barcode_data (clear for new copy)
                    None,  # barcode_image (clear for new copy)
                    product[15] if len(product) > 15 else None,  # image_url
                    client_id,  # user_id - ASSIGN TO THIS CLIENT
                    product[17] if len(product) > 17 else None,  # expiry_date
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                products_created += 1
            except sqlite3.IntegrityError as e:
                print(f"   ⚠️  Skipping duplicate: {product[2]} - {e}")
                continue
        
        print(f"   ✅ Created {products_created} products for {username}")
    
    conn.commit()
    
    # Now delete the shared products (they've been copied to each client)
    print(f"\n🗑️  Deleting {len(shared_products_list)} shared products (now duplicated per client)...")
    cursor.execute('DELETE FROM products WHERE user_id IS NULL')
    deleted_count = cursor.rowcount
    print(f"   ✅ Deleted {deleted_count} shared products")
    
    conn.commit()
    
    # Verify final state
    print("\n" + "=" * 80)
    print("FINAL DATA DISTRIBUTION (STRICT ISOLATION)")
    print("=" * 80)
    
    for client_id, username, company_name in clients:
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (client_id,))
        products = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id = ? AND is_active = 1', (client_id,))
        customers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', (client_id,))
        bills = cursor.fetchone()[0]
        
        print(f"\n   {username} ({company_name}):")
        print(f"      📦 Products: {products}")
        print(f"      👥 Customers: {customers}")
        print(f"      🧾 Bills: {bills}")
    
    # Final verification
    print("\n" + "=" * 80)
    print("VERIFICATION - NO SHARED DATA ALLOWED")
    print("=" * 80)
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id IS NULL AND is_active = 1')
    null_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id IS NULL AND is_active = 1')
    null_customers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id IS NULL')
    null_bills = cursor.fetchone()[0]
    
    print(f"\n   📦 Products with NULL user_id: {null_products}")
    print(f"   👥 Customers with NULL user_id: {null_customers}")
    print(f"   🧾 Bills with NULL business_owner_id: {null_bills}")
    
    if null_products == 0 and null_customers == 0 and null_bills == 0:
        print("\n✅ SUCCESS! STRICT MULTI-TENANT ISOLATION ACHIEVED!")
        print("   - Every product belongs to a specific client")
        print("   - Every customer belongs to a specific client")
        print("   - Every bill belongs to a specific client")
        print("   - NO shared data exists")
    else:
        print("\n⚠️  WARNING: Some shared data still exists!")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("STRICT MULTI-TENANT IMPLEMENTATION COMPLETE!")
    print("=" * 80)

if __name__ == '__main__':
    implement_strict_multi_tenant()
