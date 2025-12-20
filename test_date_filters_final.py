#!/usr/bin/env python3
"""
Test date filters in Sales module - Final comprehensive test
"""
import requests
import json
from datetime import datetime, timedelta
import pytz

# Test configuration
BASE_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

def test_date_filter(filter_type, start_date=None, end_date=None):
    """Test a specific date filter"""
    print(f"\n🧪 Testing {filter_type.upper()} filter...")
    
    params = {'filter': filter_type}
    if start_date:
        params['startDate'] = start_date
    if end_date:
        params['endDate'] = end_date
    
    try:
        response = requests.get(f"{BASE_URL}/api/sales/all", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sales = data.get('sales', [])
                summary = data.get('summary', {})
                filters = data.get('filters', {})
                
                print(f"✅ {filter_type.upper()} Filter Results:")
                print(f"   📊 Records: {len(sales)}")
                print(f"   💰 Total Sales: ₹{summary.get('total_sales', 0):,.2f}")
                print(f"   🧾 Total Bills: {summary.get('total_bills', 0)}")
                print(f"   📅 Date Range: {filters.get('startDate')} to {filters.get('endDate')}")
                
                # Show first few records
                if sales:
                    print(f"   📋 Sample Records:")
                    for i, sale in enumerate(sales[:3]):
                        date_str = sale.get('date') or sale.get('created_at', 'N/A')
                        print(f"      {i+1}. Bill #{sale.get('bill_number', 'N/A')} - {date_str} - ₹{sale.get('total_amount', 0)}")
                
                return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False

def test_custom_date_range():
    """Test custom date range"""
    print(f"\n🧪 Testing CUSTOM DATE RANGE filter...")
    
    # Test with specific date range
    start_date = "2024-12-19"  # Yesterday
    end_date = "2024-12-20"    # Today
    
    params = {
        'filter': 'custom',
        'startDate': start_date,
        'endDate': end_date
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/sales/all", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sales = data.get('sales', [])
                summary = data.get('summary', {})
                
                print(f"✅ CUSTOM RANGE Results:")
                print(f"   📊 Records: {len(sales)}")
                print(f"   💰 Total Sales: ₹{summary.get('total_sales', 0):,.2f}")
                print(f"   📅 Range: {start_date} to {end_date}")
                
                return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False

def main():
    """Run comprehensive date filter tests"""
    print("🚀 Starting Date Filter Tests...")
    print("=" * 50)
    
    # Get current IST date
    ist_tz = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist_tz)
    today = now_ist.strftime('%Y-%m-%d')
    yesterday = (now_ist - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Current IST Date: {today}")
    print(f"📅 Yesterday IST Date: {yesterday}")
    
    # Test all filter types
    tests = [
        ('today', None, None),
        ('yesterday', None, None),
        ('week', None, None),
        ('month', None, None)
    ]
    
    results = []
    for filter_type, start, end in tests:
        success = test_date_filter(filter_type, start, end)
        results.append((filter_type, success))
    
    # Test custom date range
    custom_success = test_custom_date_range()
    results.append(('custom', custom_success))
    
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
        print("🎉 All date filters are working correctly!")
    else:
        print("⚠️  Some date filters need attention")

if __name__ == "__main__":
    main()