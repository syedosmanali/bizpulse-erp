import requests
import json

# Get credit history
response = requests.get('http://localhost:5000/api/credit/history')
data = response.json()

# Check specific bills
target_bills = ['BILL-20260210-2e9f4ae6', 'BILL-20260210-f1597447']

print("Checking specific bills:")
for bill in data['bills']:
    if bill['bill_number'] in target_bills:
        print(f"  - {bill['bill_number']}:")
        print(f"    Payment Method: {bill['payment_method']}")
        print(f"    Payment Status: {bill['payment_status']}")
        print(f"    Total Amount: ₹{bill['total_amount']}")
        print(f"    Paid Amount: ₹{bill['paid_amount']}")
        print(f"    Created: {bill['created_at']}")
        print()