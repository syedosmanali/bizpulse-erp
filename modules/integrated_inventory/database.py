"""
Integrated Inventory Database Schema
Handles Product Master, Inventory Control, and Purchase Entry tables
"""

from modules.shared.database import get_db_connection
import sqlite3

def init_integrated_inventory_tables():
    """Initialize all tables for the integrated inventory system"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ensure products table has all required columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                price REAL DEFAULT 0,
                stock INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'piece',
                sku TEXT UNIQUE,
                barcode_data TEXT,
                image_url TEXT,
                is_active INTEGER DEFAULT 1,
                user_id TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                min_stock INTEGER DEFAULT 0,
                max_stock INTEGER DEFAULT 0,
                hsn_code TEXT,
                gst_rate REAL DEFAULT 18,
                mrp REAL DEFAULT 0,
                purchase_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0
            )
        """)
        
        # Add missing columns to existing products table
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN min_stock INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN max_stock INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN hsn_code TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN gst_rate REAL DEFAULT 18")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN mrp REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN purchase_price REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN selling_price REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        # Stock transactions table for detailed tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_transactions (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL, -- 'in' or 'out'
                quantity INTEGER NOT NULL,
                unit_cost REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                reference_type TEXT, -- 'purchase', 'sale', 'adjustment', 'transfer', 'opening'
                reference_id TEXT, -- ID of the related record (purchase_id, sale_id, etc.)
                supplier_name TEXT,
                customer_name TEXT,
                batch_number TEXT,
                expiry_date TEXT,
                location_from TEXT,
                location_to TEXT,
                notes TEXT,
                created_by TEXT NOT NULL,
                business_owner_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Purchase entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_entries (
                id TEXT PRIMARY KEY,
                supplier TEXT,
                total_amount REAL DEFAULT 0,
                total_items INTEGER DEFAULT 0,
                notes TEXT,
                status TEXT DEFAULT 'completed', -- 'draft', 'completed', 'cancelled'
                created_by TEXT NOT NULL,
                business_owner_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Suppliers table for better supplier management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                pincode TEXT,
                gst_number TEXT,
                is_active INTEGER DEFAULT 1,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Product categories table for better category management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                parent_id TEXT,
                is_active INTEGER DEFAULT 1,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES product_categories (id)
            )
        """)
        
        # Stock alerts table for automated notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_alerts (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                alert_type TEXT NOT NULL, -- 'low_stock', 'out_of_stock', 'expiry_soon', 'expired'
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                user_id TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Create indexes for better performance (only if columns exist)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_user_id ON products (user_id)")
        
        # Check if sku column exists before creating index
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'sku' in columns:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku)")
        if 'barcode_data' in columns:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_barcode ON products (barcode_data)")
        if 'category' in columns:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products (category)")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_transactions_product_id ON stock_transactions (product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_transactions_business_owner ON stock_transactions (business_owner_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_transactions_type ON stock_transactions (transaction_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_transactions_reference ON stock_transactions (reference_type, reference_id)")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchase_entries_business_owner ON purchase_entries (business_owner_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_suppliers_user_id ON suppliers (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_user_id ON product_categories (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON stock_alerts (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON stock_alerts (product_id)")
        
        # Insert default categories if they don't exist
        default_categories = [
            ('electronics', 'Electronics & Gadgets'),
            ('clothing', 'Clothing & Fashion'),
            ('food', 'Food & Beverages'),
            ('books', 'Books & Stationery'),
            ('home', 'Home & Garden'),
            ('sports', 'Sports & Fitness'),
            ('health', 'Health & Beauty'),
            ('automotive', 'Automotive'),
            ('toys', 'Toys & Games'),
            ('other', 'Other')
        ]
        
        for cat_id, cat_name in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO product_categories (id, name, is_active, user_id, created_at)
                VALUES (?, ?, 1, 'system', datetime('now'))
            """, (cat_id, cat_name))
        
        conn.commit()
        print("✅ Integrated inventory tables initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing integrated inventory tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_current_stock(product_id, user_id):
    """Get current stock level for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Calculate current stock from transactions
        cursor.execute("""
            SELECT SUM(
                CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END
            ) as current_stock
            FROM stock_transactions
            WHERE product_id = ? AND business_owner_id = ?
        """, (product_id, user_id))
        
        result = cursor.fetchone()
        current_stock = result[0] if result and result[0] is not None else 0
        
        return max(0, current_stock)  # Ensure stock is never negative
        
    except Exception as e:
        print(f"❌ Error getting current stock: {e}")
        return 0
    finally:
        conn.close()

def update_stock_alerts(user_id):
    """Update stock alerts for low stock, out of stock, etc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing alerts for this user
        cursor.execute("DELETE FROM stock_alerts WHERE user_id = ?", (user_id,))
        
        # Get products with stock issues
        cursor.execute("""
            SELECT 
                p.id, p.name, p.min_stock,
                COALESCE(s.current_stock, 0) as current_stock
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
        """, (user_id, user_id))
        
        from modules.shared.database import generate_id
        from datetime import datetime
        
        for row in cursor.fetchall():
            product_id, product_name, min_stock, current_stock = row
            
            alert_id = generate_id()
            now = datetime.now().isoformat()
            
            if current_stock == 0:
                # Out of stock alert
                cursor.execute("""
                    INSERT INTO stock_alerts (id, product_id, alert_type, message, user_id, created_at)
                    VALUES (?, ?, 'out_of_stock', ?, ?, ?)
                """, (alert_id, product_id, f"{product_name} is out of stock", user_id, now))
                
            elif current_stock <= min_stock and min_stock > 0:
                # Low stock alert
                cursor.execute("""
                    INSERT INTO stock_alerts (id, product_id, alert_type, message, user_id, created_at)
                    VALUES (?, ?, 'low_stock', ?, ?, ?)
                """, (alert_id, product_id, f"{product_name} is low on stock ({current_stock} remaining)", user_id, now))
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error updating stock alerts: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_existing_products_to_integrated():
    """Migrate existing products to the integrated inventory system"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all products that don't have stock transactions yet
        cursor.execute("""
            SELECT p.id, p.stock, p.price, p.user_id
            FROM products p
            LEFT JOIN stock_transactions st ON p.id = st.product_id
            WHERE st.product_id IS NULL AND p.is_active = 1
        """)
        
        products_to_migrate = cursor.fetchall()
        
        from modules.shared.database import generate_id
        from datetime import datetime
        
        migrated_count = 0
        
        for product_id, stock, price, user_id in products_to_migrate:
            if stock > 0:
                # Create opening stock transaction
                transaction_id = generate_id()
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO stock_transactions (
                        id, product_id, transaction_type, quantity, unit_cost, total_cost,
                        reference_type, reference_id, notes, created_by, business_owner_id, created_at
                    ) VALUES (?, ?, 'in', ?, ?, ?, 'opening', ?, 'Opening stock migration', ?, ?, ?)
                """, (
                    transaction_id, product_id, stock, price, stock * price,
                    product_id, user_id, user_id, now
                ))
                
                migrated_count += 1
        
        conn.commit()
        print(f"✅ Migrated {migrated_count} products to integrated inventory system")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating products: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    # Initialize tables when run directly
    init_integrated_inventory_tables()
    print("Database initialization completed!")