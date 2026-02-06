"""
Simple migration: SQLite to Supabase
Creates schema and migrates data in one go
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

print("🚀 Starting SQLite to Supabase migration...")
print("=" * 60)

# Step 1: Drop all existing tables
print("\n📋 Step 1: Cleaning Supabase database...")
os.system(f"{sys.executable} scripts/drop_all_supabase_tables.py")

# Step 2: Create fresh schema
print("\n📋 Step 2: Creating fresh schema...")
os.system(f"{sys.executable} scripts/setup_supabase_schema.py")

# Step 3: Migrate data
print("\n📋 Step 3: Migrating data from SQLite...")
os.system(f"{sys.executable} scripts/migrate_to_postgres.py")

print("\n" + "=" * 60)
print("✅ Migration complete!")
print("   Your data is now in Supabase PostgreSQL")
print("   Restart your app to use Supabase")
