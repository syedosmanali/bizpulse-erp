"""
Quick script to check SQLite database contents
"""
import sqlite3
import os

# Get database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(os.path.dirname(script_dir), 'billing.db')

if not os.path.exists(db_path):
    print(f"❌ Database not found: {db_path}")
    exit(1)

print(f"📁 Checking database: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"📊 Found {len(tables)} tables\n")
print("="*60)

total_records = 0
tables_with_data = []

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    total_records += count
    
    if count > 0:
        tables_with_data.append((table, count))
        print(f"✅ {table:30} {count:6} records")
    else:
        print(f"⚪ {table:30} {count:6} records")

print("="*60)
print(f"\n📈 Total Records: {total_records}")
print(f"📦 Tables with Data: {len(tables_with_data)}/{len(tables)}")

if tables_with_data:
    print("\n🔥 Tables to migrate:")
    for table, count in tables_with_data:
        print(f"   • {table}: {count} records")

conn.close()
