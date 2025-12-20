#!/usr/bin/env python3
"""
Test the sales-management page fix
"""
import urllib.request
import urllib.parse
import json

def test_sales_management_api():
    """Test the API that sales-management page uses"""
    print("🧪 Testing /api/sales/all endpoint for sales-management page...")
    
    # Test today filter
    params = urllib.parse.urlencode({'filter': 'today'})
    url = f"http://localhost:5000/api/sales/all?{params}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        if data.get('success'):
            sales = data.get('sales', [])
            summary = data.get('summary', {})
            
            print("✅ API Test Results:")
            print(f"   📊 Records: {len(sales)}")
            print(f"   💰 Total Sales: ₹{summary.get('total_sales', 0):,.2f}")
            print(f"   🧾 Total Bills: {summary.get('total_bills', 0)}")
            print(f"   📈 Avg Sale: ₹{summary.get('avg_sale_value', 0):,.2f}")
            print(f"   💵 Total Profit: ₹{summary.get('total_profit', 0):,.2f}")
            
            return True
        else:
            print(f"❌ API Error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False

def main():
    print("🚀 Testing Sales Management Page Fix")
    print("=" * 50)
    
    # Test API
    api_working = test_sales_management_api()
    
    print("\n" + "=" * 50)
    if api_working:
        print("✅ SALES MANAGEMENT FIX SUCCESSFUL!")
        print("\n📱 Test Instructions:")
        print("1. Open: http://localhost:5000/sales-management")
        print("2. Select 'Today' filter")
        print("3. Should show today's sales data")
        print("4. Try other filters (Yesterday, Week, Month)")
        print("5. All should work correctly now")
        
        print("\n🎯 Expected Results:")
        print("   TODAY: Should show today's sales only")
        print("   YESTERDAY: Should show yesterday's sales only")
        print("   WEEK: Should show this week's sales")
        print("   MONTH: Should show this month's sales")
    else:
        print("❌ API test failed - check server status")

if __name__ == "__main__":
    main()