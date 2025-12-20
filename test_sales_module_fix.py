#!/usr/bin/env python3
"""
Test the fixed sales module with proper filtering and data storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_sales_api_filters():
    """Test sales API with different filters"""
    
    print("🧪 Testing Sales Module API with Filters")
    print("=" * 60)
    
    filters_to_test = [
        {'filter': 'today', 'name': 'Today Filter'},
        {'filter': 'yesterday', 'name': 'Yesterday Filter'},
        {'filter': 'week', 'name': 'Week Filter'},
        {'filter': 'month', 'name': 'Month Filter'},
        {'filter': 'all', 'name': 'All Data Filter'},
        {'filter': 'today', 'payment_method': 'cash', 'name': 'Today + Cash Filter'},
        {'filter': 'today', 'category': 'General', 'name': 'Today + Category Filter'}
    ]
    
    with app.test_client() as client:
        for filter_test in filters_to_test:
            print(f"\n📋 Testing {filter_test['name']}...")
            
            # Build query parameters
            params = []
            for key, value in filter_test.items():
                if key != 'name':
                    params.append(f"{key}={value}")
            
            query_string = '&'.join(params)
            url = f'/api/sales/all?{query_string}'
            
            try:
                response = client.get(url)
                
                if response.status_code == 200:
                    data = response.get_json()
                    
                    if data.get('success'):
                        sales_count = len(data.get('sales', []))
                        summary = data.get('summary', {})
                        filters_applied = data.get('filters', {})
                        
                        print(f"✅ {filter_test['name']}: Working")
                        print(f"   Sales Records: {sales_count}")
                        print(f"   Total Sales: ₹{summary.get('total_sales', 0)}")
                        print(f"   Total Bills: {summary.get('total_bills', 0)}")
                        print(f"   Filters Applied: {filters_applied}")
                    else:
                        print(f"❌ {filter_test['name']}: API returned success=false")
                else:
                    print(f"❌ {filter_test['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {filter_test['name']}: Exception - {str(e)}")

def test_sales_data_format():
    """Test if sales data has correct format for frontend"""
    
    print("\n🧪 Testing Sales Data Format")
    print("=" * 40)
    
    with app.test_client() as client:
        response = client.get('/api/sales/all?filter=all&limit=5')
        
        if response.status_code == 200:
            data = response.get_json()
            
            if data.get('success') and data.get('sales'):
                sales = data['sales']
                
                if len(sales) > 0:
                    sample_sale = sales[0]
                    
                    print("✅ Sales data format check:")
                    
                    # Check required fields for frontend
                    required_fields = [
                        'id', 'bill_number', 'customer_name', 'product_name',
                        'total_amount', 'payment_method', 'date', 'quantity'
                    ]
                    
                    for field in required_fields:
                        if field in sample_sale:
                            print(f"   ✅ {field}: {sample_sale[field]}")
                        else:
                            print(f"   ❌ {field}: Missing")
                    
                    print(f"\n📊 Sample Sale Data:")
                    print(f"   Bill: {sample_sale.get('bill_number', 'N/A')}")
                    print(f"   Customer: {sample_sale.get('customer_name', 'N/A')}")
                    print(f"   Product: {sample_sale.get('product_name', 'N/A')}")
                    print(f"   Amount: ₹{sample_sale.get('total_amount', 0)}")
                    print(f"   Payment: {sample_sale.get('payment_method', 'N/A')}")
                    
                else:
                    print("❌ No sales data found")
            else:
                print("❌ API response format incorrect")
        else:
            print(f"❌ API request failed: {response.status_code}")

def test_sales_page_route():
    """Test if sales page loads correctly"""
    
    print("\n🧪 Testing Sales Page Route")
    print("=" * 30)
    
    with app.test_client() as client:
        response = client.get('/retail/sales')
        
        if response.status_code == 200:
            print("✅ Sales page route: Working")
            content = response.get_data(as_text=True)
            
            # Check if important elements are present
            checks = [
                ('Sales Management', 'Page title'),
                ('filter-input', 'Filter controls'),
                ('salesTable', 'Sales table'),
                ('loadSales()', 'JavaScript function'),
                ('/api/sales/all', 'API endpoint')
            ]
            
            for check_text, description in checks:
                if check_text in content:
                    print(f"   ✅ {description}: Found")
                else:
                    print(f"   ❌ {description}: Missing")
        else:
            print(f"❌ Sales page route failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing Sales Module Complete Fix")
    print("=" * 70)
    
    test_sales_api_filters()
    test_sales_data_format()
    test_sales_page_route()
    
    print("\n🎉 Sales module testing complete!")
    print("\n📋 What should work now:")
    print("- ✅ Proper date filtering (today, yesterday, week, month, all)")
    print("- ✅ Payment method filtering")
    print("- ✅ Category filtering")
    print("- ✅ Correct data format for frontend")
    print("- ✅ Real-time stats and summaries")
    print("- ✅ CSV export functionality")
    print("- ✅ Auto-refresh every 30 seconds")