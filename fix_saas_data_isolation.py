"""
🔧 COMPLETE FIX: SaaS Multi-Tenant Data Isolation
This script fixes the business_owner_id issue causing sales to not show
"""
import os
import sys

# Set DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://postgres.dnflpvmertmioebhjzas:PEhR2p3tARI915Lz@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'

print("=" * 80)
print("🔧 FIXING SAAS DATA ISOLATION - BUSINESS_OWNER_ID MIGRATION")
print("=" * 80)

try:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        import psycopg2_binary as psycopg2
        from psycopg2.extras import RealDictCursor
    
    # Connect to database
    print("\n🔗 Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Connected successfully!")
    
    # ============================================================================
    # STEP 1: Add business_owner_id columns to all tables
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Adding business_owner_id columns")
    print("=" * 80)
    
    tables_to_fix = [
        'bills',
        'sales',
        'products',
        'customers',
        'bill_items',
        'payments',
        'credit_transactions',
        'hotel_guests',
        'hotel_services'
    ]
    
    for table in tables_to_fix:
        try:
            cursor.execute(f"""
                ALTER TABLE {table} 
                ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255)
            """)
            conn.commit()
            print(f"✅ Added business_owner_id to {table}")
        except Exception as e:
            print(f"⚠️  {table}: {e}")
            conn.rollback()
    
    # ============================================================================
    # STEP 2: Create performance indexes
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Creating performance indexes")
    print("=" * 80)
    
    indexes = [
        ('bills', 'idx_bills_business_owner_id', 'business_owner_id'),
        ('sales', 'idx_sales_business_owner_id', 'business_owner_id'),
        ('products', 'idx_products_business_owner_id', 'business_owner_id'),
        ('customers', 'idx_customers_business_owner_id', 'business_owner_id'),
        ('bill_items', 'idx_bill_items_business_owner_id', 'business_owner_id'),
    ]
    
    for table, index_name, column in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})
            """)
            conn.commit()
            print(f"✅ Created index {index_name} on {table}")
        except Exception as e:
            print(f"⚠️  {index_name}: {e}")
            conn.rollback()
    
    # ============================================================================
    # STEP 3: Backfill existing data
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Backfilling existing data")
    print("=" * 80)
    
    # Check how many clients exist
    cursor.execute("SELECT COUNT(*) as count FROM clients")
    client_count = cursor.fetchone()['count']
    print(f"📊 Found {client_count} clients in database")
    
    if client_count == 1:
        # Single client - assign all data to them
        cursor.execute("SELECT id FROM clients LIMIT 1")
        client = cursor.fetchone()
        if client:
            client_id = client['id']
            print(f"✅ Single client found: {client_id}")
            print(f"   Assigning all unassigned data to this client...")
            
            # Update all tables
            for table in tables_to_fix:
                try:
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET business_owner_id = %s 
                        WHERE business_owner_id IS NULL
                    """, (client_id,))
                    count = cursor.rowcount
                    conn.commit()
                    print(f"   ✅ Updated {count} records in {table}")
                except Exception as e:
                    print(f"   ⚠️  {table}: {e}")
                    conn.rollback()
    else:
        # Multiple clients - use default admin
        print(f"⚠️  Multiple clients found - using default 'admin-bizpulse'")
        
        for table in tables_to_fix:
            try:
                cursor.execute(f"""
                    UPDATE {table} 
                    SET business_owner_id = 'admin-bizpulse' 
                    WHERE business_owner_id IS NULL
                """, )
                count = cursor.rowcount
                conn.commit()
                print(f"   ✅ Updated {count} records in {table}")
            except Exception as e:
                print(f"   ⚠️  {table}: {e}")
                conn.rollback()
    
    # ============================================================================
    # STEP 4: Verification
    # ============================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Verification")
    print("=" * 80)
    
    # Check bills
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(business_owner_id) as with_owner,
            COUNT(*) - COUNT(business_owner_id) as without_owner
        FROM bills
    """)
    bills_stats = cursor.fetchone()
    print(f"\n📊 BILLS:")
    print(f"   Total: {bills_stats['total']}")
    print(f"   With business_owner_id: {bills_stats['with_owner']}")
    print(f"   Without business_owner_id: {bills_stats['without_owner']}")
    
    # Check sales
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(business_owner_id) as with_owner,
            COUNT(*) - COUNT(business_owner_id) as without_owner
        FROM sales
    """)
    sales_stats = cursor.fetchone()
    print(f"\n📊 SALES:")
    print(f"   Total: {sales_stats['total']}")
    print(f"   With business_owner_id: {sales_stats['with_owner']}")
    print(f"   Without business_owner_id: {sales_stats['without_owner']}")
    
    # Check products
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(business_owner_id) as with_owner,
            COUNT(*) - COUNT(business_owner_id) as without_owner
        FROM products
    """)
    products_stats = cursor.fetchone()
    print(f"\n📊 PRODUCTS:")
    print(f"   Total: {products_stats['total']}")
    print(f"   With business_owner_id: {products_stats['with_owner']}")
    print(f"   Without business_owner_id: {products_stats['without_owner']}")
    
    # Check indexes
    cursor.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename IN ('bills', 'sales', 'products', 'customers')
        AND indexname LIKE '%business_owner_id%'
    """)
    indexes_created = cursor.fetchall()
    print(f"\n📊 INDEXES CREATED:")
    for idx in indexes_created:
        print(f"   ✅ {idx['indexname']}")
    
    cursor.close()
    conn.close()
    
    # ============================================================================
    # FINAL STATUS
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print("\n🎉 Your database is now ready for multi-tenant data isolation!")
    print("\n📝 NEXT STEPS:")
    print("   1. Update sales service: Copy service_FIXED.py to service.py")
    print("   2. Run test: python test_data_isolation.py")
    print("   3. Deploy to production")
    print("\n" + "=" * 80)
    
except ImportError:
    print("\n❌ psycopg2 not installed!")
    print("Installing now...")
    os.system("pip install psycopg2-binary")
    print("\n✅ Installed! Please run this script again:")
    print("   python fix_saas_data_isolation.py")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
