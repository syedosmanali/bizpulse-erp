import requests
import json

# Test creating a cheque bill without customer details (should fail)
print("Testing cheque payment without customer details...")

bill_data = {
    "customer_id": None,
    "customer_name": "Walk-in Customer",  # This should trigger validation
    "customer_phone": None,
    "payment_method": "cheque",
    "total_amount": 1000,
    "subtotal": 1000,
    "tax_amount": 0,
    "discount_amount": 0,
    "items": [
        {
            "product_id": "test-product-1",
            "product_name": "Test Product",
            "quantity": 1,
            "unit_price": 1000,
            "total_price": 1000
        }
    ]
}

try:
    response = requests.post('http://localhost:5000/api/bills', json=bill_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        error_data = response.json()
        print(f"✅ Validation working correctly: {error_data.get('error', 'Validation error')}")
    else:
        print(f"❌ Unexpected response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test creating a cheque bill WITH customer details (should succeed)
print("Testing cheque payment WITH customer details...")

# First get a customer
try:
    customer_response = requests.get('http://localhost:5000/api/customers')
    customers = customer_response.json()
    
    if customers:
        customer = customers[0]
        customer_id = customer['id']
        customer_name = customer['name']
        customer_phone = customer.get('phone', '9876543210')
        
        print(f"Using customer: {customer_name} (ID: {customer_id})")
        
        bill_data_with_customer = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "payment_method": "cheque",
            "total_amount": 1000,
            "subtotal": 1000,
            "tax_amount": 0,
            "discount_amount": 0,
            "items": [
                {
                    "product_id": "test-product-1",
                    "product_name": "Test Product",
                    "quantity": 1,
                    "unit_price": 1000,
                    "total_price": 1000
                }
            ]
        }
        
        response = requests.post('http://localhost:5000/api/bills', json=bill_data_with_customer)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Cheque bill created successfully: {result.get('bill_number', 'N/A')}")
        else:
            print(f"❌ Failed to create cheque bill: {response.text}")
    else:
        print("❌ No customers found in database")
        
except Exception as e:
    print(f"Error: {e}")