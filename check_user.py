"""
Check if user exists in Supabase
"""

import psycopg2

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def check_user():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    try:
        # Check clients table
        cursor.execute("SELECT username, contact_email, is_active FROM clients WHERE username = %s", ("tasleem",))
        user = cursor.fetchone()
        
        if user:
            print("✅ User found in Supabase!")
            print(f"   Username: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Active: {user[2]}")
        else:
            print("❌ User NOT found in Supabase")
        
        # Check total clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total clients in Supabase: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_user()
