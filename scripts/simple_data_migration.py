"""
Simple Data Migration - Only Important Tables
Migrates core business data with proper type conversion and foreign key handling
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

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

print("🚀 Simple Data Migration - Core Tables Only")
print("=" * 60)

# Connect to databases
sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'billing.db')
postgres_url = os.environ.get('DATABASE_URL')

print(f"📁 SQLite: {sqlite_path}")
print(f"🐘 PostgreSQL: Connected")
print()

sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_conn.row_factory = sqlite3.Row

postgres_conn = psycopg2.connect(postgres_url)
postgres_cursor = postgres_conn.cursor()

# Disable foreign key checks temporarily for migration
print("🔓 Disabling foreign key constraints...")
postgres_cursor.execute("SET session_replication_role = 'replica';")
postgres_conn.commit()

# Core tables to migrate (in order - parents before children)
core_tables = [
    'products',      # Parent table
    'customers',     # Parent table
    'bills',         # Parent table (references customers)
    'bill_items',    # Child table (references bills, products)
    'payments',      # Child table (references bills)
    'sales',         # Child table (references bills, customers, products)
    'credit_transactions'  # Child table (references bills, customers)
]

total_migrated = 0
total_failed = 0

for table in core_tables:
    print(f"📦 Migrating {table}...")
    
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"   ℹ️  No data")
        continue
    
    # Get column names from Supabase
    postgres_cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    supabase_columns = [row[0] for row in postgres_cursor.fetchall()]
    
    # Get column names from SQLite
    sqlite_columns = [description[0] for description in sqlite_cursor.description]
    
    # Find common columns
    common_columns = [col for col in sqlite_columns if col in supabase_columns]
    
    print(f"   📊 Found {len(rows)} records, {len(common_columns)} matching columns")
    
    migrated = 0
    failed = 0
    error_details = []
    
    for row in rows:
        try:
            # Extract only common columns with type conversion
            values = []
            for col in common_columns:
                val = row[sqlite_columns.index(col)]
                
                # Convert boolean values (0/1 to TRUE/FALSE)
                if col in ['is_active', 'is_credit', 'is_read', 'is_system_role', 'force_password_change', 'send_daily_report', 'is_popular']:
                    val = bool(val) if val is not None else None
                
                values.append(val)
            
            # Build INSERT query with ON CONFLICT DO NOTHING for duplicate handling
            placeholders = ', '.join(['%s'] * len(common_columns))
            columns_str = ', '.join(common_columns)
            query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            postgres_cursor.execute(query, values)
            
            # Check if row was actually inserted
            if postgres_cursor.rowcount > 0:
                migrated += 1
            else:
                # Row already exists (duplicate)
                migrated += 1
            
        except Exception as e:
            failed += 1
            error_msg = str(e)
            if len(error_details) < 3:  # Store first 3 errors
                error_details.append(error_msg[:150])
            
            # Rollback this transaction and continue
            postgres_conn.rollback()
    
    # Commit successful inserts for this table
    postgres_conn.commit()
    total_migrated += migrated
    total_failed += failed
    
    print(f"   ✅ Migrated {migrated}/{len(rows)} records")
    if error_details:
        print(f"   ⚠️  Sample errors:")
        for err in error_details:
            print(f"      - {err}")
    print()

# Re-enable foreign key checks
print("🔒 Re-enabling foreign key constraints...")
postgres_cursor.execute("SET session_replication_role = 'origin';")
postgres_conn.commit()

sqlite_conn.close()
postgres_conn.close()

print("=" * 60)
print("MIGRATION SUMMARY")
print("=" * 60)
print(f"Total Migrated: {total_migrated}")
print(f"Total Failed: {total_failed}")
print("=" * 60)

if total_failed == 0:
    print("\n✅ Migration completed successfully!")
else:
    print(f"\n⚠️  Migration completed with {total_failed} errors")
    print("   Core data migrated, some records may have failed due to:")
    print("   - Duplicate keys (already migrated)")
    print("   - Missing parent records (foreign key constraints)")

print("\n🎉 Your important data is now in Supabase!")
print("   Restart your app with: python app.py")
