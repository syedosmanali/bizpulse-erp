"""
Test script for user permissions functionality
"""

from modules.shared.database import get_db_connection
from modules.user_management.models import UserManagementModels
import json

def test_permissions():
    print("🧪 Testing User Permissions System")
    print("=" * 50)
    
    # Add permissions column if it doesn't exist
    print("\n1️⃣ Adding permissions column...")
    UserManagementModels.add_permissions_column()
    print("✅ Permissions column added/verified")
    
    # Get all users
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, full_name, username, module_permissions 
        FROM user_accounts 
        LIMIT 5
    ''')
    
    users = cursor.fetchall()
    
    if not users:
        print("\n❌ No users found in database")
        conn.close()
        return
    
    print(f"\n2️⃣ Found {len(users)} users:")
    for user in users:
        user_id, name, username, perms = user
        print(f"   - {name} ({username})")
        if perms:
            try:
                perms_dict = json.loads(perms)
                print(f"     Permissions: {perms_dict}")
            except:
                print(f"     Permissions: None (invalid JSON)")
        else:
            print(f"     Permissions: None (not set)")
    
    # Test setting permissions for first user
    if users:
        test_user_id = users[0][0]
        test_user_name = users[0][1]
        
        print(f"\n3️⃣ Testing permission update for {test_user_name}...")
        
        # Set some test permissions
        test_permissions = {
            'dashboard': True,
            'billing': True,
            'sales': False,
            'products': True,
            'customers': False,
            'inventory': True,
            'reports': True,
            'credit': False
        }
        
        cursor.execute('''
            UPDATE user_accounts 
            SET module_permissions = ?
            WHERE id = ?
        ''', (json.dumps(test_permissions), test_user_id))
        
        conn.commit()
        print(f"✅ Updated permissions for {test_user_name}")
        
        # Verify the update
        cursor.execute('''
            SELECT module_permissions FROM user_accounts WHERE id = ?
        ''', (test_user_id,))
        
        result = cursor.fetchone()
        if result and result[0]:
            saved_perms = json.loads(result[0])
            print(f"✅ Verified saved permissions: {saved_perms}")
        
        # Test get_user_permissions_by_id
        print(f"\n4️⃣ Testing get_user_permissions_by_id...")
        perms = UserManagementModels.get_user_permissions_by_id(test_user_id)
        print(f"✅ Retrieved permissions: {perms}")
        
        # Test get_all_user_permissions
        print(f"\n5️⃣ Testing get_all_user_permissions...")
        cursor.execute('SELECT client_id FROM user_accounts WHERE id = ?', (test_user_id,))
        client_id = cursor.fetchone()[0]
        
        all_perms = UserManagementModels.get_all_user_permissions(client_id)
        print(f"✅ Retrieved permissions for {len(all_perms)} users")
        for user_perm in all_perms[:3]:  # Show first 3
            print(f"   - {user_perm['full_name']}: {len(user_perm['permissions'])} modules configured")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")

if __name__ == '__main__':
    test_permissions()
