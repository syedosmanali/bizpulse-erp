#!/usr/bin/env python3
"""
Complete fix for sales data issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_db_connection
from datetime import datetime
from uuid import uuid4

def fix_sales_data_issues():
    """Fix all sales data issues"""
    
    print("🔧 Fixing Sales Data Issues")
    print("=" * 50)
    
    conn = get_db_connection()
    
    # 1. Fix sales entries with None values
    print("1. Fixing sales entries with None values...")
    
    sales_with_none = conn.execute('''
        SELECT s.*, bi.product_name as bill_item_name, bi.total_price as bill_item_price
        FROM sales s
        LEFT JOIN bill_items bi ON s.bill_id = bi.bill_id AND s.product_id = bi.product_id
        WHERE s.product_name IS NULL OR s.total_price IS NULL
    ''').fetchall()
    
    if sales_with_none:
        print(f"   Found {len(sales_with_none)} sales entries with None values")
        
        try:
            conn.execute('BEGIN TRANSACTION')
            
            for sale in sales_with_none:
                # Update with correct values from bill_items
                conn.execute('''
                    UPDATE sales 
                    SET product_name = COALESCE(?, product_name),
                        total_price = COALESCE(?, total_price)
                    WHERE id = ?
                ''', (sale['bill_item_name'], sale['bill_item_price'], sale['id']))
                
                print(f"   ✅ Fixed sale {sale['id'][:8]}... - {sale['bill_item_name']} - ₹{sale['bill_item_price']}")
            
            conn.commit()
            print(f"   🎉 Successfully fixed {len(sales_with_none)} sales entries")
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Failed to fix sales entries: {str(e)}")
    else:
        print("   ✅ No sales entries with None values found")
    
    # 2. Ensure all bills have corresponding sales entries
    print("\n2. Ensuring all bills have sales entries...")
    
    bills_without_sales = conn.execute('''
        SELECT b.*, bi.product_id, bi.product_name, bi.quantity, bi.unit_price, bi.total_price
        FROM bills b
        LEFT JOIN sales s ON b.id = s.bill_id
        LEFT JOIN bill_items bi ON b.id = bi.bill_id
        WHERE s.id IS NULL AND bi.id IS NOT NULL
    ''').fetchall()
    
    if bills_without_sales:
        print(f"   Found {len(bills_without_sales)} bill items without sales entries")
        
        try:
            conn.execute('BEGIN TRANSACTION')
            
            for bill_item in bills_without_sales:
                # Create missing sales entry
                sale_id = str(uuid4())
                created_at = bill_item['created_at'] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sale_date = created_at.split(' ')[0]  # Extract date part
                sale_time = created_at.split(' ')[1] if ' ' in created_at else '00:00:00'
                
                # Get product category
                product = conn.execute('SELECT category FROM products WHERE id = ?', (bill_item['product_id'],)).fetchone()
                category = product['category'] if product else 'General'
                
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
                
                print(f"   ✅ Created sales entry for {bill_item['bill_number']} - {bill_item['product_name']}")
            
            conn.commit()
            print(f"   🎉 Successfully created {len(bills_without_sales)} missing sales entries")
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Failed to create sales entries: {str(e)}")
    else:
        print("   ✅ All bills have corresponding sales entries")
    
    # 3. Verify data integrity
    print("\n3. Verifying data integrity...")
    
    # Check today's data
    today = datetime.now().strftime('%Y-%m-%d')
    
    bills_count = conn.execute('SELECT COUNT(*) as count FROM bills WHERE DATE(created_at) = ?', (today,)).fetchone()['count']
    sales_count = conn.execute('SELECT COUNT(*) as count FROM sales WHERE DATE(created_at) = ?', (today,)).fetchone()['count']
    
    print(f"   📋 Bills today: {bills_count}")
    print(f"   💰 Sales entries today: {sales_count}")
    
    if sales_count >= bills_count:
        print("   ✅ Data integrity check passed")
    else:
        print("   ⚠️ Sales entries less than bills - may need further investigation")
    
    # 4. Test sales API
    print("\n4. Testing sales API...")
    
    from app import app
    with app.test_client() as client:
        response = client.get('/api/sales/all?filter=today')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                api_sales_count = len(data.get('sales', []))
                total_sales = data.get('summary', {}).get('total_sales', 0)
                print(f"   ✅ Sales API working: {api_sales_count} records, ₹{total_sales} total")
            else:
                print("   ❌ Sales API returned success=false")
        else:
            print(f"   ❌ Sales API failed: {response.status_code}")
    
    conn.close()
    print("\n🎉 Sales data fix complete!")

if __name__ == "__main__":
    fix_sales_data_issues()