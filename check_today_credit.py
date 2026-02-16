import requests
import json

# Get today's credit history
response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
data = response.json()

print("Today's credit bills:")
for bill in data['bills']:
    if '2026-02-10' in bill['created_at']:
        print(f"  - {bill['bill_number']}: {bill['payment_method']} - {bill['payment_status']}")
        print(f"    Customer: {bill['customer_name']}")
        print(f"    Amount: ₹{bill['total_amount']}")
        print(f"    Paid: ₹{bill['paid_amount']}")
        print()