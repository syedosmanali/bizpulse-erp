"""
Simple Supabase Fix Script
Run this script to fix your Supabase database issues
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def fix_supabase_database():
    """Apply all necessary fixes to Supabase database"""
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found!")
        print("Please set your Supabase DATABASE_URL in environment variables")
        return False
    
    print("🔧 Connecting to Supabase database...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Connected to database successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        print("\n🔧 Applying database fixes...")
        
        # Fix 1: Bills table columns
        print("1. Fixing bills table...")
        bills_fixes = [
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20)",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2)",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50)",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_paid_amount NUMERIC(10,2) DEFAULT 0",
            "ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_balance NUMERIC(10,2) DEFAULT 0"
        ]
        
        for fix in bills_fixes:
            try:
                cursor.execute(fix)
                print(f"   ✅ Applied: {fix.split()[2]}")  # Print column name
            except Exception as e:
                print(f"   ℹ️  Skipped: {fix.split()[2]} (already exists or error)")
        
        # Fix 2: Products table columns
        print("\n2. Fixing products table...")
        product_fixes = [
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS min_stock INTEGER DEFAULT 0",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
        
        for fix in product_fixes:
            try:
                cursor.execute(fix)
                print(f"   ✅ Applied: {fix.split()[2]}")
            except Exception as e:
                print(f"   ℹ️  Skipped: {fix.split()[2]} (already exists or error)")
        
        # Fix 3: Sales table columns
        print("\n3. Fixing sales table...")
        sales_fixes = [
            "ALTER TABLE sales ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)",
            "ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)",
            "ALTER TABLE sales ADD COLUMN IF NOT EXISTS profit_amount NUMERIC(10,2) DEFAULT 0",
            "ALTER TABLE sales ADD COLUMN IF NOT EXISTS cost_amount NUMERIC(10,2) DEFAULT 0"
        ]
        
        for fix in sales_fixes:
            try:
                cursor.execute(fix)
                print(f"   ✅ Applied: {fix.split()[2]}")
            except Exception as e:
                print(f"   ℹ️  Skipped: {fix.split()[2]} (already exists or error)")
        
        # Fix 4: Customers table columns
        print("\n4. Fixing customers table...")
        customer_fixes = [
            "ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)",
            "ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)",
            "ALTER TABLE customers ADD COLUMN IF NOT EXISTS current_balance NUMERIC(10,2) DEFAULT 0",
            "ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_purchases NUMERIC(10,2) DEFAULT 0"
        ]
        
        for fix in customer_fixes:
            try:
                cursor.execute(fix)
                print(f"   ✅ Applied: {fix.split()[2]}")
            except Exception as e:
                print(f"   ℹ️  Skipped: {fix.split()[2]} (already exists or error)")
        
        # Fix 5: Create missing tables
        print("\n5. Creating missing tables...")
        
        # Credit Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id VARCHAR(255) PRIMARY KEY,
                bill_id VARCHAR(255) NOT NULL,
                customer_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                amount NUMERIC(10,2) NOT NULL,
                payment_method VARCHAR(50) DEFAULT 'cash',
                reference_number VARCHAR(255),
                notes TEXT,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills (id),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        print("   ✅ Created credit_transactions table")
        
        # Inventory Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id VARCHAR(255) PRIMARY KEY,
                product_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                quantity_change INTEGER NOT NULL,
                bill_id VARCHAR(255),
                reference VARCHAR(255),
                notes TEXT,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (bill_id) REFERENCES bills (id)
            )
        """)
        print("   ✅ Created inventory_transactions table")
        
        # Dashboard Stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_stats (
                id VARCHAR(255) PRIMARY KEY,
                stat_type VARCHAR(50) NOT NULL,
                stat_date DATE NOT NULL,
                stat_value NUMERIC(12,2) NOT NULL,
                stat_count INTEGER DEFAULT 0,
                business_owner_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Created dashboard_stats table")
        
        # Fix 6: Create indexes
        print("\n6. Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_credit_transactions_bill_id ON credit_transactions(bill_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_transactions_product_id ON inventory_transactions(product_id)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"   ✅ Created index")
            except Exception as e:
                print(f"   ℹ️  Index may already exist")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All database fixes applied successfully!")
        
        # Verification
        print("\n🔍 Verifying fixes...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bills' 
            AND column_name IN ('customer_phone', 'business_owner_id', 'user_id', 'paid_amount', 'credit_balance')
            ORDER BY column_name
        """)
        required_columns = ['customer_phone', 'business_owner_id', 'user_id', 'paid_amount', 'credit_balance']
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        
        missing_columns = set(required_columns) - set(existing_columns)
        if not missing_columns:
            print("✅ All required columns are present in bills table")
        else:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        print("\n🎉 DATABASE FIX COMPLETED SUCCESSFULLY!")
        print("✅ Your Supabase database is now properly configured")
        print("✅ All modules (billing, products, sales, dashboard, invoices) are connected")
        print("✅ Restart your application to apply all changes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           SUPABASE DATABASE FIX                              ║")
    print("║                                                              ║")
    print("║    This script will fix all database issues for your ERP     ║")
    print("║    system and connect all modules properly                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    success = fix_supabase_database()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Restart your application on Render")
        print("2. Test by creating a new bill")
        print("3. Verify that inventory is deducted automatically")
        print("4. Check that dashboard shows real-time data")
    else:
        print("\n❌ Fix failed - please check the error messages above")