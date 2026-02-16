import requests
import json

# Get today's bills
response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
data = response.json()

print("Today's Credit Bills:")
print("=" * 50)
for i, bill in enumerate(data['bills'], 1):
    print(f"{i}. {bill['bill_number']}")
    print(f"   Customer: {bill['customer_name']}")
    print(f"   Status: {bill['payment_status']}")
    print(f"   Paid: ₹{bill['paid_amount']}")
    print(f"   Balance: ₹{bill['balance_due']}")
    print()

# Test the cheque bounced functionality with first cheque bill
cheque_bills = [b for b in data['bills'] if b['payment_status'] == 'cheque_deposited']
if cheque_bills:
    test_bill = cheque_bills[0]
    print(f"Testing bounced functionality on: {test_bill['bill_number']}")
    
    # Test bounced action
    bounce_response = requests.post('http://localhost:5000/api/credit/cheque-cleared', 
                                  json={'bill_id': test_bill['id'], 'action': 'bounced'})
    print("Bounced response:", bounce_response.json())
    
    # Test cleared action  
    clear_response = requests.post('http://localhost:5000/api/credit/cheque-cleared',
                                 json={'bill_id': test_bill['id'], 'action': 'cleared'})
    print("Cleared response:", clear_response.json())
else:
    print("No cheque bills found for testing")