"""
Test bill creation and verify sales data is stored
"""
import requests
import time

BASE_URL = "https://bizpulse-erp-1.onrender.com"
EMAIL = "bizpulse.erp@gmail.com"
PASSWORD = "admin123"

def test_bill_and_sales():
    """Test bill creation and sales data"""
    
    # Login
    print("🔐 Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Get products
    print("\n📦 Fetching products...")
    products_response = session.get(f"{BASE_URL}/api/products")
    products = products_response.json()
    print(f"✅ Found {len(products)} products")
    
    if len(products) < 2:
        print("⚠️  Not enough products")
        return
    
    # Get sales count before
    print("\n📊 Checking sales before bill creation...")
    sales_before_response = session.get(f"{BASE_URL}/api/sales")
    if sales_before_response.status_code == 200:
        sales_before = sales_before_response.json()
        print(f"   Sales count before: {len(sales_before)}")
    else:
        sales_before = []
        print(f"   Could not fetch sales: {sales_before_response.status_code}")
    
    # Create bill
    print("\n🧾 Creating test bill...")
    test_products = products[:2]
    
    subtotal = float(test_products[0]['price']) + (float(test_products[1]['price']) * 2)
    tax_amount = subtotal * 0.18
    total_amount = subtotal + tax_amount
    
    bill_data = {
        "customer_name": "Test Customer",
        "business_type": "retail",
        "items": [
            {
                "product_id": test_products[0]['id'],
                "product_name": test_products[0]['name'],
                "quantity": 1,
                "unit_price": float(test_products[0]['price']),
                "total_price": float(test_products[0]['price'])
            },
            {
                "product_id": test_products[1]['id'],
                "product_name": test_products[1]['name'],
                "quantity": 2,
                "unit_price": float(test_products[1]['price']),
                "total_price": float(test_products[1]['price']) * 2
            }
        ],
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": 0,
        "total_amount": total_amount,
        "payment_method": "cash"
    }
    
    bill_response = session.post(
        f"{BASE_URL}/api/bills",
        json=bill_data
    )
    
    if bill_response.status_code == 201:
        result = bill_response.json()
        print(f"✅ Bill created: {result.get('bill_number')}")
        bill_id = result.get('bill_id')
        
        # Wait a moment for data to propagate
        time.sleep(2)
        
        # Check sales after
        print("\n📊 Checking sales after bill creation...")
        sales_after_response = session.get(f"{BASE_URL}/api/sales")
        if sales_after_response.status_code == 200:
            sales_after = sales_after_response.json()
            print(f"   Sales count after: {len(sales_after)}")
            
            # Check if new sales were added
            new_sales_count = len(sales_after) - len(sales_before)
            if new_sales_count >= 2:  # Should have 2 sales entries (one per item)
                print(f"✅ Sales data updated correctly (+{new_sales_count} entries)")
            else:
                print(f"❌ Sales data not updated properly (expected +2, got +{new_sales_count})")
        else:
            print(f"❌ Could not fetch sales after: {sales_after_response.status_code}")
        
        # Check dashboard stats
        print("\n📈 Checking dashboard stats...")
        dashboard_response = session.get(f"{BASE_URL}/api/dashboard/stats/sales")
        if dashboard_response.status_code == 200:
            stats = dashboard_response.json()
            print(f"✅ Dashboard stats accessible")
            print(f"   Total sales: {stats.get('total_sales', 'N/A')}")
        else:
            print(f"⚠️  Dashboard stats: {dashboard_response.status_code}")
        
    else:
        print(f"❌ Bill creation failed: {bill_response.status_code}")
        print(f"   Response: {bill_response.text}")

if __name__ == "__main__":
    test_bill_and_sales()
