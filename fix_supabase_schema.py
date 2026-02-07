"""
Fix Supabase schema to match local SQLite
Add missing columns to existing tables
"""

import psycopg2

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def fix_schema():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    print("🔧 Fixing Supabase schema...")
    print("=" * 60)
    
    # List of ALTER TABLE commands to add missing columns
    schema_fixes = [
        # Users table
        ("users", "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(255)"),
        ("users", "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(255)"),
        
        # Clients table
        ("clients", "ALTER TABLE clients ADD COLUMN IF NOT EXISTS password_plain TEXT"),
        
        # Products table
        ("products", "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT"),
        ("products", "ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("products", "ALTER TABLE products ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Bills table
        ("bills", "ALTER TABLE bills ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0"),
        ("bills", "ALTER TABLE bills ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("bills", "ALTER TABLE bills ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Bill items table
        ("bill_items", "ALTER TABLE bill_items ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("bill_items", "ALTER TABLE bill_items ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Payments table
        ("payments", "ALTER TABLE payments ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("payments", "ALTER TABLE payments ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Sales table
        ("sales", "ALTER TABLE sales ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)"),
        ("sales", "ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("sales", "ALTER TABLE sales ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Hotel services table
        ("hotel_services", "ALTER TABLE hotel_services ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("hotel_services", "ALTER TABLE hotel_services ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Companies table - fix boolean
        ("companies", "ALTER TABLE companies ALTER COLUMN send_daily_report TYPE BOOLEAN USING send_daily_report::boolean"),
        
        # Tenants table
        ("tenants", "ALTER TABLE tenants ADD COLUMN IF NOT EXISTS mobile_encrypted TEXT"),
        
        # Inventory items
        ("inventory_items", "ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS item_type VARCHAR(50)"),
        ("inventory_items", "ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("inventory_items", "ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Inventory categories
        ("inventory_categories", "ALTER TABLE inventory_categories ADD COLUMN IF NOT EXISTS icon VARCHAR(100)"),
        ("inventory_categories", "ALTER TABLE inventory_categories ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("inventory_categories", "ALTER TABLE inventory_categories ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Inventory movements
        ("inventory_movements", "ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS from_location VARCHAR(255)"),
        ("inventory_movements", "ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS to_location VARCHAR(255)"),
        ("inventory_movements", "ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("inventory_movements", "ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
        
        # Notifications - make id auto-generate if null
        ("notifications", "ALTER TABLE notifications ALTER COLUMN id SET DEFAULT gen_random_uuid()"),
        
        # Customers
        ("customers", "ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"),
        ("customers", "ALTER TABLE customers ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255)"),
    ]
    
    for table, sql in schema_fixes:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"✅ Fixed: {table}")
        except Exception as e:
            print(f"⚠️  {table}: {str(e)[:80]}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Schema fixes completed!")

if __name__ == "__main__":
    fix_schema()
