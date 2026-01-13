#!/usr/bin/env python3
"""
Add admin flag to users table for flexible admin management
"""

import sqlite3
from modules.shared.database import get_db_connection

def add_admin_flag():
    """Add is_admin column to users table"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("📝 Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            
            # Set existing BizPulse users as admins
            bizpulse_emails = [
                'bizpulse.erp@gmail.com',
                'admin@bizpulse.com', 
                'support@bizpulse.com',
                'developer@bizpulse.com',
                'osman@bizpulse.com'
            ]
            
            for email in bizpulse_emails:
                cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
                print(f"   ✅ Set {email} as admin")
            
            # Also set users with @bizpulse.com domain as admins
            cursor.execute("UPDATE users SET is_admin = 1 WHERE email LIKE '%@bizpulse.com'")
            
            conn.commit()
            print("✅ Admin flag added successfully!")
            
        else:
            print("ℹ️  is_admin column already exists")
        
        # Show current admin users
        cursor.execute("SELECT id, first_name, last_name, email, is_admin FROM users WHERE is_active = 1")
        users = cursor.fetchall()
        
        print("\n📋 Current Users and Admin Status:")
        print("-" * 80)
        for user in users:
            admin_status = "✅ ADMIN" if user[4] else "👤 USER"
            print(f"{admin_status} | {user[1]} {user[2]} | {user[3]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def make_user_admin(email):
    """Make a specific user an admin"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ? AND is_active = 1", (email,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ {email} is now an admin!")
        else:
            print(f"❌ User {email} not found or inactive")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def remove_user_admin(email):
    """Remove admin privileges from a user"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET is_admin = 0 WHERE email = ? AND is_active = 1", (email,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Removed admin privileges from {email}")
        else:
            print(f"❌ User {email} not found or inactive")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'add-flag':
            add_admin_flag()
        elif command == 'make-admin' and len(sys.argv) > 2:
            make_user_admin(sys.argv[2])
        elif command == 'remove-admin' and len(sys.argv) > 2:
            remove_user_admin(sys.argv[2])
        else:
            print("Usage:")
            print("  python add_admin_flag_to_users.py add-flag")
            print("  python add_admin_flag_to_users.py make-admin <email>")
            print("  python add_admin_flag_to_users.py remove-admin <email>")
    else:
        add_admin_flag()