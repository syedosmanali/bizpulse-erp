#!/usr/bin/env python3
"""
Setup Super Admin User for Client Management
Creates a super admin user that can access the client management module
"""

from modules.shared.database import get_db_connection, generate_id, hash_password
from datetime import datetime

def setup_super_admin():
    """Create or update super admin user"""
    
    print("🔧 Setting up Super Admin for Client Management...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Super admin details
    admin_email = "admin@bizpulse.com"
    admin_password = "admin123"
    
    try:
        # Check if admin user already exists
        cursor.execute("SELECT id, is_admin FROM users WHERE email = ?", (admin_email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Update existing user to be admin
            cursor.execute("""
                UPDATE users 
                SET is_admin = 1, password_hash = ?
                WHERE email = ?
            """, (hash_password(admin_password), admin_email))
            
            print(f"✅ Updated existing user {admin_email} to super admin")
        else:
            # Create new super admin user
            user_id = generate_id()
            cursor.execute("""
                INSERT INTO users (
                    id, email, password_hash, business_name, business_type,
                    first_name, last_name, is_admin, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                admin_email,
                hash_password(admin_password),
                "BizPulse ERP",
                "software",
                "Super",
                "Admin",
                1,  # is_admin = True
                1,  # is_active = True
                datetime.now().isoformat()
            ))
            
            print(f"✅ Created new super admin user: {admin_email}")
        
        # Create some sample clients for testing
        sample_clients = [
            {
                "company_name": "ABC Electronics",
                "contact_email": "contact@abcelectronics.com",
                "contact_name": "John Smith",
                "username": "abc_electronics",
                "business_type": "retail",
                "phone_number": "+91 9876543210"
            },
            {
                "company_name": "XYZ Wholesale",
                "contact_email": "info@xyzwholesale.com",
                "contact_name": "Jane Doe",
                "username": "xyz_wholesale",
                "business_type": "wholesale",
                "phone_number": "+91 9876543211"
            },
            {
                "company_name": "Tech Services Ltd",
                "contact_email": "admin@techservices.com",
                "contact_name": "Mike Johnson",
                "username": "tech_services",
                "business_type": "service",
                "phone_number": "+91 9876543212"
            }
        ]
        
        for client_data in sample_clients:
            # Check if client already exists
            cursor.execute("SELECT id FROM clients WHERE username = ?", (client_data["username"],))
            if not cursor.fetchone():
                client_id = generate_id()
                cursor.execute("""
                    INSERT INTO clients (
                        id, company_name, contact_email, contact_name, phone_number,
                        username, password_hash, business_type, is_active, 
                        city, state, country, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    client_id,
                    client_data["company_name"],
                    client_data["contact_email"],
                    client_data["contact_name"],
                    client_data["phone_number"],
                    client_data["username"],
                    hash_password("admin123"),  # Default password
                    client_data["business_type"],
                    1,  # is_active
                    "Mumbai",  # city
                    "Maharashtra",  # state
                    "India",  # country
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                print(f"✅ Created sample client: {client_data['company_name']}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Super Admin Setup Complete!")
        print("=" * 50)
        print("Super Admin Credentials:")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("\nAccess Client Management:")
        print("1. Start your app: python app.py")
        print("2. Login with super admin credentials")
        print("3. Go to: http://localhost:5000/admin/clients")
        print("\nSample Clients Created:")
        for client in sample_clients:
            print(f"- {client['company_name']} (@{client['username']}) - Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up super admin: {e}")
        conn.rollback()
        conn.close()
        return False

def test_super_admin_access():
    """Test super admin authentication"""
    
    print("\n🧪 Testing Super Admin Access...")
    
    from modules.auth.service import AuthService
    
    auth_service = AuthService()
    
    # Test authentication
    result = auth_service.authenticate_user("admin@bizpulse.com", "admin123")
    
    if result['success']:
        user = result['user']
        print("✅ Super Admin Authentication Test PASSED")
        print(f"   User: {user['name']} ({user['email']})")
        print(f"   Type: {user['type']}")
        print(f"   Is Super Admin: {user['is_super_admin']}")
        
        if user['is_super_admin']:
            print("✅ Super Admin flag is correctly set")
            return True
        else:
            print("❌ Super Admin flag is NOT set")
            return False
    else:
        print(f"❌ Super Admin Authentication Test FAILED: {result['message']}")
        return False

def main():
    """Main setup function"""
    print("🏪 BizPulse ERP - Super Admin Setup for Client Management")
    print("=" * 60)
    
    # Setup super admin
    if setup_super_admin():
        # Test authentication
        if test_super_admin_access():
            print("\n🎯 Next Steps:")
            print("1. Start your application: python app.py")
            print("2. Login with: admin@bizpulse.com / admin123")
            print("3. Access client management: http://localhost:5000/admin/clients")
            print("4. Test client impersonation and management features")
            print("\n✨ Client Management Features Available:")
            print("- View all clients with statistics")
            print("- Add new clients")
            print("- Login as any client (impersonation)")
            print("- Reset client passwords")
            print("- Bulk operations (activate/deactivate)")
            print("- Client analytics and reports")
        else:
            print("\n⚠️  Authentication test failed. Please check the setup.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()