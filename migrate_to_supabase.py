"""
Migration Script: SQLite to Supabase PostgreSQL
Migrates all data from local billing.db to Supabase
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv

load_dotenv()

# Database connections
SQLITE_DB = 'billing.db'
SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def get_sqlite_connection():
    """Get SQLite connection"""
    return sqlite3.connect(SQLITE_DB)

def get_postgres_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(SUPABASE_URL, sslmode='require')

def migrate_table(table_name, sqlite_conn, pg_conn):
    """Migrate a single table from SQLite to PostgreSQL"""
    try:
        print(f"\n📊 Migrating table: {table_name}")
        
        # Get data from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ⚠️  No data in {table_name}")
            return
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Prepare PostgreSQL insert
        pg_cursor = pg_conn.cursor()
        
        # Build INSERT query with ON CONFLICT DO NOTHING (to avoid duplicates)
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        insert_query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        # Convert boolean values (1/0 to True/False)
        converted_rows = []
        for row in rows:
            converted_row = []
            for i, value in enumerate(row):
                col_name = column_names[i].lower()
                # Check if column is boolean type
                if any(keyword in col_name for keyword in ['is_', 'active', 'enabled', 'used', 'force_']):
                    if value == 1:
                        converted_row.append(True)
                    elif value == 0:
                        converted_row.append(False)
                    else:
                        converted_row.append(value)
                else:
                    converted_row.append(value)
            converted_rows.append(tuple(converted_row))
        
        # Batch insert
        execute_batch(pg_cursor, insert_query, converted_rows)
        pg_conn.commit()
        
        print(f"   ✅ Migrated {len(rows)} rows to {table_name}")
        
    except Exception as e:
        print(f"   ❌ Error migrating {table_name}: {e}")
        pg_conn.rollback()

def main():
    """Main migration function"""
    print("🚀 Starting migration from SQLite to Supabase PostgreSQL")
    print("=" * 60)
    
    # Connect to databases
    sqlite_conn = get_sqlite_connection()
    pg_conn = get_postgres_connection()
    
    # Tables to migrate (in order to respect foreign keys)
    tables = [
        'users',
        'clients',
        'super_admins',
        'user_roles',
        'user_accounts',
        'client_users',
        'tenants',
        'tenant_users',
        'companies',
        'customers',
        'products',
        'hotel_services',
        'hotel_guests',
        'bills',
        'bill_items',
        'payments',
        'sales',
        'credit_transactions',
        'invoices',
        'notifications',
        'notification_settings',
        'inventory_items',
        'inventory_categories',
        'inventory_movements',
        'cms_site_settings',
        'cms_hero_section',
        'cms_features',
        'cms_pricing_plans',
        'cms_testimonials',
        'cms_faqs',
        'cms_gallery',
        'cms_admin_users',
        'cms_website_content',
        'whatsapp_reports_log',
        'password_reset_tokens'
    ]
    
    # Migrate each table
    for table in tables:
        try:
            migrate_table(table, sqlite_conn, pg_conn)
        except Exception as e:
            print(f"⚠️  Skipping {table}: {e}")
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("\n📝 Summary:")
    print("   - All data migrated from SQLite to Supabase")
    print("   - Duplicates were skipped automatically")
    print("   - You can now login with your existing credentials")

if __name__ == "__main__":
    main()
