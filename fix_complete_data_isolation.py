"""
Fix Complete Data Isolation - Assign user_ids to all data
Each client should ONLY see their own data
"""

import sqlite3
from datetime import datetime

DB_PATH = 'billing.db'

def fix_data_isolation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("COMPLETE DATA ISOLATION FIX")
    print("=" * 60)
    
    # Get all clients
    cursor.execute('SELECT id, username, company_name FROM clients WHERE is_active = 1')
    clients = cursor.fetchall()
    
    print(f"\n✅ Found {len(clients)} active clients:")
    for client in clients:
        print(f"   - {client[1]} ({client[2]}) - ID: {client[0]}")
    
    # Check current data distribution
    print("\n📊 CURRENT DATA DISTRIBUTION:")
    print("-" * 60)
    
    # Products
    cursor.execute('SELECT user_id, COUNT(*) FROM products WHERE is_active = 1 GROUP BY user_id')
    products_dist = cursor.fetchall()
    print("\n📦 Products:")
    for row in products_dist:
        user_id = row[0] if row[0] else "NULL (shared)"
        print(f"   {user_id}: {row[1]} products")
    
    # Customers
    cursor.execute('SELECT user_id, COUNT(*) FROM customers WHERE is_active = 1 GROUP BY user_id')
    customers_dist = cursor.fetchall()
    print("\n👥 Customers:")
    for row in customers_dist:
        user_id = row[0] if row[0] else "NULL (shared)"
        print(f"   {user_id}: {row[1]} customers")
    
    # Bills
    cursor.execute('SELECT business_owner_id, COUNT(*) FROM bills GROUP BY business_owner_id')
    bills_dist = cursor.fetchall()
    print("\n🧾 Bills:")
    for row in bills_dist:
        user_id = row[0] if row[0] else "NULL (shared)"
        print(f"   {user_id}: {row[1]} bills")
    
    # Now assign data to each client
    print("\n" + "=" * 60)
    print("ASSIGNING DATA TO CLIENTS")
    print("=" * 60)
    
    # For each client, we'll keep their existing data and ensure it's properly assigned
    for client_id, username, company_name in clients:
        print(f"\n🔧 Processing: {username} ({company_name})")
        
        # Update products with NULL user_id to belong to this client
        # But ONLY if they don't already have a user_id
        cursor.execute('''
            UPDATE products 
            SET user_id = ? 
            WHERE user_id IS NULL AND is_active = 1
        ''', (client_id,))
        products_updated = cursor.rowcount
        
        # Update customers with NULL user_id to belong to this client
        cursor.execute('''
            UPDATE customers 
            SET user_id = ? 
            WHERE user_id IS NULL AND is_active = 1
        ''', (client_id,))
        customers_updated = cursor.rowcount
        
        # Update bills with NULL business_owner_id to belong to this client
        cursor.execute('''
            UPDATE bills 
            SET business_owner_id = ? 
            WHERE business_owner_id IS NULL
        ''', (client_id,))
        bills_updated = cursor.rowcount
        
        print(f"   ✅ Updated {products_updated} products")
        print(f"   ✅ Updated {customers_updated} customers")
        print(f"   ✅ Updated {bills_updated} bills")
        
        # Break after first client to assign all NULL data to them
        # Other clients will start fresh
        if products_updated > 0 or customers_updated > 0 or bills_updated > 0:
            print(f"\n   ℹ️  All shared data assigned to {username}")
            break
    
    conn.commit()
    
    # Verify final distribution
    print("\n" + "=" * 60)
    print("FINAL DATA DISTRIBUTION")
    print("=" * 60)
    
    for client_id, username, company_name in clients:
        print(f"\n📊 {username} ({company_name}):")
        
        # Count products
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (client_id,))
        products_count = cursor.fetchone()[0]
        
        # Count customers
        cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id = ? AND is_active = 1', (client_id,))
        customers_count = cursor.fetchone()[0]
        
        # Count bills
        cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', (client_id,))
        bills_count = cursor.fetchone()[0]
        
        print(f"   📦 Products: {products_count}")
        print(f"   👥 Customers: {customers_count}")
        print(f"   🧾 Bills: {bills_count}")
    
    # Check for any remaining NULL data
    print("\n" + "=" * 60)
    print("CHECKING FOR REMAINING SHARED DATA")
    print("=" * 60)
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id IS NULL AND is_active = 1')
    null_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id IS NULL AND is_active = 1')
    null_customers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id IS NULL')
    null_bills = cursor.fetchone()[0]
    
    print(f"\n📦 Products with NULL user_id: {null_products}")
    print(f"👥 Customers with NULL user_id: {null_customers}")
    print(f"🧾 Bills with NULL business_owner_id: {null_bills}")
    
    if null_products == 0 and null_customers == 0 and null_bills == 0:
        print("\n✅ SUCCESS! All data is now properly isolated!")
    else:
        print("\n⚠️  WARNING: Some data still has NULL user_id")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("DATA ISOLATION FIX COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    fix_data_isolation()
