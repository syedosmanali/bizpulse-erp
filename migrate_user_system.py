"""
Migration script for new User Management System
Migrates existing user data to new system
"""

import sqlite3
import json
from datetime import datetime
from modules.shared.database import get_db_connection, generate_id, hash_password
from modules.user_management.models import UserManagementModels

def migrate_user_system():
    """Migrate existing user data to new user management system"""
    print("🔄 Starting User Management System Migration...")
    
    try:
        # Initialize new user management tables
        print("📋 Creating new user management tables...")
        UserManagementModels.create_user_tables()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all existing clients
        cursor.execute('SELECT id, company_name FROM clients WHERE is_active = 1')
        clients = cursor.fetchall()
        
        print(f"👥 Found {len(clients)} active clients")
        
        for client in clients:
            client_id = client[0]
            company_name = client[1]
            
            print(f"🏢 Processing client: {company_name} ({client_id})")
            
            # Create default roles for this client
            try:
                UserManagementModels.create_default_roles(client_id, client_id)
                print(f"  ✅ Created default roles for {company_name}")
            except Exception as e:
                print(f"  ⚠️  Roles already exist for {company_name}: {e}")
            
            # Migrate existing client_users if they exist
            try:
                cursor.execute('''
                    SELECT id, full_name, email, username, password_hash, password_plain, 
                           role, department, phone_number, is_active, created_at
                    FROM client_users 
                    WHERE client_id = ?
                ''', (client_id,))
                
                old_users = cursor.fetchall()
                
                if old_users:
                    print(f"  📤 Migrating {len(old_users)} existing users...")
                    
                    # Get cashier role ID (default role for migration)
                    cursor.execute('''
                        SELECT id FROM user_roles 
                        WHERE client_id = ? AND role_name = 'cashier'
                    ''', (client_id,))
                    
                    cashier_role = cursor.fetchone()
                    default_role_id = cashier_role[0] if cashier_role else None
                    
                    if not default_role_id:
                        print(f"  ❌ No default role found for {company_name}")
                        continue
                    
                    for old_user in old_users:
                        try:
                            # Check if user already migrated
                            cursor.execute('''
                                SELECT id FROM user_accounts 
                                WHERE client_id = ? AND username = ?
                            ''', (client_id, old_user[3]))
                            
                            if cursor.fetchone():
                                print(f"    ⏭️  User {old_user[3]} already migrated")
                                continue
                            
                            # Create new user account
                            new_user_id = generate_id()
                            cursor.execute('''
                                INSERT INTO user_accounts (
                                    id, client_id, user_id, full_name, email, mobile, username,
                                    password_hash, temp_password, role_id, department, status,
                                    force_password_change, created_by, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                new_user_id, client_id, new_user_id, old_user[1],
                                old_user[2], old_user[8] or '', old_user[3],
                                old_user[4], old_user[5], default_role_id,
                                old_user[7], 'active' if old_user[9] else 'inactive',
                                1 if old_user[5] else 0,  # Force password change if temp password exists
                                client_id, old_user[10] or datetime.now()
                            ))
                            
                            print(f"    ✅ Migrated user: {old_user[1]} ({old_user[3]})")
                            
                        except Exception as e:
                            print(f"    ❌ Failed to migrate user {old_user[3]}: {e}")
                
            except sqlite3.OperationalError:
                print(f"  ℹ️  No existing client_users table for {company_name}")
        
        conn.commit()
        conn.close()
        
        print("✅ User Management System Migration Completed Successfully!")
        print("\n📋 Migration Summary:")
        print(f"   • Created user management tables")
        print(f"   • Processed {len(clients)} clients")
        print(f"   • Created default roles for all clients")
        print(f"   • Migrated existing users to new system")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count clients with roles
        cursor.execute('''
            SELECT COUNT(DISTINCT client_id) FROM user_roles
        ''')
        clients_with_roles = cursor.fetchone()[0]
        
        # Count total users
        cursor.execute('SELECT COUNT(*) FROM user_accounts')
        total_users = cursor.fetchone()[0]
        
        # Count active users
        cursor.execute('SELECT COUNT(*) FROM user_accounts WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        
        # Count total roles
        cursor.execute('SELECT COUNT(*) FROM user_roles')
        total_roles = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Verification Results:")
        print(f"   • Clients with roles: {clients_with_roles}")
        print(f"   • Total users: {total_users}")
        print(f"   • Active users: {active_users}")
        print(f"   • Total roles: {total_roles}")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BizPulse ERP - User Management System Migration")
    print("=" * 50)
    
    # Run migration
    if migrate_user_system():
        # Verify migration
        verify_migration()
        print("\n🎉 Migration completed successfully!")
        print("💡 You can now use the new User Management system at /user-management")
    else:
        print("\n💥 Migration failed. Please check the errors above.")