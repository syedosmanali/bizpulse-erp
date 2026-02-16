import requests
import json

# Test the retail dashboard endpoint
try:
    response = requests.get('http://localhost:5000/api/dashboard/stats')
    data = response.json()
    
    print("=== RETAIL DASHBOARD ENDPOINT RESPONSE ===")
    print(json.dumps(data, indent=2))
    
    # Extract the relevant stats
    if data.get('success'):
        print("\n=== EXTRACTED STATS ===")
        print(f"Today Sales: {data.get('today_sales', 0)}")
        print(f"Today Revenue: {data.get('today_revenue', 0)}")
        print(f"Today Profit: {data.get('today_profit', 0)}")
        print(f"Today Orders: {data.get('today_orders', 0)}")
        
except Exception as e:
    print(f"Error: {e}")