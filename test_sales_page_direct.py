#!/usr/bin/env python3
"""
Direct test to check what the sales management page is actually showing
"""

import sqlite3
from datetime import datetime, timedelta
import os

def test_sales_page():
    print("🔍 Testing Sales Management Page Behavior")
    print("=" * 60)
    
    # Check current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Current Date: {current_date}")
    print(f"📅 Yesterday: {yesterday}")
    
    # Check database
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get today's sales
    today_sales = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales WHERE sale_date = ?
    ''', (current_date,)).fetchone()
    
    # Get yesterday's sales  
    yesterday_sales = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
        FROM sales WHERE sale_date = ?
    ''', (yesterday,)).fetchone()
    
    print(f"\n📊 Database Results:")
    print(f"   Today ({current_date}): {today_sales['count']} sales, ₹{today_sales['total']}")
    print(f"   Yesterday ({yesterday}): {yesterday_sales['count']} sales, ₹{yesterday_sales['total']}")
    
    # Check which template file exists and when it was last modified
    template_path = 'templates/sales_management_wine.html'
    if os.path.exists(template_path):
        mod_time = os.path.getmtime(template_path)
        mod_date = datetime.fromtimestamp(mod_time)
        print(f"\n📄 Template File:")
        print(f"   Path: {template_path}")
        print(f"   Last Modified: {mod_date}")
        
        # Check if the file contains our debug markers
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_debug = 'DEBUG: This is the FIXED version' in content
        has_version = 'Fixed v2.0' in content
        has_auto_switch = 'switching to yesterday automatically' in content
        
        print(f"   Contains Debug Marker: {'✅' if has_debug else '❌'}")
        print(f"   Contains Version Marker: {'✅' if has_version else '❌'}")
        print(f"   Contains Auto-Switch Logic: {'❌ (GOOD)' if not has_auto_switch else '⚠️ (BAD)'}")
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print("🎯 Expected Page Behavior:")
    print(f"   1. Page loads with 'Today' selected in dropdown")
    print(f"   2. Shows {today_sales['count']} sales for today ({current_date})")
    print(f"   3. If 0 sales, shows message: 'No sales found for today'")
    print(f"   4. Does NOT automatically switch to yesterday")
    print(f"   5. User can manually select 'Yesterday' to see {yesterday_sales['count']} sales")
    
    if today_sales['count'] == 0:
        print(f"\n✅ CORRECT BEHAVIOR: Today has 0 sales")
        print(f"   - Page should show 0 results")
        print(f"   - Should show 'No sales found for today' message")
        print(f"   - Should NOT show yesterday's {yesterday_sales['count']} sales automatically")
    
    print(f"\n🔧 If Still Seeing Wrong Behavior:")
    print(f"   1. Clear browser cache (Ctrl+Shift+R)")
    print(f"   2. Check URL is exactly: /sales-management")
    print(f"   3. Look for '(Fixed v2.0)' in page title")
    print(f"   4. Check browser console for debug messages")

if __name__ == "__main__":
    test_sales_page()