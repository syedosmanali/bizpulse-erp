"""
Sync newly added products from local SQLite to Supabase
"""

import sqlite3
import psycopg2
from datetime import datetime

SQLITE_DB = 'billing.db'
SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def sync_products():
    print("🔄 Syncing products from local to Supabase...")
    print("=" * 60)
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    pg_cursor = pg_conn.cursor()
    
    try:
        # Get all products from local SQLite
        sqlite_cursor.execute("SELECT * FROM products WHERE is_active = 1")
        local_products = sqlite_cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in sqlite_cursor.description]
        
        print(f"📦 Found {len(local_products)} products in local database")
        
        # Get existing product IDs from Supabase
        pg_cursor.execute("SELECT id FROM products")
        existing_ids = set(row[0] for row in pg_cursor.fetchall())
        
        print(f"📊 {len(existing_ids)} products already in Supabase")
        
        # Sync new products
        new_count = 0
        for product in local_products:
            product_dict = dict(zip(columns, product))
            product_id = product_dict['id']
            
            if product_id not in existing_ids:
                # Insert new product
                placeholders = ', '.join(['%s'] * len(columns))
                cols = ', '.join(columns)
                
                # Convert boolean values
                values = []
                for i, col in enumerate(columns):
                    val = product[i]
                    if col in ['is_active'] and val in [0, 1]:
                        val = bool(val)
                    values.append(val)
                
                insert_query = f"INSERT INTO products ({cols}) VALUES ({placeholders})"
                
                try:
                    pg_cursor.execute(insert_query, values)
                    new_count += 1
                    print(f"   ✅ Added: {product_dict['name']}")
                except Exception as e:
                    print(f"   ⚠️  Skipped {product_dict['name']}: {str(e)[:50]}")
        
        pg_conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Sync completed!")
        print(f"   New products added: {new_count}")
        print(f"   Total in Supabase: {len(existing_ids) + new_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        pg_conn.rollback()
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    sync_products()
