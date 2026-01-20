"""
Test User Login
Verify that created users can login properly
"""

import sqlite3
from modules.shared.database import get_db_connection, hash_password
from modules.auth.service import AuthService

def test_user_login():
    """Test user login functionality"""
    print("🧪 Testing User Login...")
    print("=" * 40)
    
    # Get a test user from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ua.username, ua.temp_password, ua.password_hash, c.company_name
        FROM user_accounts ua
        LEFT JOIN clients c ON ua.client_id = c.id
        WHERE ua.status = 'active'
        LIMIT 1
    ''')
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        print("❌ No test users found in database")
        return
    
    username, temp_password, password_hash, company_name = user
    print(f"📋 Testing user: {username}")
    print(f"   Password: {temp_password}")
    print(f"   Company: {company_name}")
    print(f"   Hash: {password_hash[:20]}...")
    
    # Test authentication
    auth_service = AuthService()
    
    print(f"\n🔐 Testing login with username: {username}, password: {temp_password}")
    result = auth_service.authenticate_user(username, temp_password)
    
    if result['success']:
        print("✅ Login successful!")
        print(f"   User ID: {result['user']['id']}")
        print(f"   Name: {result['user']['name']}")
        print(f"   Type: {result['user']['type']}")
        print(f"   Client ID: {result['user'].get('client_id', 'Not set')}")
        print(f"   Company: {result['user'].get('company_name', 'Not set')}")
    else:
        print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
        
        # Debug: Check password hash
        print(f"\n🔍 Debug info:")
        print(f"   Expected hash: {password_hash}")
        print(f"   Actual hash: {hash_password(temp_password)}")
        print(f"   Match: {hash_password(temp_password) == password_hash}")

if __name__ == "__main__":
    test_user_login()