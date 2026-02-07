"""
Comprehensive test for all fixes deployed
Tests: Login, Products, Bill Creation, Data Persistence
"""
import requests
import json
import time

# Live site URL
BASE_URL = "https://bizpulse-erp-1.onrender.com"

# Test credentials
EMAIL = "bizpulse.erp@gmail.com"
PASSWORD = "admin123"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_login():
    """Test 1: Login"""
    print_section("TEST 1: LOGIN")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        print("✅ Login successful")
        data = response.json()
        print(f"   User: {data.get('user', {}).get('name')}")
        print(f"   Type: {data.get('user', {}).get('type')}")
        print(f"   Admin: {data.get('user', {}).get('is_super_admin')}")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_products(cookies):
    """Test 2: Get Products"""
    print_section("TEST 2: GET PRODUCTS")
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    response = session.get(f"{BASE_URL}/api/products")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Products fetched: {len(products)} products")
        if len(products) > 0:
            print(f"   Sample: {products[0]['name']} - ${products[0]['price']}")
        return products
    else:
        print(f"❌ Failed to fetch products: {response.status_code}")
        print(f"   Response: {response.text}")
        return []

def test_add_product(cookies):
    """Test 3: Add Product"""
    print_section("TEST 3: ADD PRODUCT")
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    test_product = {
        "name": f"Test Product {int(time.time())}",
        "category": "Test Category",
        "price": 99.99,
        "cost": 50.00,
        "stock": 100,
        "min_stock": 10,
        "unit": "piece",
        "business_type": "retail"
    }
    
    response = session.post(
        f"{BASE_URL}/api/products",
        json=test_product
    )
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Product added successfully")
        print(f"   ID: {data.get('product', {}).get('id')}")
        print(f"   Name: {data.get('product', {}).get('name')}")
        return data.get('product', {}).get('id')
    else:
        print(f"❌ Failed to add product: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_product_persistence(cookies, product_id):
    """Test 4: Product Persistence After Refresh"""
    print_section("TEST 4: PRODUCT PERSISTENCE")
    
    if not product_id:
        print("⚠️  Skipping - no product ID")
        return False
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    # Wait a moment
    time.sleep(2)
    
    # Fetch products again
    response = session.get(f"{BASE_URL}/api/products")
    
    if response.status_code == 200:
        products = response.json()
        product_exists = any(p['id'] == product_id for p in products)
        
        if product_exists:
            print("✅ Product persists after refresh")
            return True
        else:
            print("❌ Product disappeared after refresh")
            return False
    else:
        print(f"❌ Failed to fetch products: {response.status_code}")
        return False

def test_delete_product(cookies, product_id):
    """Test 5: Delete Product"""
    print_section("TEST 5: DELETE PRODUCT")
    
    if not product_id:
        print("⚠️  Skipping - no product ID")
        return False
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    response = session.delete(f"{BASE_URL}/api/products/{product_id}")
    
    if response.status_code == 200:
        print("✅ Product deleted successfully")
        
        # Wait and verify it stays deleted
        time.sleep(2)
        
        response = session.get(f"{BASE_URL}/api/products")
        if response.status_code == 200:
            products = response.json()
            product_exists = any(p['id'] == product_id for p in products)
            
            if not product_exists:
                print("✅ Product stays deleted after refresh")
                return True
            else:
                print("❌ Product reappeared after refresh")
                return False
    else:
        print(f"❌ Failed to delete product: {response.status_code}")
        return False

def test_bill_creation(cookies, products):
    """Test 6: Bill Creation"""
    print_section("TEST 6: BILL CREATION")
    
    if len(products) < 2:
        print("⚠️  Not enough products for billing test")
        return False
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    # Use first 2 products
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
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": 0,
        "total_amount": total_amount,
        "payment_method": "cash"
    }
    
    response = session.post(
        f"{BASE_URL}/api/bills",
        json=bill_data
    )
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Bill created successfully")
        print(f"   Bill Number: {data.get('bill_number')}")
        print(f"   Total: ${data.get('total_amount')}")
        return True
    else:
        print(f"❌ Bill creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("  COMPREHENSIVE FIX VERIFICATION TEST")
    print("  Testing: bizpulse-erp-1.onrender.com")
    print("🚀" * 30)
    
    results = {
        "login": False,
        "get_products": False,
        "add_product": False,
        "product_persistence": False,
        "delete_product": False,
        "bill_creation": False
    }
    
    # Test 1: Login
    cookies = test_login()
    results["login"] = cookies is not None
    
    if not cookies:
        print("\n❌ Cannot continue - login failed")
        return results
    
    # Test 2: Get Products
    products = test_products(cookies)
    results["get_products"] = len(products) > 0
    
    # Test 3: Add Product
    product_id = test_add_product(cookies)
    results["add_product"] = product_id is not None
    
    # Test 4: Product Persistence
    results["product_persistence"] = test_product_persistence(cookies, product_id)
    
    # Test 5: Delete Product
    results["delete_product"] = test_delete_product(cookies, product_id)
    
    # Test 6: Bill Creation
    results["bill_creation"] = test_bill_creation(cookies, products)
    
    # Summary
    print_section("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("All critical fixes are working correctly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("Some issues may still need attention")
    
    return results

if __name__ == "__main__":
    run_all_tests()
