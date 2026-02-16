import requests
import time

# Wait for server to be ready
time.sleep(3)

try:
    response = requests.get('http://localhost:5000/api/dashboard/stats', timeout=10)
    data = response.json()
    print("=== DASHBOARD TEST RESULTS ===")
    print(f"Success: {data.get('success')}")
    print(f"Today Sales: {data.get('today_sales', 'N/A')}")
    print(f"Today Revenue: {data.get('today_revenue', 'N/A')}")
    print(f"Today Profit: {data.get('today_profit', 'N/A')}")
    print(f"Today Orders: {data.get('today_orders', 'N/A')}")
    print(f"Recent Sales Count: {len(data.get('recent_sales', []))}")
    
    if data.get('recent_sales'):
        print("\nRecent Sales:")
        for sale in data['recent_sales'][:3]:  # Show first 3
            print(f"  - {sale.get('bill_number')}: ₹{sale.get('total_amount')} ({sale.get('customer_name')})")
            
except Exception as e:
    print(f"Error: {e}")