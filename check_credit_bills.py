import requests

# Get today's sales data
r = requests.get('http://localhost:5000/api/sales/all?filter=today')
data = r.json()
sales = data.get('sales', [])

print("Today's Bills Analysis:")
print("=" * 50)

for i, s in enumerate(sales):
    bill_num = s.get('bill_number', 'N/A')
    is_credit = s.get('is_credit', False)
    credit_balance = s.get('credit_balance', 0)
    
    # Handle string credit_balance
    if isinstance(credit_balance, str):
        try:
            credit_balance = float(credit_balance) if credit_balance else 0
        except:
            credit_balance = 0
    
    print(f"Bill {i+1}: {bill_num}")
    print(f"  Is Credit: {is_credit}")
    print(f"  Credit Balance: {credit_balance}")
    print(f"  Type: {type(credit_balance)}")
    print()

# Count summary
total_bills = len(sales)
credit_bills = len([s for s in sales if s.get('is_credit')])
pending_bills = len([s for s in sales if s.get('is_credit') and (float(s.get('credit_balance', 0)) if isinstance(s.get('credit_balance', 0), str) else s.get('credit_balance', 0)) > 0])

print(f"Summary:")
print(f"  Total bills today: {total_bills}")
print(f"  Credit bills today: {credit_bills}")
print(f"  Credit bills with pending balance: {pending_bills}")