"""
Fix invoice visibility issue - Update bills to match current user
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Get all unique business_owner_ids from bills
cursor.execute('SELECT DISTINCT business_owner_id FROM bills WHERE business_owner_id IS NOT NULL')
owner_ids = cursor.fetchall()

print("📊 Found business_owner_ids in bills:")
for owner in owner_ids:
    owner_id = owner['business_owner_id'] if isinstance(owner, dict) else owner[0]
    cursor.execute('SELECT COUNT(*) as count FROM bills WHERE business_owner_id = ?', (owner_id,))
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    print(f"  - {owner_id}: {count} bills")

# Get all users
print("\n👥 Available users:")
cursor.execute('SELECT id, email, business_name FROM users')
users = cursor.fetchall()
for user in users:
    user_dict = dict(user) if isinstance(user, dict) else {'id': user[0], 'email': user[1], 'business_name': user[2]}
    print(f"  - {user_dict['email']} ({user_dict['business_name']}): {user_dict['id']}")

print("\n" + "="*60)
print("🔧 SOLUTION OPTIONS:")
print("="*60)
print("\nOption 1: Update all bills to your current user_id")
print("  This will make all bills visible to you in the invoice module")
print("\nOption 2: Remove business_owner_id filter temporarily")
print("  This will show all bills regardless of owner")
print("\nWhich user_id should own these bills?")
print("Enter the user_id or email, or type 'all' to see all bills:")

conn.close()
