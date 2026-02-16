import requests
import json

# Check the dashboard stats API response
response = requests.get('http://localhost:5000/api/dashboard/stats/sales')
data = response.json()

print("API Response Structure:")
print("=" * 50)
print(json.dumps(data, indent=2))

print("\nKey Fields Check:")
print("=" * 30)
if 'stats' in data:
    stats = data['stats']
    print(f"today_sales: {stats.get('today_sales', 'NOT FOUND')}")
    print(f"today_revenue: {stats.get('today_revenue', 'NOT FOUND')}")
    print(f"today_profit: {stats.get('today_profit', 'NOT FOUND')}")
    print(f"today_orders: {stats.get('today_orders', 'NOT FOUND')}")
    print(f"today nested: {stats.get('today', 'NOT FOUND')}")
    if isinstance(stats.get('today'), dict):
        print(f"  today.sales: {stats['today'].get('sales', 'NOT FOUND')}")
        print(f"  today.revenue: {stats['today'].get('revenue', 'NOT FOUND')}")
        print(f"  today.transactions: {stats['today'].get('transactions', 'NOT FOUND')}")
        print(f"  today.profit: {stats['today'].get('profit', 'NOT FOUND')}")
else:
    print("No 'stats' key found in response")