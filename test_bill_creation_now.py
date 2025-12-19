import requests
import json

print("Testing bill creation with actual data...")

# Test bill data matching your screenshot
test_bill = {
    "items": [
        {
            "id": "prod-1",
            "name": "Rice (1kg)",
            "price": 80.0,
            "quantity": 3
        },
        {
            "id": "prod-2", 
            "name": "Wheat Flour (1kg)",
            "price": 45.0,
            "quantity": 1
        }
    ],
    "subtotal": 478.0,
    "cgst": 43.02,
    "sgst": 43.02,
    "total": 564.04
}

try:
    print("\nSending POST request to /api/sales...")
    response = requests.post(
        'http://localhost:5000/api/sales',
        json=test_bill,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"Bill Number: {result.get('bill_number')}")
        print(f"Total: ₹{result.get('total')}")
    else:
        print("\n❌ ERROR!")
        print(f"Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Raw response: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to server!")
    print("Make sure server is running on http://localhost:5000")
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
