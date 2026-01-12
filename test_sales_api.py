import requests
import json

# Test the sales API to see what data it's returning
try:
    response = requests.get('http://localhost:5000/api/sales/all?filter=today')
    if response.status_code == 200:
        data = response.json()
        print("API Response:")
        print(f"Total sales: {len(data.get('sales', []))}")
        print("\nFirst few sales:")
        for i, sale in enumerate(data.get('sales', [])[:3]):
            print(f"\nSale {i+1}:")
            print(f"  Bill Number: {sale.get('bill_number', 'N/A')}")
            print(f"  Created At: {sale.get('created_at', 'N/A')}")
            print(f"  Date: {sale.get('date', 'N/A')}")
            print(f"  Time: {sale.get('time', 'N/A')}")
            print(f"  Sale Date: {sale.get('sale_date', 'N/A')}")
            print(f"  Sale Time: {sale.get('sale_time', 'N/A')}")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")