#!/usr/bin/env python3
"""
Reset Ajay's password to something simple
"""
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reset_ajay_password():
    print("🔄 Resetting Ajay's Password...")
    
    try:
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        # Set a simple password
        new_password = "ajay123"
        password_hash = hash_password(new_password)
        
        # Update Ajay's password
        result = conn.execute('''
            UPDATE client_users SET 
                password_hash = ?,
                password_plain = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE full_name = 'ajay'
        ''', (password_hash, new_password))
        
        if result.rowcount > 0:
            conn.commit()
            print(f"✅ Password reset successfully!")
            print(f"🔑 New credentials for Ajay:")
            print(f"   Username: ajay711 (or ajay@gmail.com)")
            print(f"   Password: {new_password}")
            
            # Verify the update
            user = conn.execute('''
                SELECT full_name, password_plain, password_hash FROM client_users WHERE full_name = 'ajay'
            ''').fetchone()
            
            print(f"\n✅ Verification:")
            print(f"   Name: {user['full_name']}")
            print(f"   Plain Password: {user['password_plain']}")
            print(f"   Hash: {user['password_hash']}")
            print(f"   Hash Match: {hash_password(new_password) == user['password_hash']}")
            
        else:
            print("❌ No user updated")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_ajay_password()