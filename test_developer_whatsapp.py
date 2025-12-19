#!/usr/bin/env python3
"""
Test script for Developer WhatsApp Integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_developer_whatsapp():
    """Test WhatsApp integration with developer number"""
    print("🧪 Testing Developer WhatsApp Integration")
    print("=" * 50)
    
    try:
        from services.whatsapp_service import WhatsAppService
        
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppService()
        print("✅ WhatsApp service initialized")
        
        # Test configuration
        validation = whatsapp_service.validate_configuration()
        print(f"📊 Service Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        
        if validation['valid']:
            print(f"   Service: {validation.get('service', 'N/A')}")
            print(f"   Method: {validation.get('method', 'N/A')}")
            print(f"   Status: {validation.get('status', 'N/A')}")
        
        # Test developer number integration
        print(f"\n📱 Developer Number: {whatsapp_service.default_phone}")
        
        # Test message creation
        test_client_number = "9876543210"  # Test number
        test_message = """🎉 Welcome to BizPulse ERP!

This is a test message from the developer dashboard.

Your login credentials:
• Username: test_user
• Password: test_pass

Thank you for choosing BizPulse ERP!"""
        
        print(f"\n🧪 Testing message creation for client: {test_client_number}")
        
        # Test developer number method
        result = whatsapp_service.send_from_developer_number(test_client_number, test_message)
        
        if result['success']:
            print("✅ Developer WhatsApp integration working!")
            print(f"   Message ID: {result['message_id']}")
            print(f"   To Number: {result['to_number']}")
            print(f"   From Number: {result['from_number']}")
            print(f"   Method: {result['response']['method']}")
            
            if result.get('whatsapp_link'):
                print(f"\n📱 WhatsApp Link Generated:")
                print(f"   {result['whatsapp_link'][:100]}...")
            
            if result.get('developer_link'):
                print(f"\n👨‍💻 Developer Link Generated:")
                print(f"   {result['developer_link'][:100]}...")
                
        else:
            print(f"❌ Developer WhatsApp integration failed: {result.get('error')}")
        
        # Test regular text message as fallback
        print(f"\n🧪 Testing fallback text message...")
        fallback_result = whatsapp_service.send_text_message(test_client_number, "Test fallback message")
        
        if fallback_result['success']:
            print("✅ Fallback text message working!")
            print(f"   Method: {fallback_result['response']['method']}")
        else:
            print(f"❌ Fallback failed: {fallback_result.get('error')}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 DEVELOPER WHATSAPP INTEGRATION SUMMARY")
        print("=" * 50)
        print(f"✅ Service Initialized: Yes")
        print(f"📱 Developer Number: {whatsapp_service.default_phone}")
        print(f"🔧 Service Valid: {'Yes' if validation['valid'] else 'No'}")
        print(f"📤 Developer Method: {'Working' if result['success'] else 'Failed'}")
        print(f"🔄 Fallback Method: {'Working' if fallback_result['success'] else 'Failed'}")
        
        print(f"\n🎉 WhatsApp Integration Status: {'READY' if result['success'] or fallback_result['success'] else 'NEEDS ATTENTION'}")
        
        if result['success']:
            print(f"\n📋 How to Use:")
            print(f"1. Go to /whatsapp-sender in developer dashboard")
            print(f"2. Select a client and click 'Welcome' button")
            print(f"3. Click the generated WhatsApp link")
            print(f"4. Message will open in WhatsApp from your number (7093635305)")
            print(f"5. Send the message to the client")
        
    except Exception as e:
        print(f"❌ Error testing WhatsApp integration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_developer_whatsapp()