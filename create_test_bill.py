from services.billing_service import BillingService
from datetime import datetime

print("=" * 80)
print("CREATING TEST BILL")
print("=" * 80)

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Current time: {current_time}")

billing_service = BillingService()

# Create a test bill
test_bill_data = {
    'customer_id': None,
    'business_type': 'retail',
    'subtotal': 100.0,
    'tax_amount': 10.0,
    'discount_amount': 0.0,
    'total_amount': 110.0,
    'payment_method': 'cash',
    'items': [
        {
            'product_id': '8f962389-18e5-40a9-8e02-bcad96704be4',
            'product_name': 'Basmati Rice Premium 5kg',
            'quantity': 1,
            'unit_price': 100.0
        }
    ]
}

print("Creating bill...")
success, result = billing_service.create_bill(test_bill_data)

if success:
    print(f"✅ Bill created successfully!")
    print(f"Bill ID: {result['bill_id']}")
    print(f"Bill Number: {result['bill_number']}")
    print(f"Created At: {result['created_at']}")
    
    # Now check what's in the database
    import sqlite3
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    
    bill = conn.execute('SELECT * FROM bills WHERE id = ?', (result['bill_id'],)).fetchone()
    sales = conn.execute('SELECT * FROM sales WHERE bill_id = ?', (result['bill_id'],)).fetchall()
    
    print(f"\n📊 Database Records:")
    print(f"Bill created_at: {bill['created_at']}")
    if sales:
        print(f"Sales created_at: {sales[0]['created_at']}")
        print(f"Sales sale_date: {sales[0]['sale_date']}")
        print(f"Sales sale_time: {sales[0]['sale_time']}")
    
    conn.close()
else:
    print(f"❌ Failed to create bill: {result}")