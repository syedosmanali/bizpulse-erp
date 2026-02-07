"""
Test client creation with Supabase
"""

import psycopg2
import hashlib
import uuid
from datetime import datetime

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_create_client():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    client_id = str(uuid.uuid4())
    username = f"testuser_{datetime.now().strftime('%H%M%S')}"
    password = "admin123"
    password_hash = hash_password(password)
    
    try:
        print("🧪 Testing client creation...")
        
        # Test with proper boolean values
        cursor.execute('''
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, phone_number,
                whatsapp_number, business_address, business_type, gst_number,
                username, password_hash, password_plain, is_active, city, state, country,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            client_id,
            "Test Company",
            f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "Test User",
            "1234567890",
            "1234567890",
            "Test Address",
            "retail",
            "",
            username,
            password_hash,
            password,
            True,  # Changed from 1 to True
            "Hyderabad",
            "Telangana",
            "India",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Client created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_create_client()
