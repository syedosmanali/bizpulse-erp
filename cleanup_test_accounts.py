"""
Cleanup Test/Fake Accounts from Production Database
RUN THIS ONCE TO CLEAN UP
"""
from modules.shared.database import get_db_connection

print("="*60)
print("CLEANING UP TEST/FAKE ACCOUNTS")
print("="*60)

conn = get_db_connection()
cursor = conn.cursor()

# List of test/fake account IDs to delete
test_accounts = [
    'test-client-123',
    'api-test-client-456',
    'api-test-client-789',
    'auto-alert-client-999',
    '2849ebe3-94d2-4591-a881-c1f5f20d5ea8',  # Wrapper Test Company
    '613bb59f-7320-4b39-acd4-c7539715a9f3',  # Test Company
]

# Test emails to delete
test_emails = [
    'test@example.com',
    'apitest@example.com',
    'apitest2@example.com',
    'autoalert@test.com',
    'wrapper140909@example.com',
    'test140831@example.com',
]

print("\n🗑️  Deleting test accounts by ID...")
for account_id in test_accounts:
    try:
        cursor.execute("DELETE FROM clients WHERE id = %s", (account_id,))
        if cursor.rowcount > 0:
            print(f"   ✅ Deleted: {account_id}")
    except Exception as e:
        print(f"   ⚠️  {account_id}: {e}")

print("\n🗑️  Deleting test accounts by email...")
for email in test_emails:
    try:
        cursor.execute("DELETE FROM clients WHERE contact_email = %s", (email,))
        if cursor.rowcount > 0:
            print(f"   ✅ Deleted: {email}")
    except Exception as e:
        print(f"   ⚠️  {email}: {e}")

# Delete accounts with "Test" in company name
print("\n🗑️  Deleting accounts with 'Test' in company name...")
cursor.execute("""
    DELETE FROM clients 
    WHERE company_name LIKE '%Test%' 
    OR company_name LIKE '%test%'
    OR company_name LIKE '%API%'
    OR company_name LIKE '%Wrapper%'
""")
deleted = cursor.rowcount
print(f"   ✅ Deleted {deleted} test accounts")

conn.commit()

# Show remaining accounts
print("\n📊 Remaining Accounts:")
cursor.execute("""
    SELECT id, company_name, contact_email, username
    FROM clients
    ORDER BY created_at DESC
""")
accounts = cursor.fetchall()

for i, acc in enumerate(accounts, 1):
    if isinstance(acc, dict):
        print(f"\n{i}. {acc['company_name']}")
        print(f"   Email: {acc['contact_email']}")
        print(f"   Username: {acc['username']}")
    else:
        print(f"\n{i}. {acc[1]}")
        print(f"   Email: {acc[2]}")
        print(f"   Username: {acc[3]}")

conn.close()

print("\n" + "="*60)
print("✅ CLEANUP COMPLETE!")
print("="*60)
