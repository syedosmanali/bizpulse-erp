from datetime import datetime
import sqlite3

print("=" * 80)
print("TESTING TIMESTAMP CREATION")
print("=" * 80)

# Test current timestamp generation
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Current timestamp: {current_time}")

# Test what gets stored in database
conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row

# Create a test bill to see what timestamp gets stored
try:
    test_id = "test-timestamp-" + datetime.now().strftime('%H%M%S')
    test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"About to insert timestamp: {test_time}")
    
    conn.execute('''
        INSERT INTO bills (
            id, bill_number, customer_id, business_type, 
            subtotal, tax_amount, discount_amount, total_amount, 
            status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_id,
        f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        None,
        'retail',
        100.0,
        10.0,
        0.0,
        110.0,
        'completed',
        test_time
    ))
    
    conn.commit()
    
    # Read it back
    result = conn.execute('SELECT created_at FROM bills WHERE id = ?', (test_id,)).fetchone()
    print(f"Retrieved from database: {result['created_at']}")
    
    # Clean up
    conn.execute('DELETE FROM bills WHERE id = ?', (test_id,))
    conn.commit()
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

print("\n" + "=" * 80)
print("SYSTEM TIME INFO")
print("=" * 80)

import time
import os

print(f"System timezone: {time.tzname}")
print(f"Current time (local): {datetime.now()}")
print(f"Current time (UTC): {datetime.utcnow()}")

# Check if there's a TZ environment variable
tz = os.environ.get('TZ', 'Not set')
print(f"TZ environment variable: {tz}")