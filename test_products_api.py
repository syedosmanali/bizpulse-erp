"""
Test products API to verify data is being returned
"""

import requests
import json

# Test without authentication (should fail or return empty)
print("Testing /api/products endpoint...")
print("=" * 60)

try:
    response = requests.get('http://localhost:5000/api/products')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"Products returned: {len(products)}")
        
        if len(products) > 0:
            print("\nFirst 3 products:")
            for i, product in enumerate(products[:3]):
                print(f"\n{i+1}. {product.get('name')}")
                print(f"   ID: {product.get('id')}")
                print(f"   Price: ₹{product.get('price')}")
                print(f"   Stock: {product.get('stock')}")
                print(f"   User ID: {product.get('user_id', 'NULL')}")
        else:
            print("\n⚠️ No products returned!")
            print("This means the API is working but no products match the filter.")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Note: If no products returned, you need to login first")
print("The API filters products by user_id from session")
