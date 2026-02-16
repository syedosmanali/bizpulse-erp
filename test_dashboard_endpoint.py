import requests
import json

# Test the actual dashboard endpoint
try:
    response = requests.get('http://localhost:5000/api/dashboard/data')
    data = response.json()
    
    print("=== DASHBOARD ENDPOINT RESPONSE ===")
    print(json.dumps(data, indent=2))
    
    # Extract the relevant stats
    if data.get('success') and data.get('data'):
        dashboard_data = data['data']
        sales_stats = dashboard_data.get('sales_stats', {})
        
        print("\n=== EXTRACTED STATS ===")
        print(f"Today Sales: {sales_stats.get('today', {}).get('sales', 0)}")
        print(f"Today Revenue: {sales_stats.get('today', {}).get('revenue', 0)}")
        print(f"Today Orders: {sales_stats.get('today', {}).get('orders', 0)}")
        
except Exception as e:
    print(f"Error: {e}")