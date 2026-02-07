"""
Direct database check to see if sales are being stored
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres')

print("🔍 Checking sales data in Supabase...")

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check bills
    print("\n📊 Bills Table:")
    cursor.execute("SELECT COUNT(*) as count FROM bills")
    bills_count = cursor.fetchone()['count']
    print(f"   Total bills: {bills_count}")
    
    cursor.execute("SELECT bill_number, customer_name, total_amount, created_at FROM bills ORDER BY created_at DESC LIMIT 5")
    recent_bills = cursor.fetchall()
    print(f"   Recent bills:")
    for bill in recent_bills:
        print(f"      - {bill['bill_number']}: ₹{bill['total_amount']} ({bill['customer_name']}) - {bill['created_at']}")
    
    # Check sales
    print("\n💰 Sales Table:")
    cursor.execute("SELECT COUNT(*) as count FROM sales")
    sales_count = cursor.fetchone()['count']
    print(f"   Total sales: {sales_count}")
    
    cursor.execute("SELECT bill_number, product_name, quantity, total_price, created_at FROM sales ORDER BY created_at DESC LIMIT 5")
    recent_sales = cursor.fetchall()
    print(f"   Recent sales:")
    for sale in recent_sales:
        print(f"      - {sale['bill_number']}: {sale['product_name']} x{sale['quantity']} = ₹{sale['total_price']} - {sale['created_at']}")
    
    # Check bill_items
    print("\n📦 Bill Items Table:")
    cursor.execute("SELECT COUNT(*) as count FROM bill_items")
    items_count = cursor.fetchone()['count']
    print(f"   Total bill items: {items_count}")
    
    cursor.execute("SELECT bi.product_name, bi.quantity, bi.total_price, b.bill_number FROM bill_items bi JOIN bills b ON bi.bill_id = b.id ORDER BY bi.id DESC LIMIT 5")
    recent_items = cursor.fetchall()
    print(f"   Recent items:")
    for item in recent_items:
        print(f"      - {item['bill_number']}: {item['product_name']} x{item['quantity']} = ₹{item['total_price']}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Database check complete!")
    print(f"\nSummary:")
    print(f"   Bills: {bills_count}")
    print(f"   Sales: {sales_count}")
    print(f"   Bill Items: {items_count}")
    
    if bills_count > 0 and sales_count > 0:
        print("\n✅ Data is being stored correctly!")
    elif bills_count > 0 and sales_count == 0:
        print("\n⚠️  Bills are created but sales entries are missing!")
    else:
        print("\n❌ No data found!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
