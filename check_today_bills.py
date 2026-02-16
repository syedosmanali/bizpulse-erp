import requests
import json

# Get credit history
response = requests.get('http://localhost:5000/api/credit/history')
data = response.json()

# Find today's bills
today_bills = []
for bill in data['bills']:
    if '2026-02-10' in bill['created_at']:
        today_bills.append(bill)

print(f"Today's bills ({len(today_bills)}):")
for bill in today_bills:
    print(f"  - {bill['bill_number']}: ₹{bill['total_amount']} ({bill['payment_method']})")
    print(f"    Status: {bill['payment_status']}")
    print(f"    Paid: ₹{bill['paid_amount']}")
    print()