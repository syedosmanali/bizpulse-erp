"""
Migration script to add new fields to products table:
- supplier
- description
- image_url
- expiry_date
- bill_receipt_photo
- last_stock_update
"""

import sqlite3
from datetime import datetime

def migrate_products_table():
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    # Add supplier field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN supplier TEXT')
        print('✅ Added supplier column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ supplier column: {e}')
    
    # Add description field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN description TEXT')
        print('✅ Added description column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ description column: {e}')
    
    # Add image_url field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN image_url TEXT')
        print('✅ Added image_url column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ image_url column: {e}')
    
    # Add expiry_date field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN expiry_date DATE')
        print('✅ Added expiry_date column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ expiry_date column: {e}')
    
    # Add bill_receipt_photo field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN bill_receipt_photo TEXT')
        print('✅ Added bill_receipt_photo column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ bill_receipt_photo column: {e}')
    
    # Add last_stock_update field
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN last_stock_update TIMESTAMP')
        print('✅ Added last_stock_update column')
    except sqlite3.OperationalError as e:
        print(f'⚠️ last_stock_update column: {e}')
    
    conn.commit()
    
    # Verify the changes
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print('\n📋 Current products table structure:')
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')
    
    conn.close()
    print('\n✅ Migration completed successfully!')

if __name__ == '__main__':
    migrate_products_table()
