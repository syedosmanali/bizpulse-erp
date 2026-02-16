import requests
import json

# Get credit history
response = requests.get('http://localhost:5000/api/credit/history')
data = response.json()

print("Today's bills (2026-02-10):")
for bill in data['bills']:
    if '2026-02-10' in bill['created_at']:
        print(f"  - {bill['bill_number']}:")
        print(f"    Payment Method: {bill['payment_method']}")
        print(f"    Payment Status: {bill['payment_status']}")
        print(f"    Total Amount: ₹{bill['total_amount']}")
        print(f"    Paid Amount: ₹{bill['paid_amount']}")
        print(f"    Customer: {bill['customer_name']}")
        print()