"""
Add missing business_owner_id column to bills and sales tables
This is the CRITICAL FIX for the 500 error on Sales API
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set DATABASE_URL environment variable
os.environ['DATABASE_URL'] = 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'

from modules.shared.database import get_db_connection

def add_business_owner_id_columns():
    """Add business_owner_id column to bills and sales tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔧 Adding business_owner_id columns...")
    
    # Add to bills table
    try:
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN business_owner_id VARCHAR(255)
        """)
        conn.commit()
        print("✅ Added business_owner_id to bills table")
    except Exception as e:
        print(f"⚠️  bills.business_owner_id: {e}")
        conn.rollback()
    
    # Add to sales table
    try:
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN business_owner_id VARCHAR(255)
        """)
        conn.commit()
        print("✅ Added business_owner_id to sales table")
    except Exception as e:
        print(f"⚠️  sales.business_owner_id: {e}")
        conn.rollback()
    
    # Update existing bills to set business_owner_id = 'admin-bizpulse' (default user)
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
    
    # Update existing sales to set business_owner_id = 'admin-bizpulse' (default user)
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
    
    # Verify the columns exist
    print("\n📊 Verifying columns...")
    
    try:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'bills' AND column_name = 'business_owner_id'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ bills.business_owner_id exists: {result['data_type']}")
        else:
            print("❌ bills.business_owner_id NOT FOUND")
    except Exception as e:
        print(f"⚠️  Verify bills: {e}")
    
    try:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sales' AND column_name = 'business_owner_id'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ sales.business_owner_id exists: {result['data_type']}")
        else:
            print("❌ sales.business_owner_id NOT FOUND")
    except Exception as e:
        print(f"⚠️  Verify sales: {e}")
    
    # Count records
    try:
        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE business_owner_id IS NOT NULL")
        result = cursor.fetchone()
        print(f"\n📊 Bills with business_owner_id: {result['count']}")
    except Exception as e:
        print(f"⚠️  Count bills: {e}")
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM sales WHERE business_owner_id IS NOT NULL")
        result = cursor.fetchone()
        print(f"📊 Sales with business_owner_id: {result['count']}")
    except Exception as e:
        print(f"⚠️  Count sales: {e}")
    
    conn.close()
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    add_business_owner_id_columns()
