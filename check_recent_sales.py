import requests
import json

# Get dashboard stats
response = requests.get('http://localhost:5000/api/dashboard/stats')
data = response.json()

print("Recent sales:")
for sale in data['recent_sales']:
    print(f"  - {sale['bill_number']}: {sale['total_amount']}")

print(f"\nToday's stats:")
print(f"  Sales: {data['today_sales']}")
print(f"  Revenue: {data['today_revenue']}")
print(f"  Orders: {data['today_orders']}")
print(f"  Profit: {data['today_profit']}")