#!/usr/bin/env python3
"""
Test WhatsApp endpoints without starting full Flask app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_whatsapp_functions():
    """Test WhatsApp functions directly"""
    print("🧪 Testing WhatsApp Functions Directly")
    print("=" * 50)
    
    try:
        # Import WhatsApp service
        from services.whatsapp_service import WhatsAppService
        
        # Initialize service
        whatsapp_service = WhatsAppService()
        print("✅ WhatsApp service initialized")
        
        # Test validation
        validation = whatsapp_service.validate_configuration()
        print(f"📊 Service Valid: {'✅ Yes' if validation['valid'] else '❌ No'}")
        
        if validation['valid']:
            print(f"   Service: {validation.get('service')}")
            print(f"   Method: {validation.get('method')}")
            print(f"   Status: {validation.get('status')}")
        
        # Test welcome message creation
        print(f"\n🎉 Testing Welcome Message Creation")
        
        test_client_data = {
            'id': 'test_123',
            'company_name': 'Test Company Ltd',
            'contact_name': 'John Doe',
            'contact_email': 'john@testcompany.com',
            'phone_number': '9876543210',
            'username': 'testuser',
            'password': 'TestPass123'
        }
        
        # Create welcome message manually (like the function does)
        phone_number = test_client_data.get('phone_number') or test_client_data.get('whatsapp_number')
        
        if phone_number and not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')
        
        welcome_message = f"""🎉 *Welcome to BizPulse ERP!*

Dear {test_client_data.get('contact_name', 'Valued Client')},

Welcome to our comprehensive business management system! Your account has been successfully set up.

🔐 *Your Login Credentials:*
• Website: http://localhost:5000
• Username: {test_client_data['username']}
• Password: {test_client_data['password']}

🚀 *Get Started:*
1. Visit our website
2. Login with your credentials
3. Explore all the powerful features

📱 *Mobile Access:*
• Use the same login on mobile
• Access from anywhere, anytime

If you need any assistance, our support team is here to help.

🔗 *BizPulse ERP System*
📞 Support: +91 7093635305
📧 Email: bizpulse.erp@gmail.com

Thank you for choosing BizPulse ERP! 🎉"""
        
        print(f"📱 Target Phone: {phone_number}")
        print(f"📝 Message Length: {len(welcome_message)} characters")
        
        # Test developer number method
        result = whatsapp_service.send_from_developer_number(phone_number, welcome_message)
        
        if result['success']:
            print("✅ Welcome message generation successful!")
            print(f"   Message ID: {result['message_id']}")
            print(f"   To Number: {result['to_number']}")
            print(f"   From Number: {result['from_number']}")
            print(f"   Method: {result['response']['method']}")
            
            if result.get('whatsapp_link'):
                print(f"\n📱 WhatsApp Link (First 100 chars):")
                print(f"   {result['whatsapp_link'][:100]}...")
            
            if result.get('developer_link'):
                print(f"\n👨‍💻 Developer Link (First 100 chars):")
                print(f"   {result['developer_link'][:100]}...")
        else:
            print(f"❌ Welcome message failed: {result.get('error')}")
        
        # Test custom notification
        print(f"\n📢 Testing Custom Notification")
        
        custom_message = """📢 *Important System Update*

Dear Test Company Ltd,

We've just released exciting new features and improvements to BizPulse ERP:

✨ Enhanced user interface
📊 Advanced reporting capabilities  
🔒 Improved security features
📱 Better mobile experience

Please log in to explore these new features!

Best regards,
BizPulse Team"""
        
        custom_result = whatsapp_service.send_from_developer_number(phone_number, custom_message)
        
        if custom_result['success']:
            print("✅ Custom notification generation successful!")
            print(f"   Message ID: {custom_result['message_id']}")
            
            if custom_result.get('whatsapp_link'):
                print(f"   WhatsApp Link Available: Yes")
        else:
            print(f"❌ Custom notification failed: {custom_result.get('error')}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 WHATSAPP INTEGRATION TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Service Initialized: Yes")
        print(f"📱 Developer Number: {whatsapp_service.default_phone}")
        print(f"🔧 Service Valid: {'Yes' if validation['valid'] else 'No'}")
        print(f"🎉 Welcome Messages: {'Working' if result['success'] else 'Failed'}")
        print(f"📢 Custom Messages: {'Working' if custom_result['success'] else 'Failed'}")
        
        print(f"\n🎯 Integration Status: {'READY FOR PRODUCTION' if result['success'] and custom_result['success'] else 'NEEDS ATTENTION'}")
        
        if result['success'] and custom_result['success']:
            print(f"\n📋 Next Steps:")
            print(f"1. Start Flask app: python app.py")
            print(f"2. Go to: http://localhost:5000/whatsapp-sender")
            print(f"3. Test with real client data")
            print(f"4. Click WhatsApp links to send from developer number (7093635305)")
        
    except Exception as e:
        print(f"❌ Error testing WhatsApp functions: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_whatsapp_functions()