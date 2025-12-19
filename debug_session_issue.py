#!/usr/bin/env python3
"""
Debug session handling for employee login
"""
import sqlite3

def debug_session_issue():
    print("🔍 Debugging Session Issue for Employee Login...")
    
    try:
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        # Check Ajay's current data
        ajay = conn.execute('''
            SELECT cu.id, cu.full_name, cu.email, cu.username, cu.client_id, cu.role,
                   c.id as client_owner_id, c.company_name, c.contact_email
            FROM client_users cu
            JOIN clients c ON cu.client_id = c.id
            WHERE cu.full_name = 'ajay'
        ''').fetchone()
        
        if ajay:
            print(f"✅ Ajay's Data:")
            print(f"   Employee ID: {ajay['id']}")
            print(f"   Name: {ajay['full_name']}")
            print(f"   Email: {ajay['email']}")
            print(f"   Username: {ajay['username']}")
            print(f"   Role: {ajay['role']}")
            print(f"   Client ID: {ajay['client_id']}")
            print(f"   Business Owner ID: {ajay['client_owner_id']}")
            print(f"   Company: {ajay['company_name']}")
            print(f"   Owner Email: {ajay['contact_email']}")
            
            print(f"\n🔍 Session Analysis:")
            print(f"   When Ajay logs in, session should be:")
            print(f"   - user_id: {ajay['id']} (Employee's ID)")
            print(f"   - user_type: 'employee'")
            print(f"   - user_name: '{ajay['full_name']}'")
            print(f"   - client_id: {ajay['client_id']} (Business Owner's ID)")
            
            print(f"\n⚠️  POTENTIAL ISSUE:")
            print(f"   If session gets confused, it might use:")
            print(f"   - user_id: {ajay['client_id']} (Business Owner's ID) ❌")
            print(f"   - user_type: 'client' ❌")
            
            print(f"\n✅ CORRECT BEHAVIOR:")
            print(f"   Employee should stay logged in as employee")
            print(f"   Should NOT redirect to business owner's account")
            print(f"   Should see only permitted modules based on permissions")
            
        else:
            print("❌ Ajay not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_session_issue()