import requests
import json

# Test the credit history API directly
response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}...")  # First 500 chars

# Parse and check bills
if response.status_code == 200:
    data = response.json()
    print(f"\nFound {len(data['bills'])} bills in response")
    
    today_bills = [b for b in data['bills'] if '2026-02-10' in b['created_at']]
    print(f"Found {len(today_bills)} bills from today")
    
    for bill in today_bills:
        print(f"  - {bill['bill_number']}: {bill['payment_method']} - {bill['payment_status']}")
else:
    print("API request failed")