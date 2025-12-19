#!/usr/bin/env python3
"""
Test login directly by simulating the API call
"""
import sqlite3
import hashlib
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_login_direct():
    print("🧪 Testing Direct Login Simulation...")
    
    # Test credentials
    test_cases = [
        ("ajay711", "ajay123"),  # New correct password
        ("ajay@gmail.com", "ajay123"),  # Correct with email
        ("ajay711", "FQkfices"),  # Wrong password you were trying
        ("ajay711", "PabaP2vd"),  # Old password (should fail now)
    ]
    
    try:
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        for login_id, password in test_cases:
            print(f"\n🔍 Testing: {login_id} / {password}")
            
            # Simulate the unified login query (exact same as in app.py)
            client_user = conn.execute('''
                SELECT cu.id, cu.full_name, cu.email, cu.username, cu.password_hash, cu.is_active, cu.role, cu.client_id,
                       c.company_name
                FROM client_users cu
                JOIN clients c ON cu.client_id = c.id
                WHERE (cu.email = ? OR cu.username = ?) AND cu.is_active = 1 AND c.is_active = 1
            ''', (login_id, login_id)).fetchone()
            
            if client_user:
                print(f"   ✅ User found: {client_user['full_name']}")
                
                # Test password (exact same logic as in app.py)
                if hash_password(password) == client_user['password_hash']:
                    print(f"   🎉 LOGIN SUCCESS!")
                    print(f"   User would be logged in as: {client_user['full_name']}")
                    print(f"   Role: {client_user['role']}")
                    print(f"   Company: {client_user['company_name']}")
                else:
                    print(f"   ❌ Password incorrect")
                    print(f"   Expected hash: {client_user['password_hash']}")
                    print(f"   Got hash: {hash_password(password)}")
            else:
                print(f"   ❌ User not found or inactive")
        
        conn.close()
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   ✅ Correct credentials: ajay711 / ajay123")
        print(f"   ❌ Wrong credentials: ajay711 / FQkfices")
        print(f"   💡 Make sure you're using the NEW password!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_direct()