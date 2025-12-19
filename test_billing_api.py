import requests
import json

print("=" * 60)
print("BILLING API TEST - बिलिंग API टेस्ट")
print("=" * 60)

# Test data
test_bill = {
    "items": [
        {
            "id": "prod-1",
            "name": "Rice (1kg)",
            "price": 80.0,
            "quantity": 2
        },
        {
            "id": "prod-2",
            "name": "Wheat Flour (1kg)",
            "price": 45.0,
            "quantity": 1
        }
    ],
    "subtotal": 205.0,
    "cgst": 18.45,
    "sgst": 18.45,
    "total": 241.90
}

print("\n1. Testing Products API...")
try:
    response = requests.get('http://localhost:5000/api/products')
    if response.status_code == 200:
        products = response.json()
        print(f"   ✅ Products API working - {len(products)} products found")
    else:
        print(f"   ❌ Products API failed - Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   ⚠️  Make sure server is running!")

print("\n2. Testing Sales POST API (Create Bill)...")
try:
    response = requests.post(
        'http://localhost:5000/api/sales',
        json=test_bill,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Bill created successfully!")
        print(f"   📝 Bill Number: {result.get('bill_number')}")
        print(f"   💰 Total: ₹{result.get('total')}")
        print(f"   🆔 Bill ID: {result.get('bill_id')}")
    else:
        print(f"   ❌ Bill creation failed - Status: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   ⚠️  Make sure server is running!")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
