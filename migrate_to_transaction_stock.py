#!/usr/bin/env python3
"""
Migration Script: Convert to Transaction-Based Stock System
This script safely migrates from products.stock to transaction-based stock tracking
"""

import sqlite3
import sys
from datetime import datetime
from modules.shared.database import get_db_connection, generate_id
from modules.stock.database import init_stock_tables, migrate_existing_stock_data

def main():
    print("🚀 Starting migration to transaction-based stock system...")
    print("=" * 60)
    
    try:
        # Step 1: Initialize new stock tables
        print("📋 Step 1: Creating new stock management tables...")
        init_stock_tables()
        print("✅ Stock tables created successfully")
        
        # Step 2: Migrate existing stock data
        print("\n📦 Step 2: Migrating existing stock data...")
        migrated_count = migrate_existing_stock_data()
        print(f"✅ Migrated {migrated_count} products with stock data")
        
        # Step 3: Verify migration
        print("\n🔍 Step 3: Verifying migration...")
        conn = get_db_connection()
        
        # Check products with stock
        products_with_stock = conn.execute("""
            SELECT COUNT(*) as count FROM products 
            WHERE stock > 0 AND is_active = 1
        """).fetchone()
        
        # Check stock transactions created
        opening_transactions = conn.execute("""
            SELECT COUNT(*) as count FROM stock_transactions 
            WHERE reference_type = 'opening'
        """).fetchone()
        
        # Check current_stock records
        current_stock_records = conn.execute("""
            SELECT COUNT(*) as count FROM current_stock
        """).fetchone()
        
        print(f"   Products with stock: {products_with_stock[0] if products_with_stock else 0}")
        print(f"   Opening transactions: {opening_transactions[0] if opening_transactions else 0}")
        print(f"   Current stock records: {current_stock_records[0] if current_stock_records else 0}")
        
        # Step 4: Test stock calculation
        print("\n🧮 Step 4: Testing stock calculations...")
        test_products = conn.execute("""
            SELECT p.id, p.name, p.stock as old_stock, cs.current_quantity as new_stock
            FROM products p
            LEFT JOIN current_stock cs ON p.id = cs.product_id
            WHERE p.stock > 0 AND p.is_active = 1
            LIMIT 5
        """).fetchall()
        
        all_match = True
        for product in test_products:
            old_stock = product[2] or 0
            new_stock = product[3] or 0
            match = "✅" if old_stock == new_stock else "❌"
            print(f"   {match} {product[1]}: Old={old_stock}, New={new_stock}")
            if old_stock != new_stock:
                all_match = False
        
        conn.close()
        
        if all_match:
            print("\n🎉 Migration completed successfully!")
            print("✅ All stock quantities match between old and new systems")
        else:
            print("\n⚠️ Migration completed with some discrepancies")
            print("   Please review the stock quantities above")
        
        print("\n📝 Next Steps:")
        print("1. Test the billing system to ensure stock reduction works")
        print("2. Use the new stock management APIs to add/adjust stock")
        print("3. Monitor the system for any issues")
        print("4. Once confident, you can remove the 'stock' column from products table")
        
        print("\n🔧 New API Endpoints Available:")
        print("   POST /api/stock/add-purchase - Add stock from purchases")
        print("   POST /api/stock/adjust - Adjust stock quantities")
        print("   GET /api/stock/history - View stock transaction history")
        print("   GET /api/stock/summary - Get stock summary")
        print("   GET /api/stock/low-stock - Get low stock alerts")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("Please check the error and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()