#!/usr/bin/env python3
"""
Test script to debug and fix the sales date filtering issue
"""

import sqlite3
from datetime import datetime

def test_date_filtering():
    print("🔍 Testing Sales Date Filtering Issue")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Current Date: {current_date}")
    
    # Check all sales dates
    print("\n📊 All Sales Dates in Database:")
    sales_dates = cursor.execute('''
        SELECT DISTINCT sale_date, COUNT(*) as count 
        FROM sales 
        GROUP BY sale_date 
        ORDER BY sale_date DESC
    ''').fetchall()
    
    for row in sales_dates:
        print(f"   {row['sale_date']}: {row['count']} sales")
    
    # Check today's sales using different methods
    print(f"\n🎯 Today's Sales ({current_date}):")
    
    # Method 1: Direct date comparison
    today_sales_1 = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales 
        WHERE sale_date = ?
    ''', (current_date,)).fetchone()
    
    print(f"   Method 1 (Direct): {today_sales_1['count']} sales, ₹{today_sales_1['total']}")
    
    # Method 2: Using DATE() function
    today_sales_2 = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales 
        WHERE DATE(sale_date) = DATE('now')
    ''').fetchone()
    
    print(f"   Method 2 (SQLite DATE): {today_sales_2['count']} sales, ₹{today_sales_2['total']}")
    
    # Method 3: Using created_at field
    today_sales_3 = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales 
        WHERE DATE(created_at) = ?
    ''', (current_date,)).fetchone()
    
    print(f"   Method 3 (created_at): {today_sales_3['count']} sales, ₹{today_sales_3['total']}")
    
    # Check what SQLite thinks 'now' is
    sqlite_now = cursor.execute("SELECT DATE('now') as today").fetchone()
    print(f"\n🕐 SQLite 'now': {sqlite_now['today']}")
    
    # Check recent sales with full details
    print(f"\n📋 Recent Sales (Last 5):")
    recent_sales = cursor.execute('''
        SELECT sale_date, sale_time, created_at, product_name, total_price
        FROM sales 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    for sale in recent_sales:
        print(f"   {sale['sale_date']} {sale['sale_time']} - {sale['product_name']} - ₹{sale['total_price']}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🔧 Recommended Fix:")
    if today_sales_1['count'] == 0:
        print("   ✅ No sales found for today - this is correct if no transactions occurred today")
        print("   ✅ The filter is working correctly, just no data for today")
    else:
        print("   ⚠️  Sales found for today, check frontend filtering logic")

if __name__ == "__main__":
    test_date_filtering()