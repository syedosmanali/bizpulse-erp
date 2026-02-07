"""
Create admin user in Supabase users table
"""

import psycopg2
import hashlib
import uuid

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    # Check users table structure first
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("📋 Users table structure:")
    for col in columns:
        print(f"   - {col[0]}: {col[1]}")
    
    # Create admin user
    user_id = str(uuid.uuid4())
    email = "bizpulse.erp@gmail.com"
    password = "admin123"
    password_hash = hash_password(password)
    
    try:
        # First add is_admin column if not exists
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
        conn.commit()
        
        cursor.execute("""
            INSERT INTO users (
                id, email, password_hash, business_name, business_type, is_active, is_admin
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE 
            SET password_hash = EXCLUDED.password_hash,
                is_admin = TRUE,
                is_active = TRUE
        """, (
            user_id,
            email,
            password_hash,
            "BizPulse ERP",
            "retail",
            True,
            True
        ))
        
        conn.commit()
        print("\n✅ Admin user created/updated successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_admin()
