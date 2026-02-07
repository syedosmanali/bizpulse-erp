"""
Test products API on live server
"""

import requests

BASE_URL = "https://bizpulse-erp-1.onrender.com"

# Login first
login_data = {
    "loginId": "bizpulse.erp@gmail.com",
    "password": "admin123"
}

session = requests.Session()

print("🔐 Logging in...")
login_response = session.post(f"{BASE_URL}/api/auth/unified-login", json=login_data)
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    print("✅ Login successful")
    
    # Now test products API
    print("\n📦 Fetching products...")
    products_response = session.get(f"{BASE_URL}/api/products")
    print(f"Products API Status: {products_response.status_code}")
    
    if products_response.status_code == 200:
        products = products_response.json()
        print(f"✅ Found {len(products)} products")
        
        if len(products) > 0:
            print("\n📋 Sample products:")
            for p in products[:5]:
                print(f"   - {p.get('name')}: ₹{p.get('price')} (Stock: {p.get('stock')})")
        else:
            print("⚠️  No products found!")
    else:
        print(f"❌ Products API failed: {products_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")
