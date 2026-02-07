"""
Test bill creation on live site
"""
import requests
import json

# Live site URL
BASE_URL = "https://bizpulse-erp-1.onrender.com"

# Test credentials
EMAIL = "bizpulse.erp@gmail.com"
PASSWORD = "admin123"

def test_bill_creation():
    """Test creating a bill on live site"""
    
    # Step 1: Login
    print("🔐 Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("✅ Login successful")
    
    # Get session cookie
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Step 2: Get products
    print("\n📦 Fetching products...")
    products_response = session.get(f"{BASE_URL}/api/products")
    
    if products_response.status_code != 200:
        print(f"❌ Failed to fetch products: {products_response.status_code}")
        print(products_response.text)
        return
    
    products = products_response.json()
    print(f"✅ Found {len(products)} products")
    
    if len(products) == 0:
        print("⚠️  No products available for billing")
        return
    
    # Step 3: Create a test bill
    print("\n🧾 Creating test bill...")
    
    # Use first 2 products
    test_products = products[:2]
    
    bill_data = {
        "customer_name": "Test Customer",
        "business_type": "retail",
        "items": [
            {
                "product_id": test_products[0]['id'],
                "product_name": test_products[0]['name'],
                "quantity": 1,
                "unit_price": test_products[0]['price'],
                "total_price": test_products[0]['price']
            },
            {
                "product_id": test_products[1]['id'],
                "product_name": test_products[1]['name'],
                "quantity": 2,
                "unit_price": test_products[1]['price'],
                "total_price": test_products[1]['price'] * 2
            }
        ],
        "subtotal": test_products[0]['price'] + (test_products[1]['price'] * 2),
        "tax_amount": (test_products[0]['price'] + (test_products[1]['price'] * 2)) * 0.18,
        "discount_amount": 0,
        "total_amount": (test_products[0]['price'] + (test_products[1]['price'] * 2)) * 1.18,
        "payment_method": "cash"
    }
    
    print(f"Bill data: {json.dumps(bill_data, indent=2)}")
    
    bill_response = session.post(
        f"{BASE_URL}/api/bills",
        json=bill_data
    )
    
    print(f"\n📊 Response status: {bill_response.status_code}")
    print(f"Response: {bill_response.text}")
    
    if bill_response.status_code == 201:
        print("✅ Bill created successfully!")
        result = bill_response.json()
        print(f"Bill Number: {result.get('bill_number')}")
    else:
        print(f"❌ Bill creation failed")

if __name__ == "__main__":
    test_bill_creation()
