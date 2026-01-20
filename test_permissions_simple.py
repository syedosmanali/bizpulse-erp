"""
Simple test for permissions - direct database check
"""

from modules.shared.database import get_db_connection
from modules.user_management.models import UserManagementModels
import json

print("🧪 Testing Permissions System")
print("=" * 60)

# Test 1: Check if column exists
print("\n1️⃣ Checking if module_permissions column exists...")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(user_accounts)")
columns = [row[1] for row in cursor.fetchall()]

if 'module_permissions' in columns:
    print("✅ module_permissions column exists")
else:
    print("❌ module_permissions column NOT found")
    print("   Adding column...")
    UserManagementModels.add_permissions_column()

# Test 2: Get a client_id
print("\n2️⃣ Getting client_id...")
cursor.execute("SELECT DISTINCT client_id FROM user_accounts LIMIT 1")
result = cursor.fetchone()

if not result:
    print("❌ No users found in database")
    conn.close()
    exit(1)

client_id = result[0]
print(f"✅ Using client_id: {client_id}")

# Test 3: Get all user permissions
print("\n3️⃣ Testing get_all_user_permissions...")
try:
    users = UserManagementModels.get_all_user_permissions(client_id)
    print(f"✅ Found {len(users)} users")
    
    for user in users[:3]:  # Show first 3
        print(f"\n   User: {user['full_name']} ({user['username']})")
        print(f"   Role: {user['role_name']}")
        print(f"   Permissions: {user['permissions']}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

conn.close()

print("\n" + "=" * 60)
print("✅ Test completed")
