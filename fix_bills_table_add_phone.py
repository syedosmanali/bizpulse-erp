"""
Add customer_phone column to bills table
"""
from modules.shared.database import get_db_connection, get_db_type

def add_customer_phone_column():
    """Add customer_phone column to bills table if it doesn't exist"""
    conn = get_db_connection()
    db_type = get_db_type()
    
    try:
        # Check if column exists
        if db_type == 'postgresql':
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='bills' AND column_name='customer_phone'
            """).fetchone()
        else:
            result = conn.execute("PRAGMA table_info(bills)").fetchall()
            result = [col for col in result if col['name'] == 'customer_phone']
        
        if not result:
            print("Adding customer_phone column to bills table...")
            
            if db_type == 'postgresql':
                conn.execute("ALTER TABLE bills ADD COLUMN customer_phone VARCHAR(20)")
            else:
                conn.execute("ALTER TABLE bills ADD COLUMN customer_phone TEXT")
            
            conn.commit()
            print("✅ Successfully added customer_phone column to bills table")
        else:
            print("✅ customer_phone column already exists in bills table")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_customer_phone_column()
