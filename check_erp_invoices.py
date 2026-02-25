"""
Check ERP invoices table
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

try:
    # Check if erp_invoices table exists
    cursor.execute("SELECT COUNT(*) as count FROM erp_invoices")
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    print(f"📊 Total invoices in erp_invoices table: {count}")
    
    if count > 0:
        # Show sample invoices
        cursor.execute("SELECT id, invoice_number, customer_name, total_amount, payment_status FROM erp_invoices LIMIT 5")
        invoices = cursor.fetchall()
        print("\n📋 Sample invoices:")
        for inv in invoices:
            inv_dict = dict(inv) if isinstance(inv, dict) else {
                'invoice_number': inv[1],
                'customer_name': inv[2],
                'total_amount': inv[3],
                'payment_status': inv[4]
            }
            print(f"  - {inv_dict.get('invoice_number')}: {inv_dict.get('customer_name')} - ₹{inv_dict.get('total_amount')} ({inv_dict.get('payment_status')})")
    else:
        print("\n❌ No invoices found in erp_invoices table!")
        print("   This is the NEW modern ERP invoice table.")
        print("   You need to create invoices from the ERP module, not the old billing module.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThe erp_invoices table might not exist yet.")
    print("Make sure you've initialized the ERP database tables.")

conn.close()
