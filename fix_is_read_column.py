#!/usr/bin/env python3
"""
Fix the notifications table is_read column type issue
"""

from modules.shared.database import get_db_connection

def fix_is_read_column():
    """Fix the is_read column to be boolean type"""
    print("🔧 Fixing notifications table is_read column...")
    
    try:
        conn = get_db_connection()
        
        # Try to alter the column type
        try:
            conn.execute("ALTER TABLE notifications ALTER COLUMN is_read TYPE BOOLEAN USING is_read::boolean")
            conn.commit()
            print("✅ Successfully converted is_read column to boolean")
        except Exception as e:
            print(f"⚠️  Error converting column: {e}")
            # Try alternative approach
            try:
                # Add new boolean column
                conn.execute("ALTER TABLE notifications ADD COLUMN is_read_new BOOLEAN")
                # Copy data
                conn.execute("UPDATE notifications SET is_read_new = (is_read = 1)")
                # Drop old column
                conn.execute("ALTER TABLE notifications DROP COLUMN is_read")
                # Rename new column
                conn.execute("ALTER TABLE notifications RENAME COLUMN is_read_new TO is_read")
                conn.commit()
                print("✅ Successfully fixed is_read column using alternative method")
            except Exception as e2:
                print(f"❌ Failed to fix column: {e2}")
                conn.rollback()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_is_read_column()