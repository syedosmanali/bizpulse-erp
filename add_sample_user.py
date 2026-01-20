"""
Add Sample User Script
Creates a sample user for testing the user management system
"""

import sqlite3
from modules.shared.database import get_db_connection, generate_id, hash_password
from modules.user_management.models import UserManagementModels
import json

def add_sample_user():
    """Add a sample user to the database"""
    print("🔄 Adding sample user...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the first active client
        cursor.execute('SELECT id, company_name FROM clients WHERE is_active = 1 LIMIT 1')
        client = cursor.fetchone()
        
        if not client:
            print("❌ No active clients found. Please create a client first.")
            return False
        
        client_id = client[0]
        company_name = client[1]
        
        print(f"📋 Using client: {company_name} ({client_id})")
        
        # Check if roles exist for this client
        cursor.execute('SELECT id FROM user_roles WHERE client_id = ? LIMIT 1', (client_id,))
        role = cursor.fetchone()
        
        if not role:
            print("🔧 Creating default roles first...")
            UserManagementModels.create_default_roles(client_id, client_id)
            
            # Get the cashier role
            cursor.execute('SELECT id FROM user_roles WHERE client_id = ? AND role_name = "cashier"', (client_id,))
            role = cursor.fetchone()
        
        role_id = role[0]
        
        # Check if sample user already exists
        cursor.execute('SELECT id FROM user_accounts WHERE client_id = ? AND username = "demo_user"', (client_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("ℹ️  Sample user already exists")
            return True
        
        # Create sample user
        user_id = generate_id()
        temp_password = "demo123"
        
        cursor.execute('''
            INSERT INTO user_accounts (
                id, client_id, user_id, full_name, email, mobile, username,
                password_hash, temp_password, role_id, department, status,
                force_password_change, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            user_id, client_id, user_id, "Demo User", "demo@example.com", 
            "9876543210", "demo_user", hash_password(temp_password), temp_password,
            role_id, "Sales", "active", 0, client_id
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample user created successfully!")
        print(f"   Username: demo_user")
        print(f"   Password: {temp_password}")
        print(f"   Full Name: Demo User")
        print(f"   Role: Cashier")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample user: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BizPulse ERP - Sample User Creator")
    print("=" * 40)
    
    if add_sample_user():
        print("\n🎉 Sample user added successfully!")
        print("💡 You can now see the user in the User Management dashboard")
    else:
        print("\n💥 Failed to add sample user. Please check the errors above.")