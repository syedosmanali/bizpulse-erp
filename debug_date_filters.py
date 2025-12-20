#!/usr/bin/env python3
"""
Debug date filters by directly testing the database queries
"""
import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('billing.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_date_queries():
    """Test date filtering queries directly"""
    print("🔍 Testing Date Filter Queries...")
    print("=" * 50)
    
    # Get current date (assuming IST)
    now = datetime.now()
    
    # Calculate date ranges
    today = now.strftime('%Y-%m-%d')
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
    month_start = now.replace(day=1).strftime('%Y-%m-%d')
    
    print(f"📅 Today: {today}")
    print(f"📅 Yesterday: {yesterday}")
    print(f"📅 Week Start: {week_start}")
    print(f"📅 Month Start: {month_start}")
    
    conn = get_db_connection()
    
    # Test queries
    test_cases = [
        ("TODAY", f"DATE(created_at) = '{today}'"),
        ("YESTERDAY", f"DATE(created_at) = '{yesterday}'"),
        ("THIS WEEK", f"DATE(created_at) BETWEEN '{week_start}' AND '{today}'"),
        ("THIS MONTH", f"DATE(created_at) BETWEEN '{month_start}' AND '{today}'"),
        ("ALL RECORDS", "1=1")
    ]
    
    for test_name, where_clause in test_cases:
        print(f"\n🧪 Testing {test_name}:")
        print(f"   Query: WHERE {where_clause}")
        
        try:
            # Count records
            count_query = f"SELECT COUNT(*) as count FROM sales WHERE {where_clause}"
            count_result = conn.execute(count_query).fetchone()
            record_count = count_result['count'] if count_result else 0
            
            # Sum total sales
            sum_query = f"SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE {where_clause}"
            sum_result = conn.execute(sum_query).fetchone()
            total_sales = sum_result['total'] if sum_result else 0
            
            print(f"   📊 Records: {record_count}")
            print(f"   💰 Total: ₹{total_sales:,.2f}")
            
            # Show sample records
            if record_count > 0:
                sample_query = f"""
                    SELECT bill_number, product_name, total_price, created_at 
                    FROM sales 
                    WHERE {where_clause} 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """
                samples = conn.execute(sample_query).fetchall()
                print(f"   📋 Sample Records:")
                for i, sample in enumerate(samples, 1):
                    print(f"      {i}. Bill #{sample['bill_number']} - {sample['product_name']} - ₹{sample['total_price']} - {sample['created_at']}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    conn.close()

def check_data_integrity():
    """Check for data integrity issues"""
    print(f"\n🔍 Checking Data Integrity...")
    print("=" * 30)
    
    conn = get_db_connection()
    
    # Check for None/NULL values
    checks = [
        ("NULL total_price", "total_price IS NULL"),
        ("NULL product_name", "product_name IS NULL"),
        ("NULL created_at", "created_at IS NULL"),
        ("Invalid total_price", "total_price <= 0"),
        ("Empty product_name", "product_name = '' OR product_name = 'None'")
    ]
    
    for check_name, condition in checks:
        try:
            query = f"SELECT COUNT(*) as count FROM sales WHERE {condition}"
            result = conn.execute(query).fetchone()
            count = result['count'] if result else 0
            
            if count > 0:
                print(f"⚠️  {check_name}: {count} records")
                
                # Show samples
                sample_query = f"SELECT id, bill_number, product_name, total_price, created_at FROM sales WHERE {condition} LIMIT 3"
                samples = conn.execute(sample_query).fetchall()
                for sample in samples:
                    print(f"   ID: {sample['id']}, Bill: {sample['bill_number']}, Product: {sample['product_name']}, Price: {sample['total_price']}")
            else:
                print(f"✅ {check_name}: Clean")
                
        except Exception as e:
            print(f"❌ Error checking {check_name}: {str(e)}")
    
    conn.close()

def main():
    """Main function"""
    print("🚀 Date Filter Debug Tool")
    print("=" * 50)
    
    test_date_queries()
    check_data_integrity()
    
    print(f"\n✅ Debug complete!")

if __name__ == "__main__":
    main()