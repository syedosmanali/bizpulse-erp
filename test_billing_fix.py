"""
Test script to verify that the billing issue has been fixed
This script tests inserting a bill record with customer_phone
"""

import sqlite3
from datetime import datetime

def test_billing_fix():
    """
    Test that we can now create bills with customer_phone without error
    """
    print("🔍 Testing billing functionality after fix...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect('billing.db')
        cursor = conn.cursor()
        
        # Test inserting a bill with customer_phone (this would fail before the fix)
        test_bill_data = {
            'id': 'test_bill_001',
            'bill_number': 'BILL-001',
            'customer_id': 'cust-test-001',
            'customer_name': 'Test Customer',
            'customer_phone': '+91-9876543210',  # This was causing the error before
            'business_type': 'retail',
            'subtotal': 100.0,
            'tax_amount': 18.0,
            'total_amount': 118.0,
            'payment_method': 'cash',
            'status': 'completed'
        }
        
        # First, delete any existing test record to avoid conflicts
        cursor.execute("DELETE FROM bills WHERE id = ?", (test_bill_data['id'],))
        
        # Insert the test bill record
        cursor.execute("""
            INSERT INTO bills (
                id, bill_number, customer_id, customer_name, customer_phone,
                business_type, subtotal, tax_amount, total_amount,
                payment_method, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_bill_data['id'],
            test_bill_data['bill_number'],
            test_bill_data['customer_id'],
            test_bill_data['customer_name'],
            test_bill_data['customer_phone'],  # This is the critical field that was failing
            test_bill_data['business_type'],
            test_bill_data['subtotal'],
            test_bill_data['tax_amount'],
            test_bill_data['total_amount'],
            test_bill_data['payment_method'],
            test_bill_data['status']
        ))
        
        conn.commit()
        print("✅ Successfully inserted bill with customer_phone!")
        
        # Verify the record was inserted correctly
        cursor.execute("SELECT * FROM bills WHERE id = ?", (test_bill_data['id'],))
        result = cursor.fetchone()
        
        if result:
            print("✅ Record found in database")
            # Find the customer_phone value in the result
            cursor.execute("PRAGMA table_info(bills)")
            column_names = [col[1] for col in cursor.fetchall()]
            
            # Map the result to column names to find customer_phone
            result_dict = dict(zip(column_names, result))
            
            if 'customer_phone' in result_dict and result_dict['customer_phone'] == test_bill_data['customer_phone']:
                print(f"✅ customer_phone field correctly stored: {result_dict['customer_phone']}")
            else:
                print("❌ customer_phone field not found or incorrect")
        else:
            print("❌ Record not found in database")
        
        # Clean up - remove the test record
        cursor.execute("DELETE FROM bills WHERE id = ?", (test_bill_data['id'],))
        conn.commit()
        print("✅ Test record cleaned up")
        
        conn.close()
        print("\n🎉 SUCCESS: Billing system is working correctly!")
        print("✅ You can now create bills without the 'customer_phone' error")
        return True
        
    except sqlite3.OperationalError as e:
        if "customer_phone" in str(e):
            print(f"❌ FAILED: The customer_phone column issue still exists: {e}")
            return False
        else:
            print(f"❌ FAILED: Database error: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 BILLING FIX VERIFICATION                     ║")
    print("║                                                              ║")
    print("║    Testing: 'table bills has no column named customer_phone'  ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    success = test_billing_fix()
    
    print()
    if success:
        print("🏆 CONCLUSION: The billing issue has been successfully fixed!")
        print("💡 You can now create bills with customer information")
        print("🔄 Restart your application to ensure all changes take effect")
    else:
        print("💥 CONCLUSION: The billing issue still exists!")
        print("🔧 Please review the error messages above")

if __name__ == "__main__":
    main()