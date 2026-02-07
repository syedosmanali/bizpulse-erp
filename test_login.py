"""
Test login logic
"""

import psycopg2
import hashlib

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_login(username, password):
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    try:
        # Get user
        cursor.execute("""
            SELECT id, company_name, contact_email, username, password_hash, is_active 
            FROM clients 
            WHERE username = %s OR contact_email = %s
        """, (username, username))
        
        user = cursor.fetchone()
        
        if not user:
            print("❌ User not found")
            return
        
        user_id, company_name, email, db_username, password_hash, is_active = user
        
        print(f"✅ User found:")
        print(f"   ID: {user_id}")
        print(f"   Username: {db_username}")
        print(f"   Email: {email}")
        print(f"   Active: {is_active}")
        
        # Check password
        input_hash = hash_password(password)
        
        print(f"\n🔐 Password check:")
        print(f"   Input hash: {input_hash[:20]}...")
        print(f"   DB hash: {password_hash[:20]}...")
        
        if input_hash == password_hash:
            print("   ✅ Password MATCH!")
        else:
            print("   ❌ Password MISMATCH!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_login("tasleem", "admin123")
