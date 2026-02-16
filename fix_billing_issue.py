"""
Fix for the billing issue: "table bills has no column named customer_phone"

This script ensures the customer_phone column exists in the bills table
and provides a comprehensive fix for the billing system.
"""

from modules.shared.database import get_db_connection, get_db_type

def fix_bills_table():
    """
    Comprehensive fix for bills table structure
    Ensures customer_phone column exists for both SQLite and PostgreSQL
    """
    conn = get_db_connection()
    db_type = get_db_type()
    
    print(f"🔧 Fixing bills table for {db_type} database...")
    
    try:
        # Check if customer_phone column exists
        if db_type == 'postgresql':
            # For PostgreSQL, check information_schema
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bills' AND column_name = 'customer_phone'
            """).fetchone()
            column_exists = result is not None
        else:
            # For SQLite, use PRAGMA
            result = conn.execute("PRAGMA table_info(bills)").fetchall()
            column_exists = any(col[1] == 'customer_phone' for col in result)
        
        if not column_exists:
            print("   Adding customer_phone column to bills table...")
            
            if db_type == 'postgresql':
                conn.execute("ALTER TABLE bills ADD COLUMN customer_phone VARCHAR(20)")
            else:
                conn.execute("ALTER TABLE bills ADD COLUMN customer_phone TEXT")
            
            conn.commit()
            print("   ✅ Successfully added customer_phone column")
        else:
            print("   ℹ️  customer_phone column already exists")
        
        # Also ensure customer_name column exists (sometimes related)
        if db_type == 'postgresql':
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bills' AND column_name = 'customer_name'
            """).fetchone()
            customer_name_exists = result is not None
        else:
            result = conn.execute("PRAGMA table_info(bills)").fetchall()
            customer_name_exists = any(col[1] == 'customer_name' for col in result)
        
        if not customer_name_exists:
            print("   Adding customer_name column to bills table...")
            
            if db_type == 'postgresql':
                conn.execute("ALTER TABLE bills ADD COLUMN customer_name VARCHAR(255)")
            else:
                conn.execute("ALTER TABLE bills ADD COLUMN customer_name TEXT")
            
            conn.commit()
            print("   ✅ Successfully added customer_name column")
        else:
            print("   ℹ️  customer_name column already exists")
        
        print("✅ Bills table structure fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing bills table: {e}")
        conn.rollback()
    finally:
        conn.close()


def verify_fix():
    """
    Verify that the fix was applied correctly
    """
    conn = get_db_connection()
    db_type = get_db_type()
    
    try:
        print(f"\n🔍 Verifying bills table structure for {db_type}...")
        
        if db_type == 'postgresql':
            # For PostgreSQL, use information_schema
            result = conn.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'bills'
                ORDER BY ordinal_position
            """).fetchall()
        else:
            # For SQLite, use PRAGMA
            result = conn.execute("PRAGMA table_info(bills)").fetchall()
        
        print("   Bills table columns:")
        for col in result:
            if db_type == 'postgresql':
                print(f"     {col[0]} ({col[1]}) - nullable: {col[2]}, default: {col[3]}")
            else:
                print(f"     {col[1]} ({col[2]}) - not_null: {col[3]}, default: {col[4]}")
        
        # Check specifically for our target columns
        if db_type == 'postgresql':
            has_customer_phone = any(col[0] == 'customer_phone' for col in result)
            has_customer_name = any(col[0] == 'customer_name' for col in result)
        else:
            has_customer_phone = any(col[1] == 'customer_phone' for col in result)
            has_customer_name = any(col[1] == 'customer_name' for col in result)
        
        if has_customer_phone and has_customer_name:
            print("\n✅ Verification successful!")
            print("✅ customer_phone column exists in bills table")
            print("✅ customer_name column exists in bills table")
            print("\n🎉 Billing system should now work correctly!")
            return True
        else:
            print("\n❌ Verification failed!")
            if not has_customer_phone:
                print("❌ customer_phone column is missing")
            if not has_customer_name:
                print("❌ customer_name column is missing")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        conn.close()


def main():
    """
    Main function to run the billing fix
    """
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                  BILLING FIX SCRIPT                          ║")
    print("║                                                              ║")
    print("║    Fixes: 'table bills has no column named customer_phone'   ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Apply the fix
    fix_bills_table()
    
    # Verify the fix
    success = verify_fix()
    
    print()
    if success:
        print("🎉 SUCCESS: Billing issue has been fixed!")
        print("📝 The customer_phone column has been added to the bills table")
        print("🚀 You can now create bills without encountering the error")
    else:
        print("❌ FAILURE: Could not fix the billing issue")
        print("🔧 Please check the error messages above and try again")
    
    print()
    print("💡 TIP: Restart your application to ensure all changes take effect")


if __name__ == "__main__":
    main()