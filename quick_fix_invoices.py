"""
Quick fix for invoice visibility - Assign all bills to a single user
"""
from modules.shared.database import get_db_connection
import sys

conn = get_db_connection()
cursor = conn.cursor()

# Get distinct owner IDs from bills
cursor.execute('SELECT DISTINCT business_owner_id FROM bills WHERE business_owner_id IS NOT NULL')
owner_ids = [row['business_owner_id'] if isinstance(row, dict) else row[0] for row in cursor.fetchall()]

print(f"📊 Found {len(owner_ids)} different business_owner_ids in bills")
print(f"   Owner IDs: {owner_ids[:3]}...")  # Show first 3

# Get all users
cursor.execute('SELECT id, email FROM users LIMIT 5')
users = cursor.fetchall()

print("\n👥 Sample users in system:")
for user in users:
    user_dict = dict(user) if isinstance(user, dict) else {'id': user[0], 'email': user[1]}
    print(f"   - {user_dict['email']}: {user_dict['id']}")

print("\n" + "="*60)
print("🔧 FIX OPTION: Assign all bills to ONE user")
print("="*60)
print("\nEnter the user_id you want to assign all bills to:")
print("(This will make all 219 bills visible in your invoice module)")
print("\nOr press Enter to skip and I'll show you another solution...")

user_input = input("\nUser ID: ").strip()

if user_input:
    # Update all bills to this user_id
    try:
        cursor.execute('UPDATE bills SET business_owner_id = ?', (user_input,))
        conn.commit()
        print(f"\n✅ SUCCESS! Updated all bills to user_id: {user_input}")
        print("   Now refresh your invoice module to see all bills!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
else:
    print("\n📝 Alternative: I can modify the invoice service to show ALL bills")
    print("   regardless of business_owner_id. Would you like me to do that?")

conn.close()
