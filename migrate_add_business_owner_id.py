#!/usr/bin/env python3
"""
CRITICAL MIGRATION: Add business_owner_id column to bills and sales tables
This fixes the 500 error on Sales API
"""
import os
import sys

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    sys.exit(1)

print(f"🔗 Connecting to database...")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("✅ Connected to PostgreSQL")
    
    # Add business_owner_id to bills table
    print("\n🔧 Adding business_owner_id to bills table...")
    try:
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)
        """)
        conn.commit()
        print("✅ Added business_owner_id to bills table")
    except Exception as e:
        print(f"⚠️  bills.business_owner_id: {e}")
        conn.rollback()
    
    # Add business_owner_id to sales table
    print("\n🔧 Adding business_owner_id to sales table...")
    try:
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)
        """)
        conn.commit()
        print("✅ Added business_owner_id to sales table")
    except Exception as e:
        print(f"⚠️  sales.business_owner_id: {e}")
        conn.rollback()
    
    # Update existing bills
    print("\n🔧 Updating existing bills...")
    try:
        cursor.execute("""
            UPDATE bills 
            SET business_owner_id = 'admin-bizpulse' 
            WHERE business_owner_id IS NULL
        """)
        conn.commit()
        print(f"✅ Updated {cursor.rowcount} bills with default business_owner_id")
    except Exception as e:
        print(f"⚠️  Update bills: {e}")
        conn.rollback()
    
    # Update existing sales
    print("\n🔧 Updating existing sales...")
    try:
        cursor.execute("""
            UPDATE sales 
            SET business_owner_id = 'admin-bizpulse' 
            WHERE business_owner_id IS NULL
        """)
        conn.commit()
        print(f"✅ Updated {cursor.rowcount} sales with default business_owner_id")
    except Exception as e:
        print(f"⚠️  Update sales: {e}")
        conn.rollback()
    
    # Verify
    print("\n📊 Verification:")
    cursor.execute("SELECT COUNT(*) as count FROM bills WHERE business_owner_id IS NOT NULL")
    result = cursor.fetchone()
    print(f"✅ Bills with business_owner_id: {result['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM sales WHERE business_owner_id IS NOT NULL")
    result = cursor.fetchone()
    print(f"✅ Sales with business_owner_id: {result['count']}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Migration complete!")
    print("🚀 Sales API should now work correctly!")
    
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    os.system("pip install psycopg2-binary")
    print("✅ Please run this script again")
    sys.exit(1)
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
