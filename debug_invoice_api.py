import requests
import json

# Test the invoice API directly
url = "http://localhost:5000/api/invoices/61f6f126-21f3-4dea-b2e1-ac1d3c259ba3"
headers = {"Cookie": "user_id=test_user"}

try:
    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Headers:", response.headers.get('content-type'))
    
    data = response.json()
    print("\nAPI Response:")
    print(json.dumps(data, indent=2, default=str))
    
    if data.get("success"):
        invoice = data.get("invoice", {})
        items = data.get("items", [])
        
        print(f"\nInvoice Data Types:")
        for key, value in invoice.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        print(f"\nItems Data Types (first item):")
        if items:
            first_item = items[0]
            for key, value in first_item.items():
                print(f"  {key}: {type(value).__name__} = {value}")
        
except Exception as e:
    print(f"Error: {e}")