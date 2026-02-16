import requests
import json

# Test 1: Check if the dashboard API is working
print("=== TEST 1: Dashboard API ===")
try:
    response = requests.get('http://localhost:5000/api/dashboard/stats', timeout=5)
    data = response.json()
    print(f"✅ API Status: {response.status_code}")
    print(f"✅ Success: {data.get('success')}")
    print(f"✅ Today Sales: {data.get('today_sales')}")
    print(f"✅ Today Revenue: {data.get('today_revenue')}")
    print(f"✅ Today Orders: {data.get('today_orders')}")
    print(f"✅ Today Profit: {data.get('today_profit')}")
except Exception as e:
    print(f"❌ API Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Check dashboard HTML template
print("=== TEST 2: Dashboard Template ===")
try:
    response = requests.get('http://localhost:5000/retail/dashboard', timeout=5)
    content = response.text
    
    # Check if key elements exist
    checks = {
        'retail_dashboard.html': 'retail_dashboard.html' in content,
        'STATS GRID': 'STATS GRID' in content,
        'todaySales': 'todaySales' in content,
        'todayRevenue': 'todayRevenue' in content,
        'totalOrders': 'totalOrders' in content,
        'netProfit': 'netProfit' in content
    }
    
    print(f"✅ Page Status: {response.status_code}")
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
        
    # Show a snippet of the content around the stats
    if 'todaySales' in content:
        start_idx = content.find('todaySales')
        snippet = content[max(0, start_idx-100):start_idx+100]
        print(f"\nSnippet around todaySales: {snippet}")
        
except Exception as e:
    print(f"❌ Template Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Check if we can access our test page
print("=== TEST 3: Test Page Access ===")
try:
    response = requests.get('http://localhost:8080/test_dashboard_display.html', timeout=5)
    print(f"✅ Test page status: {response.status_code}")
    print("✅ You can access the test page at: http://localhost:8080/test_dashboard_display.html")
except Exception as e:
    print(f"❌ Test page error: {e}")
    print("❌ Make sure the Python HTTP server is running on port 8080")