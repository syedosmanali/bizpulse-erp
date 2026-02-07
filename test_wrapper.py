"""
Test wrapper with parameter conversion
"""

import sys
sys.path.insert(0, '.')

from modules.shared.database import get_db_connection, generate_id, hash_password
from datetime import datetime

def test_wrapper():
    print("🧪 Testing wrapper with client creation...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    client_id = generate_id()
    username = f"wrappertest_{datetime.now().strftime('%H%M%S')}"
    password = "admin123"
    password_hash = hash_password(password)
    
    try:
        # This should auto-convert 1 to True
        cursor.execute('''
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, phone_number,
                whatsapp_number, business_address, business_type, gst_number,
                username, password_hash, password_plain, is_active, city, state, country,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            "Wrapper Test Company",
            f"wrapper{datetime.now().strftime('%H%M%S')}@example.com",
            "Wrapper Test",
            "9876543210",
            "9876543210",
            "Wrapper Address",
            "retail",
            "",
            username,
            password_hash,
            password,
            1,  # This should convert to True
            "Mumbai",
            "Maharashtra",
            "India",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Wrapper test SUCCESS!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("   1 was auto-converted to True")
        
    except Exception as e:
        print(f"❌ Wrapper test FAILED: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_wrapper()
