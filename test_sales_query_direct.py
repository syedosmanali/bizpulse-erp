"""
Test the exact sales query that's failing
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres')

print("🔍 Testing sales query...")

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test the FIXED query
    print("\n📊 Testing with CAST:")
    query = """
        SELECT 
            b.id,
            b.id as bill_id,
            b.bill_number,
            b.customer_id,
            COALESCE(b.customer_name, c.name, 'Walk-in Customer') as customer_name,
            b.total_amount,
            b.total_amount as total_price,
            b.subtotal,
            b.tax_amount,
            b.discount_amount,
            b.payment_method,
            b.payment_status,
            b.is_credit,
            b.credit_balance,
            b.credit_paid_amount,
            CAST(b.created_at AS DATE) as sale_date,
            CAST(b.created_at AS TIME) as sale_time,
            b.created_at,
            b.business_type,
            b.status,
            COALESCE(
                (SELECT STRING_AGG(bi.product_name, ', ') FROM bill_items bi WHERE bi.bill_id = b.id),
                'Multiple Items'
            ) as products,
            (SELECT SUM(bi.quantity) FROM bill_items bi WHERE bi.bill_id = b.id) as quantity,
            (SELECT COUNT(*) FROM bill_items bi WHERE bi.bill_id = b.id) as items_count,
            CASE 
                WHEN b.is_credit = TRUE AND b.credit_balance > 0 THEN 'due'
                WHEN b.payment_method = 'partial' THEN 'partial'
                WHEN b.payment_method = 'credit' THEN 'due'
                ELSE 'completed'
            END as transaction_status
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        WHERE b.business_owner_id = 'admin-bizpulse'
        ORDER BY b.created_at DESC
        LIMIT 10
    """
    
    cursor.execute(query)
    sales = cursor.fetchall()
    
    print(f"✅ Query successful! Found {len(sales)} sales")
    for sale in sales[:5]:
        print(f"   - {sale['bill_number']}: {sale['customer_name']} - ₹{sale['total_amount']}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Query works perfectly!")
    
except Exception as e:
    print(f"\n❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
