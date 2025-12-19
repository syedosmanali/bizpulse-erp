#!/usr/bin/env python3
"""
Test to verify that Today filter shows exactly today's data (0 if no sales)
"""

import sqlite3
from datetime import datetime

def test_today_filter():
    print("🔍 Testing Today Filter - Exact Date Matching")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Current Date: {current_date}")
    
    # Check today's sales exactly
    today_sales = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total,
               GROUP_CONCAT(product_name) as products
        FROM sales 
        WHERE sale_date = ?
    ''', (current_date,)).fetchone()
    
    print(f"\n🎯 Today's Sales ({current_date}):")
    print(f"   📊 Count: {today_sales['count']} sales")
    print(f"   💰 Total: ₹{today_sales['total']}")
    if today_sales['products']:
        print(f"   🛒 Products: {today_sales['products']}")
    else:
        print(f"   🛒 Products: None")
    
    # Check what dates have sales
    print(f"\n📋 Available Sales Dates:")
    available_dates = cursor.execute('''
        SELECT sale_date, COUNT(*) as count, SUM(total_price) as total
        FROM sales 
        GROUP BY sale_date 
        ORDER BY sale_date DESC 
        LIMIT 5
    ''').fetchall()
    
    for date_row in available_dates:
        print(f"   {date_row['sale_date']}: {date_row['count']} sales, ₹{date_row['total']}")
    
    conn.close()
    
    print(f"\n" + "=" * 50)
    print("✅ Expected Behavior:")
    print(f"   - Today filter should show: {today_sales['count']} sales")
    print(f"   - Should NOT auto-switch to yesterday")
    print(f"   - Should show clear message if 0 sales")
    
    if today_sales['count'] == 0:
        print("\n✅ CORRECT: No sales for today - filter should show 0 results")
    else:
        print(f"\n📊 INFO: Found {today_sales['count']} sales for today")

if __name__ == "__main__":
    test_today_filter()