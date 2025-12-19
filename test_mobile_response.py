#!/usr/bin/env python3
"""
Test what the mobile ERP route is actually returning
"""

import socket
import sys

def test_mobile_route():
    print("🔍 Testing Mobile ERP Route Response")
    print("=" * 50)
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.0.3', 5000))
        
        # Send HTTP request
        request = "GET /mobile-simple HTTP/1.1\r\nHost: 192.168.0.3:5000\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        
        # Receive response
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
        
        sock.close()
        
        # Parse response
        response_str = response.decode('utf-8', errors='ignore')
        
        print("📡 HTTP Response Status:")
        status_line = response_str.split('\n')[0]
        print(f"   {status_line}")
        
        print("\n📄 Content Analysis:")
        if 'mobile_simple_working.html' in response_str:
            print("   ✅ Correct template being served")
        else:
            print("   ❌ Wrong template or error")
            
        if 'BizPulse' in response_str:
            print("   ✅ BizPulse content found")
        else:
            print("   ❌ BizPulse content missing")
            
        if 'Mobile ERP' in response_str:
            print("   ✅ Mobile ERP content found")
        else:
            print("   ❌ Mobile ERP content missing")
            
        if '<script>' in response_str:
            print("   ✅ JavaScript found")
        else:
            print("   ❌ JavaScript missing")
            
        # Check for errors
        if '500 Internal Server Error' in response_str:
            print("   ❌ Server Error Detected!")
        elif '404 Not Found' in response_str:
            print("   ❌ Route Not Found!")
        elif '200 OK' in response_str:
            print("   ✅ HTTP 200 OK - Route working")
            
        # Show first few lines of HTML
        print("\n📝 HTML Content Preview:")
        html_start = response_str.find('<!DOCTYPE')
        if html_start != -1:
            html_preview = response_str[html_start:html_start+500]
            print("   " + html_preview[:200] + "...")
        else:
            print("   ❌ No HTML content found")
            
        # Check content length
        content_length = len(response_str)
        print(f"\n📏 Content Length: {content_length} bytes")
        
        if content_length < 1000:
            print("   ⚠️ Content seems too short - possible error")
        elif content_length > 10000:
            print("   ✅ Content length looks good")
        else:
            print("   ⚠️ Content length seems small")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\n🔧 Possible Issues:")
        print("   - Server not running")
        print("   - Firewall blocking connection")
        print("   - Wrong IP address")
        
if __name__ == "__main__":
    test_mobile_route()