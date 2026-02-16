import requests
import time

# Wait a moment for server to fully start
time.sleep(2)

try:
    response = requests.get('http://localhost:5000/api/dashboard/stats', timeout=5)
    data = response.json()
    print("SUCCESS - Dashboard returns:")
    print(f"Today Sales: {data.get('today_sales', 'N/A')}")
    print(f"Today Revenue: {data.get('today_revenue', 'N/A')}")
    print(f"Today Profit: {data.get('today_profit', 'N/A')}")
    print(f"Today Orders: {data.get('today_orders', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")