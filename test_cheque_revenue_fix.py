"""
Test script to verify that uncashed cheques don't show in revenue/profit
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 80)
print("Testing Cheque Revenue Fix")
print("=" * 80)

# 1. Get current dashboard stats
print("\n1. Checking dashboard stats...")
response = requests.get(f'{BASE_URL}/api/dashboard/stats')
if response.status_code == 200:
    stats = response.json()
    print(f"✅ Dashboard Stats Retrieved:")
    print(f"   Today's Revenue: ₹{stats.get('today_revenue', 0):.2f}")
    print(f"   Today's Profit: ₹{stats.get('today_profit', 0):.2f}")
    print(f"   Today's Sales: ₹{stats.get('today_sales', 0):.2f}")
    print(f"   Today's Receivable: ₹{stats.get('today_receivable', 0):.2f}")
else:
    print(f"❌ Failed to get dashboard stats: {response.status_code}")
    print(response.text)

# 2. Check for cheque bills
print("\n2. Checking for cheque bills...")
response = requests.get(f'{BASE_URL}/api/credit/history?date_range=today')
if response.status_code == 200:
    data = response.json()
    cheque_bills = [b for b in data.get('bills', []) if b.get('payment_method', '').upper() == 'CHEQUE']
    print(f"✅ Found {len(cheque_bills)} cheque bills today")
    
    for bill in cheque_bills:
        print(f"\n   Bill: {bill['bill_number']}")
        print(f"   Status: {bill['payment_status']}")
        print(f"   Amount: ₹{bill['total_amount']:.2f}")
        print(f"   Balance: ₹{bill.get('credit_balance', 0):.2f}")
else:
    print(f"❌ Failed to get credit history: {response.status_code}")

print("\n" + "=" * 80)
print("EXPECTED BEHAVIOR:")
print("- Revenue should be ₹0 if all bills are cheque with status 'cheque_deposited'")
print("- Profit should be ₹0 if all bills are cheque with status 'cheque_deposited'")
print("- Sales can show the total amount (includes credit)")
print("- Receivable should show the pending cheque amount")
print("=" * 80)
