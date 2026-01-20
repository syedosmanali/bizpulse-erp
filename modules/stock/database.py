"""
Stock Management Database Schema
Transaction-based stock tracking system
"""

from modules.shared.database import get_db_connection, generate_id
from datetime import datetime

def init_stock_tables():
    """Initialize stock management tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Stock Transactions Table - Records every stock movement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_transactions (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,  -- 'IN', 'OUT', 'ADJUSTMENT'
            quantity INTEGER NOT NULL,       -- Positive for IN, Negative for OUT
            reference_type TEXT,             -- 'sale', 'purchase', 'adjustment', 'opening'
            reference_id TEXT,               -- bill_id, purchase_id, etc.
            notes TEXT,
            created_by TEXT,                 -- user_id who made the transaction
            business_owner_id TEXT,          -- for multi-tenant isolation
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Current Stock View Table - For fast stock lookups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_stock (
            product_id TEXT PRIMARY KEY,
            current_quantity INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            business_owner_id TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Purchase Orders Table - For stock replenishment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id TEXT PRIMARY KEY,
            po_number TEXT UNIQUE,
            supplier_name TEXT,
            supplier_contact TEXT,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',   -- 'pending', 'received', 'cancelled'
            business_owner_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            received_at TIMESTAMP
        )
    ''')
    
    # Purchase Order Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            id TEXT PRIMARY KEY,
            po_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT,
            quantity INTEGER NOT NULL,
            unit_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            received_quantity INTEGER DEFAULT 0,
            FOREIGN KEY (po_id) REFERENCES purchase_orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Stock Adjustments Table - For damage, corrections, etc.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_adjustments (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            adjustment_type TEXT NOT NULL,   -- 'damage', 'expired', 'correction', 'found'
            old_quantity INTEGER,
            new_quantity INTEGER,
            difference INTEGER,              -- calculated: new - old
            reason TEXT,
            notes TEXT,
            created_by TEXT,
            business_owner_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Stock management tables created successfully")

def migrate_existing_stock_data():
    """Migrate existing products.stock to stock_transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔄 Starting stock data migration...")
    
    # Get all products with stock > 0
    cursor.execute("SELECT id, name, stock, user_id FROM products WHERE stock > 0 AND is_active = 1")
    products_with_stock = cursor.fetchall()
    
    migration_count = 0
    
    for product in products_with_stock:
        product_id = product[0]
        product_name = product[1]
        current_stock = product[2]
        user_id = product[3]
        
        if current_stock > 0:
            # Create opening stock transaction
            transaction_id = generate_id()
            cursor.execute("""
                INSERT INTO stock_transactions (
                    id, product_id, transaction_type, quantity, 
                    reference_type, notes, created_by, business_owner_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                product_id,
                'IN',
                current_stock,
                'opening',
                f'Opening stock for {product_name}',
                user_id,
                user_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # Update current_stock table
            cursor.execute("""
                INSERT OR REPLACE INTO current_stock (
                    product_id, current_quantity, business_owner_id, last_updated
                ) VALUES (?, ?, ?, ?)
            """, (
                product_id,
                current_stock,
                user_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            migration_count += 1
            print(f"✅ Migrated {product_name}: {current_stock} units")
    
    conn.commit()
    conn.close()
    
    print(f"🎉 Migration completed! {migration_count} products migrated")
    return migration_count

def get_current_stock(product_id, business_owner_id=None):
    """Get current stock for a product"""
    conn = get_db_connection()
    
    # Try to get from current_stock table first (faster)
    if business_owner_id:
        result = conn.execute("""
            SELECT current_quantity FROM current_stock 
            WHERE product_id = ? AND business_owner_id = ?
        """, (product_id, business_owner_id)).fetchone()
    else:
        result = conn.execute("""
            SELECT current_quantity FROM current_stock 
            WHERE product_id = ?
        """, (product_id,)).fetchone()
    
    if result:
        conn.close()
        return result[0]
    
    # Fallback: Calculate from transactions
    if business_owner_id:
        result = conn.execute("""
            SELECT COALESCE(SUM(quantity), 0) as current_stock
            FROM stock_transactions 
            WHERE product_id = ? AND business_owner_id = ? AND is_active = 1
        """, (product_id, business_owner_id)).fetchone()
    else:
        result = conn.execute("""
            SELECT COALESCE(SUM(quantity), 0) as current_stock
            FROM stock_transactions 
            WHERE product_id = ? AND is_active = 1
        """, (product_id,)).fetchone()
    
    current_stock = result[0] if result else 0
    conn.close()
    return current_stock

def update_current_stock(product_id, business_owner_id):
    """Recalculate and update current stock for a product"""
    conn = get_db_connection()
    
    # Calculate current stock from all transactions
    result = conn.execute("""
        SELECT COALESCE(SUM(quantity), 0) as total_stock
        FROM stock_transactions 
        WHERE product_id = ? AND business_owner_id = ? AND is_active = 1
    """, (product_id, business_owner_id)).fetchone()
    
    current_stock = result[0] if result else 0
    
    # Update current_stock table
    conn.execute("""
        INSERT OR REPLACE INTO current_stock (
            product_id, current_quantity, business_owner_id, last_updated
        ) VALUES (?, ?, ?, ?)
    """, (
        product_id,
        current_stock,
        business_owner_id,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    conn.close()
    return current_stock