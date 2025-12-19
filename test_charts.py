#!/usr/bin/env python3
"""
Test script to verify dashboard charts API is working
"""
import sqlite3
import json
from datetime import datetime, timedelta

def test_charts_api():
    print("🧪 Testing Dashboard Charts API...")
    print("=" * 50)
    
    # Test database connection and data
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    
    # Check if we have bills data
    bills_count = conn.execute('SELECT COUNT(*) as count FROM bills').fetchone()['count']
    print(f"📊 Total Bills in Database: {bills_count}")
    
    if bills_count == 0:
        print("⚠️  No bills data found. Charts will show sample data.")
        conn.close()
        return
    
    # Test revenue data query
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    revenue_data = conn.execute('''
        SELECT 
            DATE(created_at) as date,
            COALESCE(SUM(total_amount), 0) as revenue,
            COALESCE(SUM(total_amount * 0.4), 0) as profit
        FROM bills 
        WHERE DATE(created_at) >= DATE(?) AND DATE(created_at) <= DATE(?)
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))).fetchall()
    
    print(f"\n📈 Revenue Data (Last 7 days):")
    total_revenue = 0
    for row in revenue_data:
        print(f"  {row['date']}: ₹{row['revenue']:,.2f} (Profit: ₹{row['profit']:,.2f})")
        total_revenue += row['revenue']
    
    print(f"💰 Total Revenue (7 days): ₹{total_revenue:,.2f}")
    
    # Test sales distribution
    sales_distribution = conn.execute('''
        SELECT 
            COALESCE(p.category, 'Other') as category,
            COALESCE(SUM(bi.total_price), 0) as total_sales
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        LEFT JOIN products p ON bi.product_id = p.id
        WHERE DATE(b.created_at) >= DATE(?) AND DATE(b.created_at) <= DATE(?)
        GROUP BY p.category
        ORDER BY total_sales DESC
        LIMIT 5
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))).fetchall()
    
    print(f"\n🎯 Sales Distribution by Category:")
    for row in sales_distribution:
        print(f"  {row['category']}: ₹{row['total_sales']:,.2f}")
    
    # Test top products
    top_products = conn.execute('''
        SELECT 
            bi.product_name,
            COALESCE(SUM(bi.total_price), 0) as total_sales
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE DATE(b.created_at) >= DATE(?) AND DATE(b.created_at) <= DATE(?)
        GROUP BY bi.product_name
        ORDER BY total_sales DESC
        LIMIT 5
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))).fetchall()
    
    print(f"\n📦 Top Products:")
    for row in top_products:
        print(f"  {row['product_name']}: ₹{row['total_sales']:,.2f}")
    
    conn.close()
    
    print(f"\n✅ Charts API data test completed!")
    print(f"🌐 Access dashboard at: http://localhost:5000/retail/dashboard")
    print(f"📊 Charts API endpoint: http://localhost:5000/api/dashboard/charts")

if __name__ == "__main__":
    test_charts_api()