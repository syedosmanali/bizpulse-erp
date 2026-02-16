import requests
import json
from datetime import datetime

def test_cheque_flow():
    """Test the complete cheque payment flow"""
    print("=== TESTING CHEQUE PAYMENT FLOW ===")
    
    # Test 1: Create a bill with cheque payment
    print("\n1. Creating bill with cheque payment...")
    # First, get an existing customer
    try:
        customer_response = requests.get('http://localhost:5000/api/customers')
        if customer_response.status_code == 200 and customer_response.json():
            customer = customer_response.json()[0]
            customer_id = customer['id']
            customer_name = customer['name']
            print(f"Using customer: {customer_name} (ID: {customer_id})")
        else:
            # Use walk-in customer
            customer_id = "walk-in-customer"
            customer_name = "Walk-in Customer"
            print("Using walk-in customer")
    except Exception as e:
        customer_id = "walk-in-customer"
        customer_name = "Walk-in Customer"
        print(f"Error getting customer, using walk-in: {e}")
    
    # Get an existing product
    try:
        product_response = requests.get('http://localhost:5000/api/products')
        if product_response.status_code == 200 and product_response.json():
            product = product_response.json()[0]
            product_id = product['id']
            product_name = product['name']
            product_price = product['price']
            print(f"Using product: {product_name} (ID: {product_id}, Price: ₹{product_price})")
        else:
            # Use dummy product data
            product_id = "dummy-product-1"
            product_name = "Test Product"
            product_price = 1000
            print("Using dummy product data")
    except Exception as e:
        product_id = "dummy-product-1"
        product_name = "Test Product"
        product_price = 1000
        print(f"Error getting product, using dummy: {e}")
    
    bill_data = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "payment_method": "cheque",
        "total_amount": product_price,
        "subtotal": product_price,
        "tax_amount": 0,
        "discount_amount": 0,
        "items": [
            {
                "product_id": product_id,
                "product_name": product_name,
                "quantity": 1,
                "unit_price": product_price,
                "total_price": product_price
            }
        ]
    }
    
    try:
        response = requests.post('http://localhost:5000/api/bills', json=bill_data)
        print(f"Bill creation status: {response.status_code}")
        if response.status_code == 201:
            bill_result = response.json()
            print(f"✅ Bill created: {bill_result.get('bill_number')}")
            bill_id = bill_result.get('bill_id')
            bill_number = bill_result.get('bill_number')
        else:
            print(f"❌ Bill creation failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating bill: {e}")
        return
    
    # Test 2: Check initial dashboard stats
    print("\n2. Checking initial dashboard stats...")
    try:
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Initial stats:")
            print(f"   Sales: ₹{stats.get('today_sales', 0)}")
            print(f"   Revenue: ₹{stats.get('today_revenue', 0)}")
            print(f"   Orders: {stats.get('today_orders', 0)}")
            print(f"   Profit: ₹{stats.get('today_profit', 0)}")
        else:
            print(f"❌ Failed to get dashboard stats: {response.text}")
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
    
    # Test 3: Check bill status in sales module
    print("\n3. Checking bill status in sales module...")
    try:
        response = requests.get('http://localhost:5000/api/retail/sales')
        if response.status_code == 200:
            sales_data = response.json()
            bill_found = False
            for bill in sales_data.get('bills', []):
                if bill.get('bill_number') == bill_number:
                    print(f"✅ Bill found in sales:")
                    print(f"   Status: {bill.get('status')}")
                    print(f"   Payment Status: {bill.get('payment_status')}")
                    bill_found = True
                    break
            if not bill_found:
                print("❌ Bill not found in sales module")
        else:
            print(f"❌ Failed to get sales data: {response.text}")
    except Exception as e:
        print(f"❌ Error getting sales data: {e}")
    
    # Test 4: Check credit history (should show cheque bill)
    print("\n4. Checking credit history...")
    try:
        response = requests.get('http://localhost:5000/api/credit/history')
        if response.status_code == 200:
            credit_data = response.json()
            bill_found = False
            for bill in credit_data.get('bills', []):
                if bill.get('bill_number') == bill_number:
                    print(f"✅ Bill found in credit history:")
                    print(f"   Status: {bill.get('payment_status')}")
                    print(f"   Paid: ₹{bill.get('paid_amount')}")
                    print(f"   Balance: ₹{bill.get('balance_due')}")
                    bill_found = True
                    break
            if not bill_found:
                print("❌ Bill not found in credit history")
        else:
            print(f"❌ Failed to get credit history: {response.text}")
    except Exception as e:
        print(f"❌ Error getting credit history: {e}")
    
    # Test 5: Mark cheque as cleared
    print("\n5. Marking cheque as cleared...")
    try:
        clear_data = {
            'bill_id': bill_id,
            'action': 'cleared'
        }
        response = requests.post('http://localhost:5000/api/credit/cheque-cleared', json=clear_data)
        print(f"Clear cheque status: {response.status_code}")
        if response.status_code == 200:
            clear_result = response.json()
            print(f"✅ Cheque cleared:")
            print(f"   Message: {clear_result.get('message')}")
            print(f"   New Status: {clear_result.get('new_status')}")
            print(f"   Bill Status: {clear_result.get('bill_status')}")
        else:
            print(f"❌ Failed to clear cheque: {response.text}")
    except Exception as e:
        print(f"❌ Error clearing cheque: {e}")
    
    # Test 6: Check final dashboard stats
    print("\n6. Checking final dashboard stats...")
    try:
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Final stats:")
            print(f"   Sales: ₹{stats.get('today_sales', 0)}")
            print(f"   Revenue: ₹{stats.get('today_revenue', 0)}")
            print(f"   Orders: {stats.get('today_orders', 0)}")
            print(f"   Profit: ₹{stats.get('today_profit', 0)}")
            
            # Verify the logic
            sales = stats.get('today_sales', 0)
            revenue = stats.get('today_revenue', 0)
            if sales >= revenue:
                print("✅ Sales vs Revenue logic is working correctly")
            else:
                print("❌ Sales vs Revenue logic has issues")
        else:
            print(f"❌ Failed to get dashboard stats: {response.text}")
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
    
    # Test 7: Check final bill status
    print("\n7. Checking final bill status...")
    try:
        response = requests.get('http://localhost:5000/api/retail/sales')
        if response.status_code == 200:
            sales_data = response.json()
            for bill in sales_data.get('bills', []):
                if bill.get('bill_number') == bill_number:
                    print(f"✅ Final bill status:")
                    print(f"   Status: {bill.get('status')}")
                    print(f"   Payment Status: {bill.get('payment_status')}")
                    break
        else:
            print(f"❌ Failed to get sales data: {response.text}")
    except Exception as e:
        print(f"❌ Error getting sales data: {e}")

if __name__ == "__main__":
    test_cheque_flow()