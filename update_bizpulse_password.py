"""
Update BizPulse Admin Password in Production
"""
from modules.shared.database import get_db_connection, hash_password

NEW_PASSWORD = 'BizPulse@2024!'

print("="*60)
print("UPDATING BIZPULSE ADMIN PASSWORD")
print("="*60)

conn = get_db_connection()
cursor = conn.cursor()

# Check if user exists
cursor.execute("SELECT id, email FROM users WHERE email = %s", ('bizpulse.erp@gmail.com',))
user = cursor.fetchone()

if user:
    user_dict = dict(user) if hasattr(user, 'keys') else {'id': user[0], 'email': user[1]}
    print(f"\n✅ Found user: {user_dict['email']}")
    print(f"   ID: {user_dict['id']}")
    
    # Update password
    new_hash = hash_password(NEW_PASSWORD)
    cursor.execute("""
        UPDATE users 
        SET password_hash = %s
        WHERE email = %s
    """, (new_hash, 'bizpulse.erp@gmail.com'))
    
    conn.commit()
    
    print(f"\n✅ Password updated successfully!")
    print(f"\n📋 New Credentials:")
    print(f"   Email: bizpulse.erp@gmail.com")
    print(f"   Password: {NEW_PASSWORD}")
    print(f"\n⚠️  SAVE THESE CREDENTIALS SECURELY!")
    
else:
    print("\n❌ BizPulse admin user not found!")
    print("   Creating new user...")
    
    from datetime import datetime
    new_hash = hash_password(NEW_PASSWORD)
    
    cursor.execute("""
        INSERT INTO users (id, email, business_name, business_type, password_hash, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ('admin-bizpulse', 'bizpulse.erp@gmail.com', 'BizPulse ERP', 'software', new_hash, True, datetime.now().isoformat()))
    
    conn.commit()
    
    print(f"\n✅ User created successfully!")
    print(f"\n📋 Credentials:")
    print(f"   Email: bizpulse.erp@gmail.com")
    print(f"   Password: {NEW_PASSWORD}")

conn.close()

print("\n" + "="*60)
print("✅ UPDATE COMPLETE!")
print("="*60)
print("\nYou can now login to CMS with:")
print("URL: https://bizpulse24.com/cms/login")
print(f"Email: bizpulse.erp@gmail.com")
print(f"Password: {NEW_PASSWORD}")
print("="*60)
