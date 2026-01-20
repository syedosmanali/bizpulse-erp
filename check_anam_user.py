"""
Check anam user details
"""
from modules.shared.database import get_db_connection
import json

conn = get_db_connection()
cursor = conn.cursor()

# Find anam user
cursor.execute('''
    SELECT id, username, full_name, client_id, module_permissions 
    FROM user_accounts 
    WHERE username LIKE '%anam%'
''')

users = cursor.fetchall()

print("🔍 Users matching 'anam':")
print("=" * 60)

for user in users:
    user_id, username, full_name, client_id, perms = user
    print(f"\nUser: {full_name} ({username})")
    print(f"ID: {user_id}")
    print(f"Client ID: {client_id}")
    
    if perms:
        try:
            perms_dict = json.loads(perms)
            print(f"Permissions: {perms_dict}")
        except:
            print(f"Permissions: {perms} (invalid JSON)")
    else:
        print("Permissions: None")

# Check what user_type this user would have when logging in
print("\n" + "=" * 60)
print("Note: Users in user_accounts table are employees")
print("They should have user_type='employee' when logged in")

conn.close()
