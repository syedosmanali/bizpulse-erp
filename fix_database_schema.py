#!/usr/bin/env python3
"""
Fix database schema issues for notifications table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import get_db_connection, get_db_type

def fix_notifications_table():
    """Fix the notifications table schema issues"""
    print("🔧 Fixing notifications table schema...")
    
    try:
        conn = get_db_connection()
        db_type = get_db_type()
        
        print(f"Database type: {db_type}")
        
        if db_type == 'postgresql':
            # Check current column type
            result = conn.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'notifications' AND column_name = 'is_read'
            """).fetchone()
            
            if result:
                current_type = result['data_type']
                print(f"Current is_read column type: {current_type}")
                
                # If it's not boolean, we need to fix it
                if current_type != 'boolean':
                    print("Converting is_read column to boolean...")
                    try:
                        # Add new boolean column
                        conn.execute("ALTER TABLE notifications ADD COLUMN is_read_bool BOOLEAN")
                        
                        # Copy data with proper conversion
                        conn.execute("""
                            UPDATE notifications 
                            SET is_read_bool = CASE 
                                WHEN is_read = 1 THEN TRUE 
                                WHEN is_read = 0 THEN FALSE 
                                ELSE FALSE 
                            END
                        """)
                        
                        # Drop old column
                        conn.execute("ALTER TABLE notifications DROP COLUMN is_read")
                        
                        # Rename new column
                        conn.execute("ALTER TABLE notifications RENAME COLUMN is_read_bool TO is_read")
                        
                        conn.commit()
                        print("✅ Successfully converted is_read column to boolean")
                        
                    except Exception as e:
                        print(f"⚠️  Error during conversion: {e}")
                        conn.rollback()
            else:
                print("is_read column not found, creating it...")
                try:
                    conn.execute("ALTER TABLE notifications ADD COLUMN is_read BOOLEAN DEFAULT FALSE")
                    conn.commit()
                    print("✅ Created is_read column as boolean")
                except Exception as e:
                    print(f"⚠️  Error creating column: {e}")
                    conn.rollback()
        else:
            # For SQLite, boolean is stored as integer, so no conversion needed
            print("SQLite database - no conversion needed")
            
        conn.close()
        print("✅ Database schema fix completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix database schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Starting database schema fix\n")
    
    success = fix_notifications_table()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Database schema fix completed successfully!")
        print("\n✅ Notifications table is now properly configured")
        print("✅ Stock monitoring should work without errors")
    else:
        print("❌ Database schema fix failed")
        print("⚠️  You may still see notification errors in logs")
    
    print("="*50)

if __name__ == "__main__":
    main()