"""Verify Tasleem login credentials in database"""
import os
import hashlib
from modules.shared.database import get_db_connection, get_db_type

def verify_tasleem():
    conn = get_db_connection()
    cursor = conn.cursor()
    db_type = get_db_type()
    
    print(f"Database type: {db_type}")
    
    # Check in clients table
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, company_name, contact_email, username, password_hash, is_active
            FROM clients
            WHERE username = %s OR contact_email = %s
        """, ('tasleem', 'tasleem@gmail.com'))
    else:
        cursor.execute("""
            SELECT id, company_name, contact_email, username, password_hash, is_active
            FROM clients
            WHERE username = ? OR contact_email = ?
        """, ('tasleem', 'tasleem@gmail.com'))
    
    client = cursor.fetchone()
    
    if client:
        if hasattr(client, 'keys'):
            print(f"\n✅ Found in clients table:")
            print(f"   ID: {client['id']}")
            print(f"   Company: {client['company_name']}")
            print(f"   Email: {client['contact_email']}")
            print(f"   Username: {client['username']}")
            print(f"   Active: {client['is_active']}")
            print(f"   Password Hash: {client['password_hash'][:20]}...")
            
            # Verify password
            test_password = 'Tasleem@123'
            expected_hash = hashlib.sha256(test_password.encode()).hexdigest()
            print(f"\n   Expected hash: {expected_hash[:20]}...")
            print(f"   Match: {expected_hash == client['password_hash']}")
        else:
            print(f"\n✅ Found in clients table (tuple):")
            print(f"   Data: {client}")
    else:
        print("\n❌ NOT found in clients table")
    
    # Check in users table
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, email, business_name, password_hash, is_active
            FROM users
            WHERE email = %s
        """, ('tasleem@gmail.com',))
    else:
        cursor.execute("""
            SELECT id, email, business_name, password_hash, is_active
            FROM users
            WHERE email = ?
        """, ('tasleem@gmail.com',))
    
    user = cursor.fetchone()
    
    if user:
        if hasattr(user, 'keys'):
            print(f"\n✅ Found in users table:")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Business: {user['business_name']}")
            print(f"   Active: {user['is_active']}")
            print(f"   Password Hash: {user['password_hash'][:20]}...")
        else:
            print(f"\n✅ Found in users table (tuple):")
            print(f"   Data: {user}")
    else:
        print("\n❌ NOT found in users table")
    
    conn.close()

if __name__ == '__main__':
    verify_tasleem()
