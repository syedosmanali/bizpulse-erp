#!/usr/bin/env python3
"""
Test Ajay's login with correct password
"""
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_ajay_correct_login():
    print("🧪 Testing Ajay's Login with Correct Password...")
    
    try:
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        # Test with correct password
        username = 'ajay711'
        password = 'PabaP2vd'  # Correct password from database
        
        print(f"Testing: {username} / {password}")
        
        # Simulate the unified login query
        client_user = conn.execute('''
            SELECT cu.id, cu.full_name, cu.email, cu.username, cu.password_hash, cu.is_active, cu.role, cu.client_id,
                   c.company_name
            FROM client_users cu
            JOIN clients c ON cu.client_id = c.id
            WHERE (cu.email = ? OR cu.username = ?) AND cu.is_active = 1 AND c.is_active = 1
        ''', (username, username)).fetchone()
        
        if client_user:
            print(f"✅ User found: {client_user['full_name']}")
            
            # Test password hash
            input_hash = hash_password(password)
            stored_hash = client_user['password_hash']
            
            print(f"Input hash: {input_hash}")
            print(f"Stored hash: {stored_hash}")
            print(f"Hash match: {input_hash == stored_hash}")
            
            if input_hash == stored_hash:
                print("🎉 LOGIN SHOULD WORK!")
                print(f"✅ Use these credentials:")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
            else:
                print("❌ Password hash mismatch")
        else:
            print("❌ User not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ajay_correct_login()