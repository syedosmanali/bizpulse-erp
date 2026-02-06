"""
Check what tables already exist in Supabase
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

print("📊 Checking existing tables in Supabase...\n")

# Get all tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

tables = cursor.fetchall()

if tables:
    print(f"✅ Found {len(tables)} tables:\n")
    for table in tables:
        table_name = table['table_name'] if isinstance(table, dict) else table[0]
        
        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {table_name:40} {count:6} rows")
        except:
            print(f"   • {table_name:40} (error counting)")
else:
    print("⚪ No tables found - database is empty")

conn.close()
