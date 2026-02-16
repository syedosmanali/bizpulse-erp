import requests
import json

print("=== TESTING CREDIT MODULE FIXES ===")
print()

# Test 1: Check payment details endpoint
print("1. Testing Payment Details Endpoint:")
try:
    response = requests.get('http://localhost:5000/api/credit/bill/a52817ba-c434-48fd-b483-99cb18bd992d/payments')
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {data.get('success')}")
    print(f"   Bill Number: {data.get('bill', {}).get('bill_number')}")
    print(f"   Payments Count: {len(data.get('payments', []))}")
    if data.get('payments'):
        print("   Sample Payment:")
        sample_payment = data['payments'][0]
        print(f"     - Amount: ₹{sample_payment['amount']}")
        print(f"     - Method: {sample_payment['method']}")
        print(f"     - Date: {sample_payment['processed_at']}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Check credit history endpoint
print("2. Testing Credit History Endpoint:")
try:
    response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {data.get('success')}")
    print(f"   Bills Count: {len(data.get('bills', []))}")
    for bill in data.get('bills', [])[:2]:
        print(f"   - {bill['bill_number']}: {bill['customer_name']} (₹{bill['paid_amount']}) - {bill['payment_status']}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 3: Test cheque bounced functionality
print("3. Testing Cheque Bounced Functionality:")
try:
    # Find a cheque deposited bill
    history_response = requests.get('http://localhost:5000/api/credit/history?date_range=all')
    history_data = history_response.json()
    
    cheque_bills = [b for b in history_data.get('bills', []) if b['payment_status'] == 'cheque_deposited']
    
    if cheque_bills:
        test_bill = cheque_bills[0]
        print(f"   Testing on bill: {test_bill['bill_number']}")
        
        # Test bounced action
        bounce_response = requests.post('http://localhost:5000/api/credit/cheque-cleared', 
                                      json={'bill_id': test_bill['id'], 'action': 'bounced'})
        bounce_data = bounce_response.json()
        print(f"   Bounced Status: {bounce_response.status_code}")
        print(f"   Bounced Success: {bounce_data.get('success')}")
        print(f"   Bounced Message: {bounce_data.get('message')}")
        print(f"   New Status: {bounce_data.get('new_status')}")
    else:
        print("   No cheque deposited bills found for testing")
except Exception as e:
    print(f"   Error: {e}")

print()
print("=== ALL TESTS COMPLETED ===")