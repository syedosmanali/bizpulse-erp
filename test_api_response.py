#!/usr/bin/env python3
"""
Test what the sales API is actually returning
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_response():
    print("🔍 Testing Sales API Response")
    print("=" * 50)
    
    try:
        import app
        
        # Create a test request context
        with app.app.test_request_context('/api/sales?per_page=100'):
            # Call the sales API function directly
            response = app.sales_api()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
            else:
                # If it's already JSON data
                data = response
            
            print(f"📊 API Response Type: {type(data)}")
            
            if isinstance(data, dict) and 'sales' in data:
                sales = data['sales']
                print(f"📋 Total Sales Returned: {len(sales)}")
                
                # Group by date
                from collections import defaultdict
                by_date = defaultdict(list)
                
                for sale in sales:
                    sale_date = sale.get('sale_date', '').split(' ')[0] if sale.get('sale_date') else 'Unknown'
                    by_date[sale_date].append(sale)
                
                print(f"\n📅 Sales by Date:")
                for date, date_sales in sorted(by_date.items(), reverse=True):
                    total = sum(s.get('total_price', 0) for s in date_sales)
                    print(f"   {date}: {len(date_sales)} sales, ₹{total}")
                    
                    # Show details for recent dates
                    if date in ['2025-12-19', '2025-12-18']:
                        for sale in date_sales[:3]:  # Show first 3
                            print(f"      - {sale.get('product_name', 'Unknown')}: ₹{sale.get('total_price', 0)}")
                
                # Test today's filter specifically
                today = '2025-12-19'
                today_sales = [s for s in sales if s.get('sale_date', '').startswith(today)]
                print(f"\n🎯 Today's Sales ({today}):")
                print(f"   Count: {len(today_sales)}")
                print(f"   Total: ₹{sum(s.get('total_price', 0) for s in today_sales)}")
                
                # Test yesterday's filter
                yesterday = '2025-12-18'
                yesterday_sales = [s for s in sales if s.get('sale_date', '').startswith(yesterday)]
                print(f"\n📅 Yesterday's Sales ({yesterday}):")
                print(f"   Count: {len(yesterday_sales)}")
                print(f"   Total: ₹{sum(s.get('total_price', 0) for s in yesterday_sales)}")
                
            else:
                print(f"❌ Unexpected API response format: {data}")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_response()