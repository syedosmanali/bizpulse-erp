"""
Diagnostic script to identify the exact login issue on deployed server
"""

import os
from modules.shared.database import get_db_connection, get_db_type, hash_password
import hashlib

def diagnose_login_issue():
    """Diagnose the exact login issue"""
    print("🔍 Diagnosing login issue...")
    
    db_type = get_db_type()
    print(f"📊 Database type: {db_type}")
    
    if db_type != 'postgresql':
        print("❌ This script is for diagnosing PostgreSQL (deployed server) issues")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("\n📋 Checking users table structure...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        column_names = [col['column_name'] for col in columns]
        print(f"Columns in users table: {column_names}")
        
        print("\n📋 Checking if bizpulse admin user exists...")
        cursor.execute("SELECT id, email, password_hash, business_name, is_active FROM users WHERE email = %s", ('bizpulse.erp@gmail.com',))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found: {user['email']}")
            print(f"   ID: {user['id']}")
            print(f"   Business: {user['business_name']}")
            print(f"   Active: {user['is_active']}")
            
            # Test password hash
            stored_hash = user['password_hash']
            test_password = 'BizPulse@2024!'
            computed_hash = hashlib.sha256(test_password.encode()).hexdigest()
            
            print(f"\n🔒 Password verification:")
            print(f"   Stored hash: {stored_hash[:20]}...")
            print(f"   Computed hash: {computed_hash[:20]}...")
            print(f"   Match: {stored_hash == computed_hash}")
        else:
            print("❌ BizPulse admin user not found!")
            
            # Check if any users exist
            cursor.execute("SELECT email FROM users LIMIT 5;")
            all_users = cursor.fetchall()
            if all_users:
                print(f"Other users found: {[u['email'] for u in all_users]}")
            else:
                print("No users found in the database!")
        
        print("\n📋 Checking clients table...")
        cursor.execute("SELECT COUNT(*) FROM clients;")
        client_count = cursor.fetchone()['count']
        print(f"Total clients: {client_count}")
        
        if client_count > 0:
            cursor.execute("SELECT id, company_name, contact_email, username, is_active FROM clients LIMIT 3;")
            clients = cursor.fetchall()
            for client in clients:
                print(f"   Client: {client['contact_email']} - Active: {client['is_active']}")
        
        print("\n📋 Checking if required columns exist...")
        required_columns = {
            'users': ['id', 'email', 'password_hash', 'is_active', 'business_name'],
            'clients': ['id', 'username', 'password_hash', 'is_active', 'contact_email'],
            'bills': ['id', 'business_owner_id', 'user_id', 'customer_id'],
            'products': ['id', 'business_owner_id', 'user_id'],
            'customers': ['id', 'business_owner_id', 'user_id']
        }
        
        for table, cols in required_columns.items():
            try:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
                table_cols = [row['column_name'] for row in cursor.fetchall()]
                missing = [col for col in cols if col not in table_cols]
                if missing:
                    print(f"   ⚠️  Missing columns in {table}: {missing}")
                else:
                    print(f"   ✅ All required columns present in {table}")
            except Exception as e:
                print(f"   ❌ Error checking {table}: {e}")
        
        print("\n📋 Checking for user management tables...")
        um_tables = ['user_accounts', 'user_roles', 'user_sessions', 'user_activity_log']
        for table in um_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()['count']
                print(f"   {table}: ✅ Exists (rows: {count})")
            except Exception as e:
                print(f"   {table}: ❌ Missing - {str(e)[:50]}...")
                
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def check_specific_user_login(email, password):
    """Test a specific login"""
    print(f"\n🔍 Testing login for: {email}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check in users table
        cursor.execute("SELECT id, email, password_hash, is_active FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"   Found in users table: {user['email']}")
            stored_hash = user['password_hash']
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            match = stored_hash == computed_hash
            print(f"   Password match: {match}")
            print(f"   User active: {user['is_active']}")
        else:
            print("   ❌ Not found in users table")
            
        # Check in clients table
        cursor.execute("SELECT id, contact_email, username, password_hash, is_active FROM clients WHERE contact_email = %s OR username = %s", (email, email))
        client = cursor.fetchone()
        
        if client:
            print(f"   Found in clients table: {client['contact_email']}")
            stored_hash = client['password_hash']
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            match = stored_hash == computed_hash
            print(f"   Password match: {match}")
            print(f"   Client active: {client['is_active']}")
        else:
            print("   ❌ Not found in clients table")
            
    except Exception as e:
        print(f"   ❌ Error checking user: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting deployed login diagnosis...")
    diagnose_login_issue()
    
    # Test common login credentials
    print("\n" + "="*50)
    print("TESTING COMMON LOGIN CREDENTIALS")
    print("="*50)
    
    test_credentials = [
        ('bizpulse.erp@gmail.com', 'BizPulse@2024!'),
        ('admin@bizpulse.com', 'BizPulse@2024!'),
        ('support@bizpulse.com', 'BizPulse@2024!')
    ]
    
    for email, password in test_credentials:
        check_specific_user_login(email, password)
    
    print("\n💡 Recommendations:")
    print("   1. If users exist but passwords don't match, the password hash might be incorrect")
    print("   2. If tables are missing, run the SQL fixes in Supabase SQL Editor")
    print("   3. If users don't exist, you may need to create them")