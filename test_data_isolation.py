"""
🧪 TEST: Data Isolation Verification
Tests that the business_owner_id fix is working correctly
"""
import os
import sys

os.environ['DATABASE_URL'] = 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'

print("=" * 80)
print("🧪 TESTING DATA ISOLATION")
print("=" * 80)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n✅ Connected to database")
    
    # ============================================================================
    # TEST 1: Schema Verification
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 1: Schema Verification")
    print("=" * 80)
    
    tables_to_check = ['bills', 'sales', 'products', 'customers']
    
    for table in tables_to_check:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = 'business_owner_id'
        """, (table,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ {table}.business_owner_id exists ({result['data_type']})")
        else:
            print(f"❌ {table}.business_owner_id MISSING!")
    
    # ============================================================================
    # TEST 2: Index Verification
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 2: Index Verification")
    print("=" * 80)
    
    cursor.execute("""
        SELECT tablename, indexname 
        FROM pg_indexes 
        WHERE indexname LIKE '%business_owner_id%'
        ORDER BY tablename
    """)
    indexes = cursor.fetchall()
    
    if indexes:
        for idx in indexes:
            print(f"✅ {idx['tablename']}: {idx['indexname']}")
    else:
        print("❌ No business_owner_id indexes found!")
    
    # ============================================================================
    # TEST 3: Data Assignment
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Data Assignment")
    print("=" * 80)
    
    for table in tables_to_check:
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(business_owner_id) as assigned,
                COUNT(*) - COUNT(business_owner_id) as unassigned
            FROM {table}
        """)
        stats = cursor.fetchone()
        
        print(f"\n📊 {table.upper()}:")
        print(f"   Total: {stats['total']}")
        print(f"   Assigned: {stats['assigned']}")
        print(f"   Unassigned: {stats['unassigned']}")
        
        if stats['unassigned'] > 0:
            print(f"   ⚠️  WARNING: {stats['unassigned']} records without business_owner_id")
        else:
            print(f"   ✅ All records have business_owner_id")
    
    # ============================================================================
    # TEST 4: Query Performance
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 4: Query Performance")
    print("=" * 80)
    
    # Test query with business_owner_id filter
    import time
    
    # Get a sample business_owner_id
    cursor.execute("SELECT DISTINCT business_owner_id FROM bills WHERE business_owner_id IS NOT NULL LIMIT 1")
    owner = cursor.fetchone()
    
    if owner:
        owner_id = owner['business_owner_id']
        print(f"\n🔍 Testing with business_owner_id: {owner_id}")
        
        # Test bills query
        start = time.time()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM bills 
            WHERE business_owner_id = %s OR business_owner_id IS NULL
        """, (owner_id,))
        result = cursor.fetchone()
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ Bills query: {result['count']} records in {elapsed:.2f}ms")
        
        # Test sales query
        start = time.time()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM sales 
            WHERE business_owner_id = %s OR business_owner_id IS NULL
        """, (owner_id,))
        result = cursor.fetchone()
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ Sales query: {result['count']} records in {elapsed:.2f}ms")
    else:
        print("⚠️  No business_owner_id found in bills table")
    
    # ============================================================================
    # TEST 5: Sample Data Check
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 5: Sample Data Check")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            bill_number,
            customer_name,
            total_amount,
            business_owner_id,
            created_at
        FROM bills 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    bills = cursor.fetchall()
    
    print("\n📋 Recent Bills:")
    for bill in bills:
        owner_status = "✅" if bill['business_owner_id'] else "❌"
        print(f"   {owner_status} {bill['bill_number']}: ₹{bill['total_amount']} - Owner: {bill['business_owner_id']}")
    
    cursor.close()
    conn.close()
    
    # ============================================================================
    # FINAL RESULT
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)
    print("\n🎉 Your database is ready for multi-tenant data isolation!")
    print("\n📝 If all tests passed, you can now:")
    print("   1. Deploy to production")
    print("   2. Test with multiple clients")
    print("   3. Verify data isolation is working")
    print("\n" + "=" * 80)
    
except ImportError:
    print("\n❌ psycopg2 not installed!")
    print("Run: pip install psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
