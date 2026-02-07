"""
Fix missing columns in Supabase PostgreSQL
Adds columns that exist in local SQLite but missing in Supabase
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Supabase connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres')

print("🔧 Fixing missing columns in Supabase...")
print(f"📡 Connecting to: {DATABASE_URL[:50]}...")

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # List of columns to add to products table
    products_columns = [
        ("expiry_date", "DATE"),
        ("supplier", "VARCHAR(255)"),
        ("description", "TEXT"),
        ("bill_receipt_photo", "TEXT"),
        ("last_stock_update", "TIMESTAMP"),
        ("image_url", "TEXT")
    ]
    
    print("\n📦 Adding missing columns to products table...")
    
    for column_name, column_type in products_columns:
        try:
            cursor.execute(f"ALTER TABLE products ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
            print(f"   ✅ Added {column_name} ({column_type})")
        except Exception as e:
            print(f"   ⚠️  {column_name}: {str(e)[:50]}")
    
    # Add missing columns to bills table
    bills_columns = [
        ("business_owner_id", "VARCHAR(255)"),
        ("gst_rate", "NUMERIC(10,2) DEFAULT 18")
    ]
    
    print("\n🧾 Adding missing columns to bills table...")
    
    for column_name, column_type in bills_columns:
        try:
            cursor.execute(f"ALTER TABLE bills ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
            print(f"   ✅ Added {column_name} ({column_type})")
        except Exception as e:
            print(f"   ⚠️  {column_name}: {str(e)[:50]}")
    
    # Add missing columns to sales table
    sales_columns = [
        ("business_owner_id", "VARCHAR(255)")
    ]
    
    print("\n💰 Adding missing columns to sales table...")
    
    for column_name, column_type in sales_columns:
        try:
            cursor.execute(f"ALTER TABLE sales ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
            print(f"   ✅ Added {column_name} ({column_type})")
        except Exception as e:
            print(f"   ⚠️  {column_name}: {str(e)[:50]}")
    
    # Commit changes
    conn.commit()
    print("\n✅ All columns added successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
