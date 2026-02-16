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
    Automatically fix business_owner_id issue on Render deployment
    Runs once on startup, safe to run multiple times
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if not DATABASE_URL:
            print("DATABASE_URL not found, skipping auto-fix")
            return
        
        logger.info("🔧 Running auto-fix for business_owner_id...")
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if fix is needed
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
