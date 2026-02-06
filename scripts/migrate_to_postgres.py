"""
Data Migration Script: SQLite to PostgreSQL
Migrates all data from SQLite database to PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys
import os
from urllib.parse import urlparse
from datetime import datetime

# Load .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class MigrationStats:
    """Track migration statistics"""
    def __init__(self):
        self.tables = {}
        self.total_records = 0
        self.migrated_records = 0
        self.failed_records = 0
        self.start_time = None
        self.end_time = None
    
    def add_table(self, table_name, total, migrated, failed):
        self.tables[table_name] = {
            'total': total,
            'migrated': migrated,
            'failed': failed
        }
        self.total_records += total
        self.migrated_records += migrated
        self.failed_records += failed
    
    def print_summary(self):
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total Tables: {len(self.tables)}")
        print(f"Total Records: {self.total_records}")
        print(f"Migrated: {self.migrated_records}")
        print(f"Failed: {self.failed_records}")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"Duration: {duration:.2f} seconds")
        
        print("\nPer-Table Breakdown:")
        print("-"*60)
        for table_name, stats in self.tables.items():
            status = "✅" if stats['failed'] == 0 else "⚠️"
            print(f"{status} {table_name:30} {stats['migrated']:6}/{stats['total']:6} records")
        print("="*60)

def get_table_names(sqlite_conn):
    """Get all table names from SQLite database"""
    cursor = sqlite_conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_dependencies():
    """
    Define table dependencies for migration order
    Parent tables must be migrated before child tables
    """
    # Tables with no dependencies (migrate first)
    independent_tables = [
        'users', 'clients', 'tenants', 'super_admins',
        'companies', 'cms_site_settings', 'cms_hero_section',
        'cms_admin_users', 'cms_website_content'
    ]
    
    # Tables with dependencies (migrate after parents)
    dependent_tables = [
        'products', 'customers', 'hotel_services', 'cms_features',
        'cms_pricing_plans', 'cms_testimonials', 'cms_faqs', 'cms_gallery',
        'tenant_users', 'notification_settings', 'staff',
        'bills', 'hotel_guests', 'invoices',
        'bill_items', 'payments', 'sales', 'credit_transactions',
        'notifications', 'stock_alert_log', 'whatsapp_reports_log'
    ]
    
    return independent_tables + dependent_tables

def migrate_table_data(sqlite_conn, postgres_conn, table_name):
    """
    Migrate all records from SQLite table to PostgreSQL table
    
    Returns:
        Tuple of (total_records, migrated_records, failed_records)
    """
    print(f"\n📦 Migrating table: {table_name}")
    
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Get all records from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ℹ️  No data to migrate")
            return (0, 0, 0)
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        total_records = len(rows)
        migrated_records = 0
        failed_records = 0
        
        print(f"   📊 Found {total_records} records")
        
        # Prepare INSERT statement
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Migrate records in batches
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            
            for row in batch:
                try:
                    # Convert SQLite Row to tuple
                    values = tuple(row)
                    postgres_cursor.execute(insert_sql, values)
                    migrated_records += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to migrate record: {e}")
                    failed_records += 1
                    # Continue with next record
            
            # Commit batch
            postgres_conn.commit()
            print(f"   ✅ Migrated {migrated_records}/{total_records} records", end='\r')
        
        print(f"   ✅ Migrated {migrated_records}/{total_records} records")
        
        return (total_records, migrated_records, failed_records)
        
    except Exception as e:
        print(f"   ❌ Error migrating table {table_name}: {e}")
        postgres_conn.rollback()
        return (0, 0, 0)

def verify_migration(sqlite_conn, postgres_conn, table_name):
    """
    Verify record counts match between SQLite and PostgreSQL
    
    Returns:
        Tuple of (sqlite_count, postgres_count, match)
    """
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Get SQLite count
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        # Get PostgreSQL count
        postgres_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        postgres_count = postgres_cursor.fetchone()[0]
        
        match = sqlite_count == postgres_count
        
        return (sqlite_count, postgres_count, match)
        
    except Exception as e:
        print(f"   ⚠️  Error verifying {table_name}: {e}")
        return (0, 0, False)

def migrate_database(sqlite_db_path, postgres_url):
    """
    Main migration function
    
    Args:
        sqlite_db_path: Path to SQLite database file
        postgres_url: PostgreSQL connection URL
    """
    print("🚀 Starting database migration...")
    print(f"📁 SQLite: {sqlite_db_path}")
    print(f"🐘 PostgreSQL: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
    
    stats = MigrationStats()
    stats.start_time = datetime.now()
    
    # Connect to databases
    print("\n📡 Connecting to databases...")
    try:
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        print("   ✅ Connected to SQLite")
    except Exception as e:
        print(f"   ❌ Failed to connect to SQLite: {e}")
        return
    
    try:
        parsed = urlparse(postgres_url)
        postgres_conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # Remove leading '/'
        )
        print("   ✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"   ❌ Failed to connect to PostgreSQL: {e}")
        sqlite_conn.close()
        return
    
    # Get all tables
    all_tables = get_table_names(sqlite_conn)
    ordered_tables = get_table_dependencies()
    
    # Filter to only tables that exist
    tables_to_migrate = [t for t in ordered_tables if t in all_tables]
    
    # Add any tables not in dependency list
    remaining_tables = [t for t in all_tables if t not in tables_to_migrate]
    tables_to_migrate.extend(remaining_tables)
    
    print(f"\n📋 Found {len(tables_to_migrate)} tables to migrate")
    
    # Migrate each table
    for table_name in tables_to_migrate:
        total, migrated, failed = migrate_table_data(sqlite_conn, postgres_conn, table_name)
        stats.add_table(table_name, total, migrated, failed)
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    verification_failed = False
    for table_name in tables_to_migrate:
        sqlite_count, postgres_count, match = verify_migration(sqlite_conn, postgres_conn, table_name)
        if not match:
            print(f"   ⚠️  {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count}")
            verification_failed = True
    
    if not verification_failed:
        print("   ✅ All record counts match!")
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    
    stats.end_time = datetime.now()
    stats.print_summary()
    
    if stats.failed_records > 0:
        print("\n⚠️  Migration completed with errors")
        return False
    else:
        print("\n✅ Migration completed successfully!")
        return True

if __name__ == '__main__':
    # Get SQLite database path
    if len(sys.argv) > 1:
        sqlite_db_path = sys.argv[1]
    else:
        # Default to billing.db in parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sqlite_db_path = os.path.join(os.path.dirname(script_dir), 'billing.db')
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database not found: {sqlite_db_path}")
        sys.exit(1)
    
    # Get PostgreSQL URL
    postgres_url = os.environ.get('DATABASE_URL')
    if not postgres_url:
        print("❌ DATABASE_URL environment variable not set")
        print("\nUsage:")
        print("  export DATABASE_URL='postgresql://user:password@host:port/database'")
        print("  python migrate_to_postgres.py [sqlite_db_path]")
        sys.exit(1)
    
    # Run migration
    success = migrate_database(sqlite_db_path, postgres_url)
    
    sys.exit(0 if success else 1)
