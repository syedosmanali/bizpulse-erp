"""
Script to fix the deployed server login issues by applying all necessary database schema updates
"""

import os
from modules.shared.database import get_db_connection, get_db_type

def apply_all_fixes():
    """Apply all necessary database fixes for the deployed server"""
    print("🔧 Applying database fixes for deployed server...")
    
    db_type = get_db_type()
    print(f"📊 Database type: {db_type}")
    
    if db_type != 'postgresql':
        print("❌ This script is only for PostgreSQL (deployed server)")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("📝 Adding missing columns to existing tables...")
        
        # Add missing columns to users table
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
        """)
        
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
        """)
        
        # Add missing columns to bills table
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20);
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS credit_paid_amount NUMERIC(10,2) DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE bills 
            ADD COLUMN IF NOT EXISTS credit_balance NUMERIC(10,2) DEFAULT 0;
        """)
        
        # Add missing columns to other tables
        cursor.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS min_stock INTEGER DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """)
        
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS profit_amount NUMERIC(10,2) DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS cost_amount NUMERIC(10,2) DEFAULT 0;
        """)
        
        cursor.execute("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
        """)
        cursor.execute("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS current_balance NUMERIC(10,2) DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS total_purchases NUMERIC(10,2) DEFAULT 0;
        """)
        
        print("✅ Added missing columns to existing tables")
        
        print("📝 Creating missing tables...")
        
        # Create User Management Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                id VARCHAR(255) PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                role_name VARCHAR(100) NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                permissions TEXT NOT NULL DEFAULT '{}',
                is_system_role BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_by VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_id, role_name),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_accounts (
                id VARCHAR(255) PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                mobile VARCHAR(20) NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                temp_password VARCHAR(255),
                role_id VARCHAR(255) NOT NULL,
                department VARCHAR(100),
                status VARCHAR(50) DEFAULT 'active',
                module_permissions TEXT DEFAULT '{}',
                force_password_change BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                created_by VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (role_id) REFERENCES user_roles (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id VARCHAR(255) PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                module VARCHAR(100) NOT NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                ip_address VARCHAR(50),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (user_id) REFERENCES user_accounts (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id VARCHAR(255) PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(50),
                user_agent TEXT,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (user_id) REFERENCES user_accounts (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id VARCHAR(255) PRIMARY KEY,
                bill_id VARCHAR(255) NOT NULL,
                customer_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL, -- 'sale', 'payment', 'adjustment'
                amount NUMERIC(10,2) NOT NULL,
                payment_method VARCHAR(50) DEFAULT 'cash',
                reference_number VARCHAR(255),
                notes TEXT,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills (id),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id VARCHAR(255) PRIMARY KEY,
                product_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL, -- 'sale', 'purchase', 'adjustment'
                quantity_change INTEGER NOT NULL, -- negative for sales, positive for purchases
                bill_id VARCHAR(255),
                reference VARCHAR(255),
                notes TEXT,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (bill_id) REFERENCES bills (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_stats (
                id VARCHAR(255) PRIMARY KEY,
                stat_type VARCHAR(50) NOT NULL, -- 'daily_sales', 'monthly_sales', etc.
                stat_date DATE NOT NULL,
                stat_value NUMERIC(12,2) NOT NULL,
                stat_count INTEGER DEFAULT 0,
                business_owner_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("✅ Created missing tables")
        
        print("📝 Creating indexes for performance...")
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_bills_payment_method ON bills(payment_method);",
            "CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_data);",
            "CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_sales_user_id ON sales(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_credit_transactions_bill_id ON credit_transactions(bill_id);",
            "CREATE INDEX IF NOT EXISTS idx_credit_transactions_customer_id ON credit_transactions(customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_inventory_transactions_product_id ON inventory_transactions(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_inventory_transactions_bill_id ON inventory_transactions(bill_id);",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_stats_business_owner_id ON dashboard_stats(business_owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_stats_stat_date ON dashboard_stats(stat_date);",
            "CREATE INDEX IF NOT EXISTS idx_user_roles_client_id ON user_roles(client_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_accounts_client_id ON user_accounts(client_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_accounts_username ON user_accounts(username);",
            "CREATE INDEX IF NOT EXISTS idx_user_accounts_status ON user_accounts(status);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_log_client_id ON user_activity_log(client_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_log_user_id ON user_activity_log(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_log_timestamp ON user_activity_log(timestamp);"
        ]
        
        for idx_sql in indexes:
            cursor.execute(idx_sql)
        
        print("✅ Created performance indexes")
        
        # Update the default admin user if needed
        cursor.execute("""
            UPDATE users 
            SET business_name = 'BizPulse ERP', 
                business_type = 'software',
                is_active = TRUE
            WHERE email = 'bizpulse.erp@gmail.com'
            AND (business_name IS NULL OR business_name = '');
        """)
        
        print("✅ Updated default admin user")
        
        conn.commit()
        print("🎉 All fixes applied successfully!")
        print("\n💡 Next steps:")
        print("   1. Restart your deployed application")
        print("   2. Test the login functionality")
        print("   3. The login should now work on the deployed server")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting deployed server fix process...")
    apply_all_fixes()