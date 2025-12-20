#!/usr/bin/env python3
"""
Test the Sales API directly to verify date filtering
"""
import urllib.request
import urllib.parse
import json
from datetime import datetime

def test_api_endpoint(filter_type, start_date=None, end_date=None):
    """Test a specific API endpoint"""
    print(f"\n🧪 Testing {filter_type.upper()} filter...")
    
    # Build parameters
    params = {'filter': filter_type}
    if start_date:
        params['startDate'] = start_date
    if end_date:
        params['endDate'] = end_date
    
    # Build URL
    query_string = urllib.parse.urlencode(params)
    url = f"http://localhost:5000/api/sales/all?{query_string}"
    
    print(f"   🔗 URL: {url}")
    
    try:
        # Make request
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        if data.get('success'):
            sales = data.get('sales', [])
            summary = data.get('summary', {})
            filters = data.get('filters', {})
            debug_info = data.get('debug_info', {})
            
            print(f"✅ {filter_type.upper()} Results:")
            print(f"   📊 Records: {len(sales)}")
            print(f"   💰 Total Sales: ₹{summary.get('total_sales', 0):,.2f}")
            print(f"   🧾 Total Bills: {summary.get('total_bills', 0)}")
            print(f"   📅 Applied Range: {filters.get('startDate')} to {filters.get('endDate')}")
            
            if debug_info:
                print(f"   🐛 Debug Info:")
                print(f"      Server Time: {debug_info.get('current_time')}")
                print(f"      Query Dates: {debug_info.get('query_dates')}")
            
            # Show sample records
            if sales:
                print(f"   📋 Sample Records:")
                for i, sale in enumerate(sales[:3]):
                    date_str = sale.get('date') or sale.get('created_at', 'N/A')
                    print(f"      {i+1}. Bill #{sale.get('bill_number', 'N/A')} - {sale.get('product_name', 'N/A')} - ₹{sale.get('total_amount', 0)} - {date_str}")
            
            return True
        else:
            print(f"❌ API Error: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False

def main():
    """Test all date filters"""
    print("🚀 Testing Sales API Date Filters")
    print("=" * 50)
    
    # Test all filter types
    tests = [
        ('today', None, None),
        ('yesterday', None, None),
        ('week', None, None),
        ('month', None, None),
        ('custom', '2024-12-19', '2024-12-20')  # Yesterday to today
    ]
    
    results = []
    for filter_type, start, end in tests:
        success = test_api_endpoint(filter_type, start, end)
        results.append((filter_type, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    for filter_type, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {filter_type.upper()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All API date filters are working correctly!")
    else:
        print("⚠️  Some API date filters need attention")

if __name__ == "__main__":
    main()