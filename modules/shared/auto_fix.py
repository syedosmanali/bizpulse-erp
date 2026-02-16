"""
AUTO-FIX ON STARTUP - Render Deployment
========================================
This script runs automatically when your app starts on Render.
It fixes the business_owner_id issue without manual intervention.

Add this to your app.py startup sequence!
"""

import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

def auto_fix_database_on_startup():
    """
    Automatically fix database issues on Render deployment
    - Adds business_owner_id column if missing
    - Adds customer_phone column to bills table if missing
    Runs once on startup, safe to run multiple times
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if not DATABASE_URL:
            print("DATABASE_URL not found, skipping auto-fix")
            return
        
        logger.info("🔧 Running auto-fix for database...")
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # FIX 1: Check if business_owner_id exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bills' AND column_name = 'business_owner_id'
        """)
        
        column_exists = cursor.fetchone() is not None
        
        if not column_exists:
            logger.info("   Adding business_owner_id columns...")
            
            # Add columns
            tables = ['bills', 'sales', 'products', 'customers', 'bill_items', 'payments']
            for table in tables:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN business_owner_id VARCHAR(255)")
                    logger.info(f"   ✅ Added to {table}")
                except Exception as e:
                    logger.debug(f"   Column may already exist in {table}: {e}")
            
            conn.commit()
        
        # FIX 2: Check if customer_phone exists in bills table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bills' AND column_name = 'customer_phone'
        """)
        
        phone_column_exists = cursor.fetchone() is not None
        
        if not phone_column_exists:
            logger.info("   Adding customer_phone column to bills table...")
            try:
                cursor.execute("ALTER TABLE bills ADD COLUMN customer_phone VARCHAR(20)")
                conn.commit()
                logger.info("   ✅ Added customer_phone column to bills table")
            except Exception as e:
                logger.debug(f"   customer_phone column may already exist: {e}")
        
        # FIX 3: Check if user management tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'user_roles'
        """)
        
        user_tables_exist = cursor.fetchone() is not None
        
        if not user_tables_exist:
            logger.info("   Creating user management tables...")
            try:
                # Create user_roles table
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
                    )
                """)
                
                # Create user_accounts table
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
                    )
                """)
                
                # Create user_activity_log table
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
                    )
                """)
                
                # Create user_sessions table
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
                    )
                """)
                
                conn.commit()
                logger.info("   ✅ Created user management tables")
            except Exception as e:
                logger.debug(f"   User management tables may already exist: {e}")
        
        # Check if backfill is needed
        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE business_owner_id IS NULL")
        null_count = cursor.fetchone()['count']
        
        if null_count > 0:
            logger.info(f"   Backfilling {null_count} bills with NULL business_owner_id...")
            
            # Get first client
            cursor.execute("SELECT id FROM clients ORDER BY created_at LIMIT 1")
            client = cursor.fetchone()
            
            if client:
                client_id = client['id']
                
                # Backfill
                cursor.execute("""
                    UPDATE bills 
                    SET business_owner_id = %s 
                    WHERE business_owner_id IS NULL
                """, (client_id,))
                bills_updated = cursor.rowcount
                
                cursor.execute("""
                    UPDATE sales 
                    SET business_owner_id = %s 
                    WHERE business_owner_id IS NULL
                """, (client_id,))
                sales_updated = cursor.rowcount
                
                cursor.execute("""
                    UPDATE products 
                    SET business_owner_id = %s 
                    WHERE business_owner_id IS NULL
                """, (client_id,))
                products_updated = cursor.rowcount
                
                cursor.execute("""
                    UPDATE customers 
                    SET business_owner_id = %s 
                    WHERE business_owner_id IS NULL
                """, (client_id,))
                customers_updated = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"   ✅ Updated {bills_updated} bills, {sales_updated} sales, "
                          f"{products_updated} products, {customers_updated} customers")
            else:
                logger.warning("   No clients found, skipping backfill")
        
        # Create indexes if not exist
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id 
                ON bills(business_owner_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id 
                ON sales(business_owner_id)
            """)
            conn.commit()
            logger.info("   ✅ Indexes created")
        except Exception as e:
            logger.debug(f"   Indexes may already exist: {e}")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Auto-fix completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Auto-fix failed: {e}")
        import traceback
        traceback.print_exc()

# Export for use in app.py
__all__ = ['auto_fix_database_on_startup']
