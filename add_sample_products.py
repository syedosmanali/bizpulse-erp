#!/usr/bin/env python3
"""
Add sample products to the database for testing the redesigned product management system
"""

import sqlite3
import uuid
from datetime import datetime

def add_sample_products():
    """Add sample products to the database"""
    
    # Sample products data
    sample_products = [
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'description': 'Latest Samsung flagship smartphone with S Pen',
            'category': 'Electronics',
            'price': 75000,
            'stock': 25,
            'unit': 'piece',
            'sku': 'PHONE001',
            'barcode_data': '8901030123456',
            'image_url': '',
            'min_stock': 5,
            'max_stock': 100,
            'hsn_code': '85171200',
            'gst_rate': 18,
            'mrp': 80000,
            'purchase_price': 65000,
            'selling_price': 75000
        },
        {
            'name': 'Nike Air Max 270',
            'description': 'Premium running shoes with air cushioning',
            'category': 'Clothing',
            'price': 8500,
            'stock': 3,
            'unit': 'pair',
            'sku': 'SHOE001',
            'barcode_data': '8901030234567',
            'image_url': '',
            'min_stock': 10,
            'max_stock': 50,
            'hsn_code': '64039900',
            'gst_rate': 12,
            'mrp': 9500,
            'purchase_price': 6000,
            'selling_price': 8500
        },
        {
            'name': 'Organic Coffee Beans',
            'description': 'Premium organic arabica coffee beans',
            'category': 'Food',
            'price': 450,
            'stock': 0,
            'unit': 'kg',
            'sku': 'FOOD001',
            'barcode_data': '8901030345678',
            'image_url': '',
            'min_stock': 20,
            'max_stock': 200,
            'hsn_code': '09011100',
            'gst_rate': 5,
            'mrp': 500,
            'purchase_price': 300,
            'selling_price': 450
        },
        {
            'name': 'MacBook Pro M3',
            'description': 'Apple MacBook Pro with M3 chip, 14-inch',
            'category': 'Electronics',
            'price': 185000,
            'stock': 8,
            'unit': 'piece',
            'sku': 'LAPTOP001',
            'barcode_data': '8901030456789',
            'image_url': '',
            'min_stock': 3,
            'max_stock': 20,
            'hsn_code': '84713000',
            'gst_rate': 18,
            'mrp': 199000,
            'purchase_price': 160000,
            'selling_price': 185000
        },
        {
            'name': 'Yoga Mat Premium',
            'description': 'High-quality non-slip yoga mat',
            'category': 'Sports',
            'price': 2500,
            'stock': 15,
            'unit': 'piece',
            'sku': 'SPORT001',
            'barcode_data': '8901030567890',
            'image_url': '',
            'min_stock': 5,
            'max_stock': 30,
            'hsn_code': '95069990',
            'gst_rate': 18,
            'mrp': 3000,
            'purchase_price': 1800,
            'selling_price': 2500
        },
        {
            'name': 'Wireless Headphones',
            'description': 'Noise-cancelling wireless headphones',
            'category': 'Electronics',
            'price': 12000,
            'stock': 12,
            'unit': 'piece',
            'sku': 'AUDIO001',
            'barcode_data': '8901030678901',
            'image_url': '',
            'min_stock': 8,
            'max_stock': 40,
            'hsn_code': '85183000',
            'gst_rate': 18,
            'mrp': 15000,
            'purchase_price': 9000,
            'selling_price': 12000
        },
        {
            'name': 'Organic Green Tea',
            'description': 'Premium organic green tea leaves',
            'category': 'Food',
            'price': 350,
            'stock': 45,
            'unit': 'pack',
            'sku': 'TEA001',
            'barcode_data': '8901030789012',
            'image_url': '',
            'min_stock': 15,
            'max_stock': 100,
            'hsn_code': '09021000',
            'gst_rate': 5,
            'mrp': 400,
            'purchase_price': 250,
            'selling_price': 350
        },
        {
            'name': 'Gaming Mouse RGB',
            'description': 'High-precision gaming mouse with RGB lighting',
            'category': 'Electronics',
            'price': 3500,
            'stock': 2,
            'unit': 'piece',
            'sku': 'MOUSE001',
            'barcode_data': '8901030890123',
            'image_url': '',
            'min_stock': 5,
            'max_stock': 25,
            'hsn_code': '84716060',
            'gst_rate': 18,
            'mrp': 4000,
            'purchase_price': 2500,
            'selling_price': 3500
        },
        {
            'name': 'Vitamin C Tablets',
            'description': 'Immune support vitamin C supplements',
            'category': 'Health',
            'price': 450,
            'stock': 30,
            'unit': 'bottle',
            'sku': 'HEALTH001',
            'barcode_data': '8901030901234',
            'image_url': '',
            'min_stock': 10,
            'max_stock': 50,
            'hsn_code': '21069090',
            'gst_rate': 12,
            'mrp': 500,
            'purchase_price': 300,
            'selling_price': 450
        },
        {
            'name': 'Smart Watch Series 9',
            'description': 'Advanced fitness tracking smartwatch',
            'category': 'Electronics',
            'price': 25000,
            'stock': 6,
            'unit': 'piece',
            'sku': 'WATCH001',
            'barcode_data': '8901031012345',
            'image_url': '',
            'min_stock': 3,
            'max_stock': 15,
            'hsn_code': '91021200',
            'gst_rate': 18,
            'mrp': 28000,
            'purchase_price': 20000,
            'selling_price': 25000
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect('billing.db')
        cursor = conn.cursor()
        
        # Check if products table exists and has the required columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Existing columns: {columns}")
        
        # Add missing columns if they don't exist
        required_columns = [
            ('min_stock', 'INTEGER DEFAULT 0'),
            ('max_stock', 'INTEGER DEFAULT 0'),
            ('hsn_code', 'TEXT'),
            ('gst_rate', 'REAL DEFAULT 18'),
            ('mrp', 'REAL DEFAULT 0'),
            ('purchase_price', 'REAL DEFAULT 0'),
            ('selling_price', 'REAL DEFAULT 0')
        ]
        
        for col_name, col_def in required_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Column {col_name} might already exist: {e}")
        
        # Clear existing sample products (optional)
        cursor.execute("DELETE FROM products WHERE code LIKE 'PHONE%' OR code LIKE 'SHOE%' OR code LIKE 'FOOD%' OR code LIKE 'LAPTOP%' OR code LIKE 'SPORT%' OR code LIKE 'AUDIO%' OR code LIKE 'TEA%' OR code LIKE 'MOUSE%' OR code LIKE 'HEALTH%' OR code LIKE 'WATCH%'")
        print("🗑️ Cleared existing sample products")
        
        # Add sample products
        now = datetime.now().isoformat()
        user_id = 'sample_user'  # You can change this to match your user system
        
        for product in sample_products:
            product_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO products (
                    id, name, description, category, price, cost, stock, min_stock, unit, 
                    code, barcode_data, image_url, is_active, user_id, created_at,
                    max_stock, hsn_code, gst_rate, mrp, purchase_price, selling_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                product['name'],
                product['description'],
                product['category'],
                product['selling_price'],  # price field
                product['purchase_price'], # cost field
                product['stock'],
                product['min_stock'],
                product['unit'],
                product['sku'],  # code field
                product['barcode_data'],
                product['image_url'],
                user_id,
                now,
                product['max_stock'],
                product['hsn_code'],
                product['gst_rate'],
                product['mrp'],
                product['purchase_price'],
                product['selling_price']
            ))
            
            print(f"✅ Added: {product['name']} ({product['sku']})")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully added {len(sample_products)} sample products!")
        print("\n📊 Product Summary:")
        print("=" * 50)
        
        for product in sample_products:
            stock_status = "🟢 In Stock" if product['stock'] > product['min_stock'] else "🟡 Low Stock" if product['stock'] > 0 else "🔴 Out of Stock"
            print(f"{product['name']:<25} | {product['sku']:<10} | Stock: {product['stock']:>3} | {stock_status}")
        
        print("\n🌐 Access your redesigned product management at:")
        print("   http://localhost:5000/retail/products")
        print("   http://localhost:5000/retail/inventory")
        
    except Exception as e:
        print(f"❌ Error adding sample products: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Adding Sample Products to Database")
    print("=" * 50)
    add_sample_products()