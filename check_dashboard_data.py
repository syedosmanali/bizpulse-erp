#!/usr/bin/env python3
"""
Quick check of what dashboard should show
"""

import sqlite3
from datetime import datetime

def check_dashboard_data():
    print("🔍 Dashboard Data Check")
    print("=" * 40)
    
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today: {today}")
    
    # Today's bills
    bills_today = cursor.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
        FROM bills WHERE DATE(created_at) = ?
    ''', (today,)).fetchone()
    
    print(f"\n💰 Today's Revenue:")
    print(f"   Bills: {bills_today[0]}")
    print(f"   Total: ₹{bills_today[1]}")
    
    # Recent bills (all)
    recent_bills = cursor.execute('''
        SELECT bill_number, total_amount, created_at
        FROM bills ORDER BY created_at DESC LIMIT 5
    ''').fetchall()
    
    print(f"\n📋 Recent Bills:")
    for bill in recent_bills:
        date = bill[2][:10] if bill[2] else 'Unknown'
        print(f"   {bill[0]}: ₹{bill[1]} ({date})")
    
    # Products count
    products = cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1').fetchone()[0]
    customers = cursor.execute('SELECT COUNT(*) FROM customers WHERE is_active = 1').fetchone()[0]
    
    print(f"\n📊 Inventory:")
    print(f"   Products: {products}")
    print(f"   Customers: {customers}")
    
    conn.close()
    
    print(f"\n✅ Expected Dashboard:")
    print(f"   Today Revenue: ₹{bills_today[1]}")
    print(f"   Today Orders: {bills_today[0]}")
    print(f"   Total Products: {products}")
    print(f"   Total Customers: {customers}")

if __name__ == "__main__":
    check_dashboard_data()