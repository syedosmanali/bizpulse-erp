"""
Drop all tables from Supabase (fresh start)
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file manually
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("🗑️  Dropping all tables from Supabase...\n")

# Get all tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

tables = cursor.fetchall()

if not tables:
    print("⚪ No tables to drop")
    conn.close()
    sys.exit(0)

print(f"Found {len(tables)} tables to drop:\n")

# Drop all tables with CASCADE to handle foreign keys
for table in tables:
    table_name = table['table_name'] if isinstance(table, dict) else table[0]
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        print(f"   ✅ Dropped: {table_name}")
    except Exception as e:
        print(f"   ❌ Failed to drop {table_name}: {e}")

conn.commit()
conn.close()

print("\n✅ All tables dropped successfully!")
print("   Run setup_supabase_schema.py to recreate tables")
