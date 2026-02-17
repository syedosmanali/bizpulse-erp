"""
Debug script to diagnose login issues between local and deployed environments
"""

import os
import sys
import logging
from modules.shared.database import get_db_connection, get_db_type
from modules.auth.service import AuthService
from modules.shared.database import hash_password

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and get basic info"""
    print("🔍 Testing database connection...")
    
    try:
        db_type = get_db_type()
        print(f"📊 Database type: {db_type}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test basic query
        if db_type == 'postgresql':
            cursor.execute("SELECT version();")
        else:
            cursor.execute("SELECT sqlite_version();")
        
        result = cursor.fetchone()
        if result:
            # Handle both dict and tuple results
            if hasattr(result, 'keys'):  # DictRow from PostgreSQL
                version_info = result[list(result.keys())[0]]
            else:  # Tuple from SQLite
                version_info = result[0]
            print(f"✅ Database connection successful: {version_info}")
        else:
            print("✅ Database connection successful")
        
        # Check if users table exists and has records
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()
        if user_count:
            if hasattr(user_count, 'keys'):  # DictRow from PostgreSQL
                user_count = user_count['count']
            else:  # Tuple from SQLite
                user_count = user_count[0]
        else:
            user_count = 0
        print(f"👥 Users table record count: {user_count}")
        
        # Check if clients table exists and has records
        cursor.execute("SELECT COUNT(*) FROM clients;")
        client_count = cursor.fetchone()
        if client_count:
            if hasattr(client_count, 'keys'):  # DictRow from PostgreSQL
                client_count = client_count['count']
            else:  # Tuple from SQLite
                client_count = client_count[0]
        else:
            client_count = 0
        print(f"🏢 Clients table record count: {client_count}")
        
        # Show table structure for debugging
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """)
        else:
            cursor.execute("PRAGMA table_info(users);")
        
        columns = cursor.fetchall()
        if columns:
            if hasattr(columns[0], 'keys'):  # DictRow from PostgreSQL
                column_names = [col['column_name'] for col in columns]
            else:  # Tuple from SQLite
                column_names = [col[0] for col in columns]
        else:
            column_names = []
        print(f"📋 Users table columns: {column_names}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication():
    """Test authentication with sample credentials"""
    print("\n🔐 Testing authentication system...")
    
    try:
        auth_service = AuthService()
        
        # Test with common login credentials
        test_credentials = [
            ('bizpulse.erp@gmail.com', 'BizPulse@2024!'),
            ('admin@bizpulse.com', 'BizPulse@2024!'),
            ('support@bizpulse.com', 'BizPulse@2024!')
        ]
        
        for login_id, password in test_credentials:
            print(f"\nTesting login: {login_id}")
            result = auth_service.authenticate_user(login_id, password)
            
            if result['success']:
                print(f"✅ Login successful for {login_id}")
                print(f"   User Type: {result['user']['type']}")
                print(f"   User ID: {result['user']['id']}")
            else:
                print(f"❌ Login failed for {login_id}: {result['message']}")
                
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting login debug process...")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔗 Database URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    
    # Test database connection
    db_success = test_database_connection()
    
    if db_success:
        # Test authentication
        auth_success = test_authentication()
        
        if auth_success:
            print("\n🎉 Debug completed successfully!")
            print("💡 If login still fails on deployed server:")
            print("   1. Check if database tables exist on Supabase")
            print("   2. Verify user records are present")
            print("   3. Ensure DATABASE_URL is correctly set in deployment")
            print("   4. Run the SQL fixes in RUN_THIS_IN_SUPABASE.md")
        else:
            print("\n⚠️  Authentication test failed")
    else:
        print("\n❌ Database connection test failed")
        print("💡 Check your DATABASE_URL and database connectivity")

if __name__ == "__main__":
    main()