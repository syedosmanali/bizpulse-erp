import requests
import json

# Get credit history
response = requests.get('http://localhost:5000/api/credit/history')
data = response.json()

# Find payments from today
payments_today = []
for bill in data['bills']:
    last_payment_date = bill.get('last_payment_date', '')
    if '2026-02-10' in (last_payment_date or ''):
        payments_today.append(bill)

print(f"Payments today ({len(payments_today)}):")
for bill in payments_today:
    print(f"  - {bill['bill_number']}: ₹{bill['paid_amount']} on {bill['last_payment_date']}")