"""
Test Credit Billing API - Verify it works end-to-end
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

print("="*60)
print("TESTING CREDIT & PARTIAL PAYMENT BILLING")
print("="*60)

# Test 1: Create a Credit Bill
print("\n1️⃣ Testing CREDIT bill creation...")
credit_bill_data = {
    "customer_name": "Test Credit Customer",
    "customer_phone": "9876543210",
    "items": [
        {
            "product_id": "test-product-1",
            "product_name": "Test Product",
            "quantity": 2,
            "unit_price": 100,
            "total_price": 200
        }
    ],
    "subtotal": 200,
    "tax_amount": 36,
    "total_amount": 236,
    "payment_method": "credit",
    "payment_status": "unpaid",
    "is_credit": True,
    "credit_amount": 236,
    "credit_balance": 236
}

try:
    response = requests.post(
        f"{BASE_URL}/api/bills",
        json=credit_bill_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Credit bill created successfully!")
            print(f"   Bill Number: {result.get('bill_number')}")
            print(f"   Bill ID: {result.get('bill_id')}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    else:
        print(f"   ❌ HTTP Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

# Test 2: Create a Partial Payment Bill
print("\n2️⃣ Testing PARTIAL PAYMENT bill creation...")
partial_bill_data = {
    "customer_name": "Test Partial Customer",
    "customer_phone": "9876543211",
    "items": [
        {
            "product_id": "test-product-2",
            "product_name": "Test Product 2",
            "quantity": 1,
            "unit_price": 500,
            "total_price": 500
        }
    ],
    "subtotal": 500,
    "tax_amount": 90,
    "total_amount": 590,
    "payment_method": "partial",
    "payment_status": "partial",
    "partial_amount": 300,
    "partial_payment_method": "cash"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/bills",
        json=partial_bill_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Partial payment bill created successfully!")
            print(f"   Bill Number: {result.get('bill_number')}")
            print(f"   Bill ID: {result.get('bill_id')}")
            print(f"   Paid: ₹{partial_bill_data['partial_amount']}")
            print(f"   Balance: ₹{partial_bill_data['total_amount'] - partial_bill_data['partial_amount']}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    else:
        print(f"   ❌ HTTP Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

# Test 3: Create a Cheque Payment Bill
print("\n3️⃣ Testing CHEQUE PAYMENT bill creation...")
cheque_bill_data = {
    "customer_name": "Test Cheque Customer",
    "customer_phone": "9876543212",
    "items": [
        {
            "product_id": "test-product-3",
            "product_name": "Test Product 3",
            "quantity": 3,
            "unit_price": 150,
            "total_price": 450
        }
    ],
    "subtotal": 450,
    "tax_amount": 81,
    "total_amount": 531,
    "payment_method": "cheque",
    "payment_status": "cheque_deposited",
    "cheque_number": "CHQ123456",
    "cheque_date": datetime.now().strftime('%Y-%m-%d'),
    "cheque_bank": "Test Bank"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/bills",
        json=cheque_bill_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Cheque payment bill created successfully!")
            print(f"   Bill Number: {result.get('bill_number')}")
            print(f"   Bill ID: {result.get('bill_id')}")
            print(f"   Cheque Number: {cheque_bill_data['cheque_number']}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    else:
        print(f"   ❌ HTTP Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("If all tests passed, credit and partial payment billing is working!")
print("\nTest on production:")
print("https://bizpulse24.com/retail/billing")
print("="*60)
