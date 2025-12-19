#!/usr/bin/env python3
"""
Direct test of the filtering logic to see what's wrong
"""

import sqlite3
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_filter_logic():
    print("🔍 Direct Filter Logic Test")
    print("=" * 50)
    
    # Get current system date
    system_date = datetime.now().strftime('%Y-%m-%d')
    print(f"System Date: {system_date}")
    
    # Get database data
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all sales
    all_sales = cursor.execute('''
        SELECT sale_date, product_name, total_price 
        FROM sales 
        ORDER BY created_at DESC
    ''').fetchall()
    
    print(f"\nAll Sales ({len(all_sales)} total):")
    for sale in all_sales[:10]:  # Show first 10
        print(f"  {sale['sale_date']} - {sale['product_name']} - ₹{sale['total_price']}")
    
    # Test JavaScript-like filtering for today
    print(f"\n🎯 Testing Today Filter ({system_date}):")
    today_sales = []
    for sale in all_sales:
        sale_date = sale['sale_date']
        # Simulate JavaScript: sale_date.split(' ')[0]
        js_date = sale_date.split(' ')[0] if sale_date else ''
        matches = js_date == system_date
        
        if matches:
            today_sales.append(sale)
            print(f"  ✅ MATCH: {js_date} === {system_date} → {sale['product_name']}")
        else:
            # Show first few non-matches for debugging
            if len(today_sales) == 0 and len([s for s in all_sales if s['sale_date'].split(' ')[0] != system_date]) < 5:
                print(f"  ❌ NO MATCH: {js_date} !== {system_date}")
    
    print(f"\nToday Filter Results:")
    print(f"  Found: {len(today_sales)} sales")
    if today_sales:
        for sale in today_sales:
            print(f"    - {sale['product_name']}: ₹{sale['total_price']}")
    else:
        print(f"    - No sales found for {system_date}")
    
    # Test yesterday filter
    yesterday = datetime.now()
    yesterday = yesterday.replace(day=yesterday.day-1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    print(f"\n📅 Testing Yesterday Filter ({yesterday_str}):")
    yesterday_sales = []
    for sale in all_sales:
        js_date = sale['sale_date'].split(' ')[0] if sale['sale_date'] else ''
        if js_date == yesterday_str:
            yesterday_sales.append(sale)
    
    print(f"  Found: {len(yesterday_sales)} sales")
    for sale in yesterday_sales:
        print(f"    - {sale['product_name']}: ₹{sale['total_price']}")
    
    conn.close()
    
    print(f"\n" + "=" * 50)
    print("🔧 Analysis:")
    
    if len(today_sales) == 1:
        print("✅ Today filter should show 1 sale (Tea ₹800)")
    elif len(today_sales) == 0:
        print("❌ Today filter shows 0 sales - this might be why you see yesterday's data")
    else:
        print(f"⚠️  Today filter shows {len(today_sales)} sales")
    
    if len(yesterday_sales) == 2:
        print("✅ Yesterday filter should show 2 sales (Rice)")
    
    print(f"\n💡 If frontend shows yesterday's data for today filter:")
    print(f"   1. JavaScript date calculation might be wrong")
    print(f"   2. Timezone issue")
    print(f"   3. Browser cache showing old logic")
    print(f"   4. Wrong page (/retail/sales vs /sales-management)")

if __name__ == "__main__":
    test_filter_logic()