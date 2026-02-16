"""
Test if local environment is using Supabase
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("="*60)
print("LOCAL ENVIRONMENT CHECK")
print("="*60)

# Check DATABASE_URL
db_url = os.environ.get('DATABASE_URL')

if db_url:
    print(f"\n✅ DATABASE_URL found!")
    print(f"   Type: {'PostgreSQL (Supabase)' if 'postgresql' in db_url else 'Unknown'}")
    print(f"   Host: {db_url.split('@')[1].split(':')[0] if '@' in db_url else 'N/A'}")
    print(f"   Length: {len(db_url)} characters")
else:
    print(f"\n❌ DATABASE_URL NOT found!")
    print(f"   Will use SQLite (billing.db)")

# Test connection
print("\n" + "="*60)
print("TESTING DATABASE CONNECTION")
print("="*60)

try:
    from modules.shared.database import get_db_connection, get_db_type
    
    db_type = get_db_type()
    print(f"\n📊 Database Type: {db_type}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'postgresql':
        # Test PostgreSQL
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL Connected!")
        print(f"   Version: {version[0][:50]}...")
        
        # Check if we can see bills
        cursor.execute("SELECT COUNT(*) FROM bills")
        count = cursor.fetchone()[0]
        print(f"   Bills in database: {count}")
        
    else:
        # Test SQLite
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"✅ SQLite Connected!")
        print(f"   Version: {version}")
        
        # Check if we can see bills
        cursor.execute("SELECT COUNT(*) FROM bills")
        count = cursor.fetchone()[0]
        print(f"   Bills in database: {count}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if db_url and 'postgresql' in db_url:
    print("✅ Local environment is configured for Supabase!")
    print("   You should see the same data as .com server")
else:
    print("⚠️  Local environment is using SQLite!")
    print("   Data will NOT sync with .com server")
    print("\n   To fix: Make sure .env file has DATABASE_URL")

print("="*60)
