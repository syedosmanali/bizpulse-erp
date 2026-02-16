"""
Test Invoice View - Debug the invoice loading issue
"""
import os
import requests

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Test with a real bill ID from the database
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

print("🔍 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get the most recent bill
print("\n📋 Getting most recent bill...")
cursor.execute("""
    SELECT id, bill_number, customer_name, total_amount, created_at
    FROM bills
    ORDER BY created_at DESC
    LIMIT 1
""")

bill = cursor.fetchone()

if not bill:
    print("❌ No bills found in database")
    conn.close()
    exit(1)

print(f"\n✅ Found bill:")
print(f"   ID: {bill['id']}")
print(f"   Bill Number: {bill['bill_number']}")
print(f"   Customer: {bill['customer_name']}")
print(f"   Amount: ₹{bill['total_amount']}")
print(f"   Date: {bill['created_at']}")

bill_id = bill['id']

# Test the invoice API endpoint
print(f"\n🔍 Testing invoice API endpoint...")
print(f"   URL: http://localhost:5000/api/invoices/{bill_id}")

try:
    response = requests.get(f"http://localhost:5000/api/invoices/{bill_id}")
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response:")
        print(f"   Success: {data.get('success')}")
        if data.get('success'):
            invoice = data.get('invoice', {})
            print(f"   Invoice ID: {invoice.get('id')}")
            print(f"   Bill Number: {invoice.get('bill_number')}")
            print(f"   Customer: {invoice.get('customer_name')}")
            print(f"   Items: {len(data.get('items', []))}")
            print(f"   Payments: {len(data.get('payments', []))}")
        else:
            print(f"   Error: {data.get('error')}")
    else:
        print(f"❌ API Error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test the invoice view page
print(f"\n🔍 Testing invoice view page...")
print(f"   URL: http://localhost:5000/retail/invoice/{bill_id}")

try:
    response = requests.get(f"http://localhost:5000/retail/invoice/{bill_id}")
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Page loaded successfully")
        # Check if invoice_id is in the HTML
        if bill_id in response.text:
            print(f"✅ Invoice ID found in HTML")
        else:
            print(f"⚠️  Invoice ID NOT found in HTML")
    else:
        print(f"❌ Page Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

conn.close()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Test the invoice view in browser:")
print(f"http://localhost:5000/retail/invoice/{bill_id}")
print("="*60)
