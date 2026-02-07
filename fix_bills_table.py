"""
Fix bills table - add missing business_owner_id column
"""

import psycopg2

SUPABASE_URL = "postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

def fix_bills_table():
    conn = psycopg2.connect(SUPABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    try:
        print("🔧 Adding business_owner_id column to bills table...")
        
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)
        """)
        
        conn.commit()
        print("✅ Column added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_bills_table()
