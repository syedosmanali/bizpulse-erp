"""
Create test user in Supabase for login
"""

import psycopg2
import hashlib
import uuid

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_user():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    # Create test client
    client_id = str(uuid.uuid4())
    username = "tasleem"
    password = "admin123"
    password_hash = hash_password(password)
    
    try:
        cursor.execute("""
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, 
                phone_number, username, password_hash, is_active,
                business_type, country
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
            SET password_hash = EXCLUDED.password_hash
        """, (
            client_id,
            "Test Company",
            "tasleem@gmail.com",
            "Tasleem",
            "1234567890",
            username,
            password_hash,
            True,
            "retail",
            "India"
        ))
        
        conn.commit()
        print("✅ Test user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: tasleem@gmail.com")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_test_user()
