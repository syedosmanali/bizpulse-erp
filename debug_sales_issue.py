#!/usr/bin/env python3
"""
Debug script to understand why Today filter is still showing yesterday's data
"""

import sqlite3
from datetime import datetime, timedelta

def debug_sales_issue():
    print("🔍 Debugging Sales Filter Issue")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get current date info
    current_date = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Current Date: {current_date}")
    print(f"📅 Yesterday: {yesterday}")
    
    # Check all sales with their exact dates
    print(f"\n📋 All Sales in Database (Recent 10):")
    all_sales = cursor.execute('''
        SELECT sale_date, sale_time, created_at, product_name, total_price, bill_number
        FROM sales 
        ORDER BY created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    for i, sale in enumerate(all_sales, 1):
        print(f"   {i}. Date: {sale['sale_date']}, Product: {sale['product_name']}, Amount: ₹{sale['total_price']}")
    
    # Test today's filter exactly
    print(f"\n🎯 Today's Sales Filter Test ({current_date}):")
    today_sales = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales 
        WHERE sale_date = ?
    ''', (current_date,)).fetchone()
    
    print(f"   📊 Count: {today_sales['count']}")
    print(f"   💰 Total: ₹{today_sales['total']}")
    
    # Test yesterday's filter
    print(f"\n📅 Yesterday's Sales Filter Test ({yesterday}):")
    yesterday_sales = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales 
        WHERE sale_date = ?
    ''', (yesterday,)).fetchone()
    
    print(f"   📊 Count: {yesterday_sales['count']}")
    print(f"   💰 Total: ₹{yesterday_sales['total']}")
    
    # Check if there's any issue with date format
    print(f"\n🔍 Date Format Analysis:")
    unique_dates = cursor.execute('''
        SELECT DISTINCT sale_date, COUNT(*) as count
        FROM sales 
        GROUP BY sale_date 
        ORDER BY sale_date DESC
    ''').fetchall()
    
    for date_row in unique_dates:
        date_str = date_row['sale_date']
        count = date_row['count']
        if date_str == current_date:
            print(f"   ✅ {date_str}: {count} sales (TODAY)")
        elif date_str == yesterday:
            print(f"   📅 {date_str}: {count} sales (YESTERDAY)")
        else:
            print(f"   📊 {date_str}: {count} sales")
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print("🔧 Analysis:")
    
    if today_sales['count'] == 0:
        print("✅ Today has 0 sales - this is CORRECT")
        print("✅ Today filter should show 0 results")
        if yesterday_sales['count'] > 0:
            print(f"⚠️  If showing yesterday's {yesterday_sales['count']} sales, there's a frontend issue")
    else:
        print(f"📊 Today has {today_sales['count']} sales")
    
    print(f"\n💡 Expected Frontend Behavior:")
    print(f"   - Today filter: Show {today_sales['count']} sales")
    print(f"   - Yesterday filter: Show {yesterday_sales['count']} sales")
    print(f"   - No automatic switching between dates")

if __name__ == "__main__":
    debug_sales_issue()