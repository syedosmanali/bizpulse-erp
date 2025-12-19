#!/usr/bin/env python3
"""
Simple test to verify pagination implementation
"""
import sqlite3
import json

def test_pagination_logic():
    print("🧪 Testing Pagination Logic...")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    
    # Test the pagination query
    page = 1
    per_page = 10
    status = 'all'
    
    # Base query
    query = '''
        SELECT b.*, c.name as customer_name, c.phone as customer_phone
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
    '''
    
    # Count query
    count_query = '''
        SELECT COUNT(*) as total
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
    '''
    
    params = []
    where_conditions = []
    
    # Status filter
    if status != 'all':
        where_conditions.append('b.status = ?')
        params.append(status)
    
    # Add WHERE clause if conditions exist
    if where_conditions:
        where_clause = ' WHERE ' + ' AND '.join(where_conditions)
        query += where_clause
        count_query += where_clause
    
    # Get total count
    total_records = conn.execute(count_query, params).fetchone()['total']
    print(f"📊 Total Records: {total_records}")
    
    # Add pagination
    offset = (page - 1) * per_page
    query += ' ORDER BY b.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    invoices = conn.execute(query, params).fetchall()
    
    # Calculate pagination info
    total_pages = (total_records + per_page - 1) // per_page
    
    print(f"📄 Total Pages: {total_pages}")
    print(f"📋 Current Page: {page}")
    print(f"📦 Items on this page: {len(invoices)}")
    print(f"🔄 Has Next: {page < total_pages}")
    print(f"🔄 Has Previous: {page > 1}")
    
    if invoices:
        print(f"\n🧾 Sample Invoices:")
        for i, invoice in enumerate(invoices[:3]):  # Show first 3
            print(f"  {i+1}. {invoice['bill_number']} - ₹{invoice['total_amount']} - {invoice['customer_name'] or 'Walk-in'}")
    
    conn.close()
    
    print("\n✅ Pagination logic test completed!")
    
    # Test page 2 if available
    if total_pages > 1:
        print(f"\n📄 Testing Page 2...")
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        page = 2
        offset = (page - 1) * per_page
        
        query = '''
            SELECT b.*, c.name as customer_name, c.phone as customer_phone
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.id
            ORDER BY b.created_at DESC LIMIT ? OFFSET ?
        '''
        
        invoices_page2 = conn.execute(query, [per_page, offset]).fetchall()
        print(f"📦 Items on page 2: {len(invoices_page2)}")
        
        if invoices_page2:
            print(f"🧾 First invoice on page 2: {invoices_page2[0]['bill_number']}")
        
        conn.close()

if __name__ == "__main__":
    test_pagination_logic()