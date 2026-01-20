"""
Inventory Management Database Schema
Creates tables for comprehensive inventory management
"""

from modules.shared.database import get_db_connection, generate_id
from datetime import datetime

def init_inventory_tables():
    """Initialize all inventory management tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Inventory Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT '📦',
            color TEXT DEFAULT '#732C3F',
            user_id TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES clients(id)
        )
    ''')
    
    # Inventory Items Table (Comprehensive)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            item_type TEXT NOT NULL DEFAULT 'asset',  -- asset, equipment, supply, consumable, tool, furniture, vehicle, etc.
            category_id TEXT,
            serial_number TEXT,
            barcode TEXT,
            quantity INTEGER DEFAULT 1,
            unit TEXT DEFAULT 'piece',
            purchase_price REAL DEFAULT 0.0,
            current_value REAL DEFAULT 0.0,
            location TEXT,
            supplier TEXT,
            purchase_date TEXT,
            warranty_expiry TEXT,
            status TEXT DEFAULT 'active',  -- active, inactive, maintenance, disposed, lost, stolen
            condition TEXT DEFAULT 'good',  -- excellent, good, fair, poor, damaged
            notes TEXT,
            user_id TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES inventory_categories(id),
            FOREIGN KEY (user_id) REFERENCES clients(id)
        )
    ''')
    
    # Inventory Movements Table (Track all changes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            movement_type TEXT NOT NULL,  -- in, out, transfer, adjustment, maintenance, disposal
            quantity INTEGER NOT NULL,
            from_location TEXT,
            to_location TEXT,
            reason TEXT,
            notes TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES inventory_items(id),
            FOREIGN KEY (created_by) REFERENCES clients(id)
        )
    ''')
    
    # Inventory Maintenance Records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_maintenance (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            maintenance_type TEXT NOT NULL,  -- scheduled, repair, inspection, calibration
            description TEXT,
            cost REAL DEFAULT 0.0,
            performed_by TEXT,
            performed_date TEXT,
            next_due_date TEXT,
            status TEXT DEFAULT 'completed',  -- scheduled, in_progress, completed, cancelled
            notes TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES inventory_items(id),
            FOREIGN KEY (created_by) REFERENCES clients(id)
        )
    ''')
    
    # Inventory Locations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            location_type TEXT DEFAULT 'room',  -- room, building, warehouse, vehicle, external
            parent_location_id TEXT,
            address TEXT,
            user_id TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (parent_location_id) REFERENCES inventory_locations(id),
            FOREIGN KEY (user_id) REFERENCES clients(id)
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('default-assets', 'Assets', 'Fixed assets and equipment', '🏢', '#732C3F'),
        ('default-equipment', 'Equipment', 'Machinery and equipment', '⚙️', '#2563EB'),
        ('default-furniture', 'Furniture', 'Office and facility furniture', '🪑', '#059669'),
        ('default-supplies', 'Supplies', 'Office and operational supplies', '📋', '#F59E0B'),
        ('default-tools', 'Tools', 'Hand tools and instruments', '🔧', '#DC2626'),
        ('default-vehicles', 'Vehicles', 'Company vehicles and transport', '🚗', '#7C3AED'),
        ('default-electronics', 'Electronics', 'Computers, phones, and electronics', '💻', '#EC4899'),
        ('default-consumables', 'Consumables', 'Items that are consumed or used up', '🧴', '#10B981'),
        ('default-safety', 'Safety Equipment', 'Safety and security equipment', '🦺', '#EF4444'),
        ('default-maintenance', 'Maintenance', 'Maintenance and repair items', '🔨', '#6B7280')
    ]
    
    for cat_id, name, desc, icon, color in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO inventory_categories 
            (id, name, description, icon, color, user_id, is_default, created_at)
            VALUES (?, ?, ?, ?, ?, NULL, 1, ?)
        ''', (cat_id, name, desc, icon, color, datetime.now().isoformat()))
    
    # Insert default locations
    default_locations = [
        ('default-office', 'Main Office', 'Primary office location', 'building'),
        ('default-warehouse', 'Warehouse', 'Storage and inventory warehouse', 'warehouse'),
        ('default-reception', 'Reception Area', 'Front desk and reception', 'room'),
        ('default-conference', 'Conference Room', 'Meeting and conference room', 'room'),
        ('default-storage', 'Storage Room', 'General storage area', 'room'),
        ('default-parking', 'Parking Area', 'Vehicle parking area', 'external')
    ]
    
    # Note: Default locations will be created per user when they first access inventory
    
    conn.commit()
    conn.close()
    print("✅ Inventory management tables initialized successfully")

def create_sample_inventory_data(user_id):
    """Create sample inventory data for testing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sample inventory items
    sample_items = [
        {
            'name': 'Dell Laptop - Inspiron 15',
            'description': 'Dell Inspiron 15 3000 Series laptop for office work',
            'item_type': 'equipment',
            'category_id': 'default-electronics',
            'serial_number': 'DL123456789',
            'quantity': 1,
            'unit': 'piece',
            'purchase_price': 45000.0,
            'current_value': 35000.0,
            'location': 'Main Office',
            'supplier': 'Dell India',
            'status': 'active',
            'condition': 'good'
        },
        {
            'name': 'Office Chair - Ergonomic',
            'description': 'Ergonomic office chair with lumbar support',
            'item_type': 'furniture',
            'category_id': 'default-furniture',
            'quantity': 5,
            'unit': 'piece',
            'purchase_price': 8000.0,
            'current_value': 6000.0,
            'location': 'Main Office',
            'supplier': 'Office Furniture Co.',
            'status': 'active',
            'condition': 'good'
        },
        {
            'name': 'Printer Paper A4',
            'description': 'A4 size printer paper - 500 sheets per pack',
            'item_type': 'consumable',
            'category_id': 'default-supplies',
            'quantity': 25,
            'unit': 'pack',
            'purchase_price': 300.0,
            'current_value': 300.0,
            'location': 'Storage Room',
            'supplier': 'Stationery Mart',
            'status': 'active',
            'condition': 'excellent'
        },
        {
            'name': 'Fire Extinguisher',
            'description': 'ABC type fire extinguisher - 2kg capacity',
            'item_type': 'safety',
            'category_id': 'default-safety',
            'serial_number': 'FE2024001',
            'quantity': 3,
            'unit': 'piece',
            'purchase_price': 1500.0,
            'current_value': 1200.0,
            'location': 'Various Locations',
            'supplier': 'Safety Equipment Ltd.',
            'status': 'active',
            'condition': 'good'
        }
    ]
    
    for item in sample_items:
        item_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO inventory_items (
                id, name, description, item_type, category_id, serial_number,
                barcode, quantity, unit, purchase_price, current_value,
                location, supplier, purchase_date, warranty_expiry,
                status, condition, notes, user_id, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            item_id, item['name'], item['description'], item['item_type'],
            item['category_id'], item.get('serial_number', ''), '',
            item['quantity'], item['unit'], item['purchase_price'],
            item['current_value'], item['location'], item['supplier'],
            '', '', item['status'], item['condition'], '',
            user_id, now, now
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Sample inventory data created for user {user_id}")

if __name__ == '__main__':
    init_inventory_tables()