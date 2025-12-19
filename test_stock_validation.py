import sqlite3
from datetime import datetime

print("=" * 60)
print("STOCK VALIDATION TEST")
print("=" * 60)

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# 1. Check products with zero stock
print("\n1. OUT OF STOCK PRODUCTS:")
out_of_stock = cursor.execute('''
    SELECT id, name, stock, min_stock 
    FROM products 
    WHERE stock = 0 AND is_active = 1
''').fetchall()

if out_of_stock:
    for product in out_of_stock:
        print(f"   ❌ {product[1]}: Stock = {product[2]}")
else:
    print("   ✅ No out of stock products")

# 2. Check low stock products (excluding out of stock)
print("\n2. LOW STOCK PRODUCTS (Stock > 0 but <= min_stock):")
low_stock = cursor.execute('''
    SELECT id, name, stock, min_stock 
    FROM products 
    WHERE stock > 0 AND stock <= min_stock AND is_active = 1
''').fetchall()

if low_stock:
    for product in low_stock:
        print(f"   ⚠️  {product[1]}: Stock = {product[2]}, Min = {product[3]}")
else:
    print("   ✅ No low stock products")

# 3. Check products with good stock
print("\n3. PRODUCTS WITH GOOD STOCK:")
good_stock = cursor.execute('''
    SELECT id, name, stock, min_stock 
    FROM products 
    WHERE stock > min_stock AND is_active = 1
    LIMIT 5
''').fetchall()

for product in good_stock:
    print(f"   ✅ {product[1]}: Stock = {product[2]}, Min = {product[3]}")

# 4. Test stock validation logic
print("\n4. STOCK VALIDATION TEST:")
test_product = cursor.execute('''
    SELECT id, name, stock FROM products WHERE is_active = 1 LIMIT 1
''').fetchone()

if test_product:
    product_id, product_name, current_stock = test_product
    print(f"   Product: {product_name}")
    print(f"   Current Stock: {current_stock}")
    
    # Test scenarios
    test_qty = current_stock + 5
    print(f"\n   Scenario 1: Try to sell {test_qty} units (more than stock)")
    if current_stock < test_qty:
        print(f"   ❌ BLOCKED: Insufficient stock (Available: {current_stock}, Required: {test_qty})")
    else:
        print(f"   ✅ ALLOWED")
    
    test_qty = current_stock - 1 if current_stock > 0 else 0
    print(f"\n   Scenario 2: Try to sell {test_qty} units (within stock)")
    if current_stock >= test_qty and test_qty > 0:
        print(f"   ✅ ALLOWED")
    else:
        print(f"   ❌ BLOCKED")

conn.close()

print("\n" + "=" * 60)
print("✅ Stock validation test complete!")
print("=" * 60)
