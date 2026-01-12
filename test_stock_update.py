#!/usr/bin/env python3

import sqlite3
import sys

def test_stock_update():
    try:
        conn = sqlite3.connect('billing.db')
        cursor = conn.cursor()
        
        # Find rice product
        cursor.execute("SELECT id, name, stock FROM products WHERE name LIKE '%rice%' LIMIT 1")
        product = cursor.fetchone()
        
        if not product:
            print("No rice product found")
            return
            
        product_id, name, current_stock = product
        print(f"Found product: {name} (ID: {product_id}) with stock: {current_stock}")
        
        # Test update
        new_stock = current_stock - 1
        print(f"Updating stock from {current_stock} to {new_stock}")
        
        cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        updated_stock = cursor.fetchone()[0]
        
        print(f"Stock after update: {updated_stock}")
        
        if updated_stock == new_stock:
            print("✅ Stock update successful!")
        else:
            print("❌ Stock update failed!")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stock_update()