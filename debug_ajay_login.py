#!/usr/bin/env python3
"""
Debug script to check Ajay's login credentials
"""
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def debug_ajay_login():
    print("🔍 Debugging Ajay's Login Issue...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        # Check if Ajay exists in client_users table
        print("\n1. Checking client_users table for Ajay...")
        users = conn.execute('''
            SELECT cu.id, cu.full_name, cu.email, cu.username, cu.password_hash, cu.password_plain, 
                   cu.is_active, cu.role, cu.client_id, c.company_name
            FROM client_users cu
            LEFT JOIN clients c ON cu.client_id = c.id
            WHERE cu.full_name LIKE '%ajay%' OR cu.username LIKE '%ajay%' OR cu.email LIKE '%ajay%'
        ''').fetchall()
        
        if users:
            for user in users:
                print(f"✅ Found user:")
                print(f"   ID: {user['id']}")
                print(f"   Name: {user['full_name']}")
                print(f"   Email: {user['email']}")
                print(f"   Username: {user['username']}")
                print(f"   Password Hash: {user['password_hash']}")
                print(f"   Password Plain: {user['password_plain']}")
                print(f"   Active: {user['is_active']}")
                print(f"   Role: {user['role']}")
                print(f"   Client ID: {user['client_id']}")
                print(f"   Company: {user['company_name']}")
                
                # Test password hashing
                if user['password_plain']:
                    expected_hash = hash_password(user['password_plain'])
                    print(f"   Expected Hash: {expected_hash}")
                    print(f"   Hash Match: {expected_hash == user['password_hash']}")
                
                print("-" * 50)
        else:
            print("❌ No user found with 'ajay' in name, username, or email")
        
        # Check clients table to make sure client is active
        print("\n2. Checking clients table...")
        clients = conn.execute('SELECT id, company_name, is_active FROM clients').fetchall()
        for client in clients:
            print(f"Client: {client['company_name']} (ID: {client['id']}, Active: {client['is_active']})")
        
        # Test login with different variations
        print("\n3. Testing login variations...")
        test_credentials = [
            ('ajay', 'FQkfices'),  # From the screenshot
            ('ajay@gmail.com', 'FQkfices'),
            ('ajay711', 'FQkfices')
        ]
        
        for username, password in test_credentials:
            print(f"\nTesting: {username} / {password}")
            
            # Check if user exists
            user = conn.execute('''
                SELECT cu.id, cu.full_name, cu.password_hash, cu.password_plain, cu.is_active
                FROM client_users cu
                JOIN clients c ON cu.client_id = c.id
                WHERE (cu.email = ? OR cu.username = ?) AND cu.is_active = 1 AND c.is_active = 1
            ''', (username, username)).fetchone()
            
            if user:
                print(f"   ✅ User found: {user['full_name']}")
                print(f"   Stored hash: {user['password_hash']}")
                print(f"   Plain password: {user['password_plain']}")
                
                # Test password
                input_hash = hash_password(password)
                print(f"   Input hash: {input_hash}")
                print(f"   Hash match: {input_hash == user['password_hash']}")
                
                if user['password_plain']:
                    print(f"   Plain match: {password == user['password_plain']}")
            else:
                print(f"   ❌ User not found or inactive")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_ajay_login()