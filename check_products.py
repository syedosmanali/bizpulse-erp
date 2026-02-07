"""
Check products in Supabase
"""

import psycopg2

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def check_products():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    try:
        # Check total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        print(f"📊 Total products in Supabase: {total}")
        
        # Check products with user_id
        cursor.execute("SELECT COUNT(*) FROM products WHERE user_id IS NOT NULL")
        with_user = cursor.fetchone()[0]
        print(f"   - With user_id: {with_user}")
        
        # Check products without user_id
        cursor.execute("SELECT COUNT(*) FROM products WHERE user_id IS NULL")
        without_user = cursor.fetchone()[0]
        print(f"   - Without user_id: {without_user}")
        
        # Show sample products
        cursor.execute("SELECT id, name, user_id, is_active FROM products LIMIT 5")
        products = cursor.fetchall()
        
        print("\n📦 Sample products:")
        for p in products:
            print(f"   - {p[1]}: user_id={p[2]}, active={p[3]}")
        
        # Check clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        clients_count = cursor.fetchone()[0]
        print(f"\n👥 Total clients: {clients_count}")
        
        cursor.execute("SELECT id, username, company_name FROM clients LIMIT 5")
        clients = cursor.fetchall()
        print("\n👥 Sample clients:")
        for c in clients:
            print(f"   - {c[1]} ({c[2]}): id={c[0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_products()
