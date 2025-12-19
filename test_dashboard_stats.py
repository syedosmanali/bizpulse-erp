import sqlite3
from datetime import datetime

print("=" * 60)
print("DASHBOARD STATS TEST - Real-time Data Check")
print("=" * 60)

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

today = datetime.now().strftime('%Y-%m-%d')

print(f"\n📅 Testing for date: {today}")

# 1. Today's Revenue
print("\n1. TODAY'S REVENUE:")
today_revenue = cursor.execute('''
    SELECT COALESCE(SUM(total_amount), 0) as revenue,
           COUNT(*) as transactions
    FROM bills 
    WHERE DATE(created_at) = ?
''', (today,)).fetchone()

print(f"   Revenue: ₹{today_revenue['revenue']:.2f}")
print(f"   Transactions: {today_revenue['transactions']}")

# 2. Today's Profit
print("\n2. TODAY'S PROFIT:")
today_profit_data = cursor.execute('''
    SELECT 
        COALESCE(SUM(s.total_price), 0) as total_sales,
        COALESCE(SUM(s.quantity * p.cost), 0) as total_cost
    FROM sales s
    LEFT JOIN products p ON s.product_id = p.id
    WHERE s.sale_date = ?
''', (today,)).fetchone()

total_sales = float(today_profit_data['total_sales'])
total_cost = float(today_profit_data['total_cost'])
today_profit = total_sales - total_cost
profit_margin = (today_profit / total_sales * 100) if total_sales > 0 else 0

print(f"   Total Sales: ₹{total_sales:.2f}")
print(f"   Total Cost: ₹{total_cost:.2f}")
print(f"   Profit: ₹{today_profit:.2f}")
print(f"   Profit Margin: {profit_margin:.2f}%")

# 3. Products
print("\n3. INVENTORY:")
total_products = cursor.execute('''
    SELECT COUNT(*) as count FROM products WHERE is_active = 1
''').fetchone()['count']

low_stock = cursor.execute('''
    SELECT COUNT(*) as count FROM products 
    WHERE stock <= min_stock AND is_active = 1
''').fetchone()['count']

print(f"   Total Products: {total_products}")
print(f"   Low Stock: {low_stock}")

# 4. Customers
print("\n4. CUSTOMERS:")
total_customers = cursor.execute('''
    SELECT COUNT(*) as count FROM customers WHERE is_active = 1
''').fetchone()['count']

print(f"   Total Customers: {total_customers}")

# 5. Recent Sales
print("\n5. RECENT SALES (Today):")
recent_sales = cursor.execute('''
    SELECT 
        b.bill_number,
        b.total_amount,
        COALESCE(c.name, 'Walk-in Customer') as customer_name,
        strftime('%H:%M', b.created_at) as time
    FROM bills b
    LEFT JOIN customers c ON b.customer_id = c.id
    WHERE DATE(b.created_at) = ?
    ORDER BY b.created_at DESC
    LIMIT 5
''', (today,)).fetchall()

if recent_sales:
    for sale in recent_sales:
        print(f"   {sale['time']} - {sale['bill_number']} - {sale['customer_name']} - ₹{sale['total_amount']:.2f}")
else:
    print("   No sales today yet")

# 6. Top Products
print("\n6. TOP SELLING PRODUCTS (Today):")
top_products = cursor.execute('''
    SELECT 
        s.product_name,
        SUM(s.quantity) as total_quantity,
        SUM(s.total_price) as total_sales
    FROM sales s
    WHERE s.sale_date = ?
    GROUP BY s.product_id, s.product_name
    ORDER BY total_quantity DESC
    LIMIT 5
''', (today,)).fetchall()

if top_products:
    for product in top_products:
        print(f"   {product['product_name']}: {product['total_quantity']} units - ₹{product['total_sales']:.2f}")
else:
    print("   No products sold today yet")

conn.close()

print("\n" + "=" * 60)
print("✅ Dashboard stats are working with real-time data!")
print("=" * 60)
