import requests
import json

# Get dashboard stats
response = requests.get('http://localhost:5000/api/dashboard/stats')
data = response.json()

print("Recent sales:")
for sale in data['recent_sales']:
    print(f"  - {sale['bill_number']}: {sale['total_amount']}")