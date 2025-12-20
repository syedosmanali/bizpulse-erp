#!/usr/bin/env python3
"""
Debug why bills created today are not showing in sales module
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, get_db_connection
from datetime import datetime

def debug_bills_sales_sync():
    """Debug the sync between bills and sales"""
    
    print("🔍 Debugging Bills vs Sales Sync Issue")
    print("=" * 60)
    
    conn = get_db_connection()
    
    # Check today's date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today's date: {today}")
    
    # 1. Check bills created today
    print(f"\n📋 Bills created today ({today}):")
    bills_today = conn.execute('''
        SELECT id, bill_number, total_amount, created_at, customer_id
        FROM bills 
        WHERE DATE(created_at) = ?
        ORDER BY created_at DESC
    ''', (today,)).fetchall()
    
    if bills_today:
        for bill in bills_today:
            print(f"   ✅ {bill['bill_number']} - ₹{bill['total_amount']} - {bill['created_at']}")
    else:
        print("   ❌ No bills found for today")
    
    # 2. Check sales entries for today
    print(f"\n💰 Sales entries for today ({today}):")
    sales_today = conn.execute('''
        SELECT id, bill_number, product_name, total_price, created_at, sale_date
        FROM sales 
        WHERE DATE(created_at) = ? OR sale_date = ?
        ORDER BY created_at DESC
    ''', (today, today)).fetchall()
    
    if sales_today:
        for sale in sales_today:
            print(f"   ✅ {sale['bill_number']} - {sale['product_name']} - ₹{sale['total_price']} - {sale['created_at']}")
    else:
        print("   ❌ No sales entries found for today")
    
    # 3. Check for orphaned bills (bills without sales entries)
    print(f"\n🔍 Checking for orphaned bills (bills without sales entries):")
    orphaned_bills = conn.execute('''
        SELECT b.id, b.bill_number, b.total_amount, b.created_at
        FROM bills b
        LEFT JOIN sales s ON b.id = s.bill_id
        WHERE DATE(b.created_at) = ? AND s.id IS NULL
    ''', (today,)).fetchall()
    
    if orphaned_bills:
        print("   ❌ Found orphaned bills (bills without sales entries):")
        for bill in orphaned_bills:
            print(f"      🚨 {bill['bill_number']} - ₹{bill['total_amount']} - {bill['created_at']}")
    else:
        print("   ✅ No orphaned bills found")
    
    # 4. Check sales API response
    print(f"\n🔍 Testing Sales API for today:")
    with app.test_client() as client:
        response = client.get('/api/sales/all?filter=today')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                sales_count = len(data.get('sales', []))
                total_sales = data.get('summary', {}).get('total_sales', 0)
                print(f"   ✅ Sales API working: {sales_count} records, ₹{total_sales} total")
                
                if sales_count > 0:
                    print("   📊 Sample sales data:")
                    for i, sale in enumerate(data['sales'][:3]):
                        print(f"      {i+1}. {sale.get('bill_number', 'N/A')} - {sale.get('product_name', 'N/A')} - ₹{sale.get('total_amount', 0)}")
                else:
                    print("   ❌ No sales data returned by API")
            else:
                print(f"   ❌ Sales API returned success=false")
        else:
            print(f"   ❌ Sales API failed: {response.status_code}")
    
    # 5. Check invoice API response
    print(f"\n🔍 Testing Invoice API:")
    with app.test_client() as client:
        response = client.get('/api/invoices')
        if response.status_code == 200:
            invoices = response.get_json()
            today_invoices = [inv for inv in invoices if inv.get('created_at', '').startswith(today)]
            print(f"   ✅ Invoice API working: {len(today_invoices)} invoices for today")
            
            if today_invoices:
                print("   📋 Today's invoices:")
                for inv in today_invoices[:3]:
                    print(f"      - {inv.get('bill_number', 'N/A')} - ₹{inv.get('total_amount', 0)}")
        else:
            print(f"   ❌ Invoice API failed: {response.status_code}")
    
    conn.close()

def fix_orphaned_bills():
    """Fix orphaned bills by creating missing sales entries"""
    
    print(f"\n🔧 Attempting to fix orphaned bills...")
    
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Find orphaned bills
    orphaned_bills = conn.execute('''
        SELECT b.*, bi.product_id, bi.product_name, bi.quantity, bi.unit_price, bi.total_price
        FROM bills b
        LEFT JOIN sales s ON b.id = s.bill_id
        LEFT JOIN bill_items bi ON b.id = bi.bill_id
        WHERE DATE(b.created_at) = ? AND s.id IS NULL
    ''', (today,)).fetchall()
    
    if not orphaned_bills:
        print("   ✅ No orphaned bills to fix")
        conn.close()
        return
    
    print(f"   🔧 Found {len(orphaned_bills)} orphaned bill items to fix")
    
    try:
        conn.execute('BEGIN TRANSACTION')
        
        for bill_item in orphaned_bills:
            # Generate sales entry
            from uuid import uuid4
            sale_id = str(uuid4())
            sale_date = datetime.now().strftime('%Y-%m-%d')
            sale_time = datetime.now().strftime('%H:%M:%S')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get product category
            product = conn.execute('SELECT category FROM products WHERE id = ?', (bill_item['product_id'],)).fetchone()
            category = product['category'] if product else 'General'
            
            # Create sales entry
            conn.execute('''
                INSERT INTO sales (
                    id, bill_id, bill_number, customer_id, customer_name,
                    product_id, product_name, category, quantity, unit_price,
                    total_price, tax_amount, discount_amount, payment_method,
                    sale_date, sale_time, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sale_id, bill_item['id'], bill_item['bill_number'], 
                bill_item['customer_id'], 'Walk-in Customer',
                bill_item['product_id'], bill_item['product_name'], category,
                bill_item['quantity'], bill_item['unit_price'], bill_item['total_price'],
                0, 0, 'cash', sale_date, sale_time, created_at
            ))
            
            print(f"   ✅ Created sales entry for {bill_item['bill_number']}")
        
        conn.commit()
        print(f"   🎉 Successfully fixed {len(orphaned_bills)} orphaned bills")
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Failed to fix orphaned bills: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    debug_bills_sales_sync()
    fix_orphaned_bills()
    
    print(f"\n🔄 Re-checking after fix...")
    debug_bills_sales_sync()