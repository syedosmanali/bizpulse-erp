"""
Verify which database has updated passwords
"""
from modules.shared.database import get_db_connection, get_db_type, hash_password

print(f"\nDatabase Type: {get_db_type()}")

conn = get_db_connection()
cursor = conn.cursor()

# Check tasleem password
cursor.execute("SELECT username, password_hash FROM clients WHERE username = %s", ('tasleem',))
result = cursor.fetchone()

if result:
    if isinstance(result, dict):
        username = result['username']
        stored_hash = result['password_hash']
    else:
        username = result[0]
        stored_hash = result[1]
    
    test_hash = hash_password('Tasleem@123')
    
    print(f"\nTasleem:")
    print(f"  Password matches 'Tasleem@123': {test_hash == stored_hash}")
    
    # Try old password
    old_hash = hash_password('admin123')
    print(f"  Password matches 'admin123': {old_hash == stored_hash}")

conn.close()
