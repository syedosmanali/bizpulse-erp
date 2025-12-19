#!/usr/bin/env python3
"""
Debug today's filter issue - check exact data format
"""

import sqlite3
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_today_filter():
    print("🔍 Debugging Today's Filter Issue")
    print("=" * 50)
    
    # Get current date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today's Date: {today}")
    
    # Check database directly
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get today's sales with full details
    today_sales = cursor.execute('''
        SELECT id, sale_date, sale_time, product_name, total_price, created_at
        FROM sales 
        WHERE sale_date = ?
        ORDER BY created_at DESC
    ''', (today,)).fetchall()
    
    print(f"\n📊 Today's Sales in Database:")
    print(f"   Count: {len(today_sales)}")
    
    for sale in today_sales:
        print(f"   - Product: {sale['product_name']}")
        print(f"     Sale Date: '{sale['sale_date']}'")
        print(f"     Sale Time: '{sale['sale_time']}'")
        print(f"     Amount: ₹{sale['total_price']}")
        print(f"     Created: {sale['created_at']}")
        print()
    
    # Test the API response format
    print(f"🔧 Testing API Response Format:")
    try:
        import app
        
        with app.app.test_request_context('/api/sales?per_page=100'):
            response = app.sales_api()
            data = response.get_json() if hasattr(response, 'get_json') else response
            
            if isinstance(data, dict) and 'sales' in data:
                sales = data['sales']
                
                # Find today's sales in API response
                api_today_sales = []
                for sale in sales:
                    sale_date = sale.get('sale_date', '')
                    if sale_date.startswith(today):
                        api_today_sales.append(sale)
                
                print(f"   API Total Sales: {len(sales)}")
                print(f"   API Today's Sales: {len(api_today_sales)}")
                
                for sale in api_today_sales:
                    print(f"   - Product: {sale.get('product_name', 'Unknown')}")
                    print(f"     Sale Date: '{sale.get('sale_date', '')}'")
                    print(f"     Amount: ₹{sale.get('total_price', 0)}")
                    
                    # Test JavaScript filtering logic
                    js_date = sale.get('sale_date', '').split(' ')[0] if sale.get('sale_date') else ''
                    matches = js_date == today
                    print(f"     JS Filter: '{js_date}' === '{today}' = {matches}")
                    print()
                
                # Show sample of all sales dates for comparison
                print(f"📋 Sample Sales Dates from API:")
                for sale in sales[:5]:
                    sale_date = sale.get('sale_date', '')
                    js_date = sale_date.split(' ')[0] if sale_date else ''
                    print(f"   - Full: '{sale_date}' → JS: '{js_date}'")
                
    except Exception as e:
        print(f"   ❌ API Test Error: {e}")
    
    conn.close()
    
    print(f"\n" + "=" * 50)
    print("🎯 Analysis:")
    
    if len(today_sales) > 0:
        print(f"✅ Database has {len(today_sales)} sales for today")
        print(f"✅ Expected: Frontend should show {len(today_sales)} sales")
        print(f"⚠️  If frontend shows 0, there's a filtering issue")
    else:
        print(f"❌ No sales found in database for today")
        print(f"✅ Frontend showing 0 is correct")
    
    print(f"\n💡 Frontend Debug Steps:")
    print(f"   1. Open browser console (F12)")
    print(f"   2. Look for: 'Current Date (JavaScript): {today}'")
    print(f"   3. Check: 'Available Sales Dates' contains {today}")
    print(f"   4. Verify: 'Today's sales ({today}): X out of Y total'")

if __name__ == "__main__":
    debug_today_filter()