import sqlite3
import uuid
from datetime import datetime

print("=" * 60)
print("TESTING SALES INSERT - Exact Error Check")
print("=" * 60)

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Test data
bill_id = str(uuid.uuid4())
timestamp = datetime.now()
bill_number = f'TEST-{timestamp.strftime("%Y%m%d%H%M%S")}'

print(f"\n1. Creating test bill: {bill_number}")

try:
    # Create bill
    cursor.execute('''
        INSERT INTO bills (id, bill_number, business_type, subtotal, tax_amount, 
                         discount_amount, total_amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        bill_id, bill_number, 'retail', 100.0, 18.0, 0.0, 118.0, 'completed', timestamp
    ))
    print("   ✅ Bill created")
    
    # Create bill item
    item_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO bill_items (id, bill_id, product_id, product_name, quantity, 
                              unit_price, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        item_id, bill_id, 'prod-1', 'Test Product', 1, 100.0, 100.0
    ))
    print("   ✅ Bill item created")
    
    # Get product category
    print("\n2. Fetching product category...")
    product_data = cursor.execute(
        'SELECT category FROM products WHERE id = ?', 
        ('prod-1',)
    ).fetchone()
    category = product_data[0] if product_data else 'General'
    print(f"   Category: {category}")
    
    # Create sales record - EXACT SAME AS API
    print("\n3. Creating sales record...")
    sale_id = str(uuid.uuid4())
    
    print("   Columns to insert:")
    columns = ['id', 'bill_id', 'bill_number', 'customer_id', 'customer_name',
               'product_id', 'product_name', 'category', 'quantity', 'unit_price',
               'total_price', 'tax_amount', 'discount_amount', 'payment_method',
               'sale_date', 'sale_time', 'created_at']
    print(f"   {', '.join(columns)}")
    
    values = (
        sale_id,
        bill_id,
        bill_number,
        None,
        'Walk-in Customer',
        'prod-1',
        'Test Product',
        category,
        1,
        100.0,
        100.0,
        18.0,
        0,
        'cash',
        timestamp.strftime('%Y-%m-%d'),  # Convert to string
        timestamp.strftime('%H:%M:%S'),  # Convert to string
        timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Convert to string
    )
    
    print(f"\n   Values count: {len(values)}")
    print(f"   Columns count: {len(columns)}")
    
    cursor.execute('''
        INSERT INTO sales (id, bill_id, bill_number, customer_id, customer_name,
                         product_id, product_name, category, quantity, unit_price, 
                         total_price, tax_amount, discount_amount, payment_method,
                         sale_date, sale_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)
    
    print("   ✅ Sales record created successfully!")
    
    # Rollback (don't save test data)
    conn.rollback()
    print("\n✅ ALL TESTS PASSED - Test data rolled back")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    conn.rollback()

conn.close()
print("\n" + "=" * 60)
