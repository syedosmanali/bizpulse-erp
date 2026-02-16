"""
Run this AFTER restarting the server to verify the fix is working
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 80)
print("VERIFYING CHEQUE REVENUE FIX")
print("=" * 80)

# 1. Get dashboard stats
print("\n1. Getting dashboard stats...")
try:
    response = requests.get(f'{BASE_URL}/api/dashboard/stats', timeout=5)
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Dashboard API Response:")
        print(f"   Today's Revenue: ₹{stats.get('today_revenue', 0):.2f}")
        print(f"   Today's Profit: ₹{stats.get('today_profit', 0):.2f}")
        print(f"   Today's Sales: ₹{stats.get('today_sales', 0):.2f}")
        print(f"   Today's Receivable: ₹{stats.get('today_receivable', 0):.2f}")
        
        # Check if revenue is 0 (expected if only uncashed cheques)
        revenue = stats.get('today_revenue', 0)
        if revenue == 0:
            print("\n✅ SUCCESS! Revenue is ₹0 (uncashed cheques excluded)")
        else:
            print(f"\n⚠️  Revenue is ₹{revenue:.2f}")
            print("   This is OK if you have non-cheque bills or cleared cheques today")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Make sure the server is running!")

# 2. Check for cheque bills
print("\n2. Checking cheque bills...")
try:
    response = requests.get(f'{BASE_URL}/api/credit/history?date_range=today', timeout=5)
    if response.status_code == 200:
        data = response.json()
        cheque_bills = [b for b in data.get('bills', []) if b.get('payment_method', '').upper() == 'CHEQUE']
        
        if cheque_bills:
            print(f"✅ Found {len(cheque_bills)} cheque bills:")
            for bill in cheque_bills:
                status = bill['payment_status']
                amount = bill['total_amount']
                print(f"   {bill['bill_number']}: ₹{amount:.2f} | Status: {status}")
                
                if status == 'cheque_deposited':
                    print(f"      → This ₹{amount:.2f} should NOT be in revenue")
                elif status == 'paid':
                    print(f"      → This ₹{amount:.2f} SHOULD be in revenue")
        else:
            print("   No cheque bills found today")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("EXPECTED BEHAVIOR:")
print("- Cheques with status 'cheque_deposited' → NOT in revenue")
print("- Cheques with status 'paid' (cleared) → IN revenue")
print("- Cash/Card/UPI bills → IN revenue")
print("=" * 80)
