#!/usr/bin/env python3
"""
Test script to verify last_login tracking for clients, client_users, and staff
"""
import sqlite3
from datetime import datetime

def test_last_login_tracking():
    """Test last_login tracking in database"""
    print("🧪 Testing Last Login Tracking...")
    print("=" * 50)
    
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    # Test 1: Check if last_login column exists in all tables
    print("\n1. 📋 Checking Database Schema...")
    
    # Check clients table
    cursor.execute("PRAGMA table_info(clients)")
    clients_columns = [col[1] for col in cursor.fetchall()]
    has_clients_last_login = 'last_login' in clients_columns
    print(f"   Clients table has last_login: {'✅' if has_clients_last_login else '❌'}")
    
    # Check client_users table
    cursor.execute("PRAGMA table_info(client_users)")
    client_users_columns = [col[1] for col in cursor.fetchall()]
    has_client_users_last_login = 'last_login' in client_users_columns
    print(f"   Client_users table has last_login: {'✅' if has_client_users_last_login else '❌'}")
    
    # Check staff table
    cursor.execute("PRAGMA table_info(staff)")
    staff_columns = [col[1] for col in cursor.fetchall()]
    has_staff_last_login = 'last_login' in staff_columns
    print(f"   Staff table has last_login: {'✅' if has_staff_last_login else '❌'}")
    
    # Test 2: Check current data
    print("\n2. 📊 Current Last Login Data...")
    
    # Clients
    cursor.execute("SELECT company_name, last_login FROM clients LIMIT 3")
    clients = cursor.fetchall()
    print("   Clients:")
    for client in clients:
        last_login = client[1] if client[1] else 'Never'
        print(f"     - {client[0]}: {last_login}")
    
    # Client Users
    cursor.execute("SELECT full_name, last_login FROM client_users LIMIT 3")
    users = cursor.fetchall()
    print("   Client Users:")
    for user in users:
        last_login = user[1] if user[1] else 'Never'
        print(f"     - {user[0]}: {last_login}")
    
    # Staff
    cursor.execute("SELECT name, last_login FROM staff LIMIT 3")
    staff_members = cursor.fetchall()
    print("   Staff:")
    for staff in staff_members:
        last_login = staff[1] if staff[1] else 'Never'
        print(f"     - {staff[0]}: {last_login}")
    
    # Test 3: Update last_login for testing
    print("\n3. 🔄 Testing Last Login Updates...")
    
    # Update a client's last_login
    cursor.execute("SELECT id, company_name FROM clients LIMIT 1")
    client = cursor.fetchone()
    if client:
        cursor.execute("UPDATE clients SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (client[0],))
        print(f"   ✅ Updated last_login for client: {client[1]}")
    
    # Update a client_user's last_login
    cursor.execute("SELECT id, full_name FROM client_users LIMIT 1")
    user = cursor.fetchone()
    if user:
        cursor.execute("UPDATE client_users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
        print(f"   ✅ Updated last_login for user: {user[1]}")
    
    # Update a staff's last_login
    cursor.execute("SELECT id, name FROM staff LIMIT 1")
    staff = cursor.fetchone()
    if staff:
        cursor.execute("UPDATE staff SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (staff[0],))
        print(f"   ✅ Updated last_login for staff: {staff[1]}")
    
    conn.commit()
    
    # Test 4: Verify updates
    print("\n4. ✅ Verifying Updates...")
    
    if client:
        cursor.execute("SELECT last_login FROM clients WHERE id = ?", (client[0],))
        result = cursor.fetchone()
        print(f"   Client {client[1]} last_login: {result[0] if result and result[0] else 'None'}")
    
    if user:
        cursor.execute("SELECT last_login FROM client_users WHERE id = ?", (user[0],))
        result = cursor.fetchone()
        print(f"   User {user[1]} last_login: {result[0] if result and result[0] else 'None'}")
    
    if staff:
        cursor.execute("SELECT last_login FROM staff WHERE id = ?", (staff[0],))
        result = cursor.fetchone()
        print(f"   Staff {staff[1]} last_login: {result[0] if result and result[0] else 'None'}")
    
    conn.close()
    print("\n🎉 Last Login Tracking Test Complete!")

if __name__ == "__main__":
    test_last_login_tracking()