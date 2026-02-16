import requests
import json

# Get customers
response = requests.get('http://localhost:5000/api/customers')
customers = response.json()

if customers:
    customer_id = customers[0]['id']
    customer_name = customers[0]['name']
    print(f"Using customer: {customer_name} (ID: {customer_id})")
    
    # Create a cheque bill
    bill_data = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "payment_method": "cheque",
        "total_amount": 500,
        "subtotal": 500,
        "tax_amount": 0,
        "discount_amount": 0,
        "items": [
            {
                "product_id": "test-product-1",
                "product_name": "Test Product",
                "quantity": 1,
                "unit_price": 500,
                "total_price": 500
            }
        ]
    }
    
    response = requests.post('http://localhost:5000/api/bills', json=bill_data)
    print(f"Bill creation status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Bill created: {result['bill_number']}")
        bill_id = result['bill_id']
        
        # Check if it appears in credit history
        credit_response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
        credit_data = credit_response.json()
        cheque_bills = [b for b in credit_data['bills'] if b['payment_method'] == 'cheque']
        print(f"✅ Found {len(cheque_bills)} cheque bills in credit history")
        for bill in cheque_bills:
            print(f"  - {bill['bill_number']}: {bill['payment_status']} - {bill['is_credit']}")
    else:
        print(f"❌ Bill creation failed: {response.text}")
else:
    print("❌ No customers found")