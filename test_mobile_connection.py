#!/usr/bin/env python3
"""
Mobile Connection Diagnostic Script
Tests if the mobile app is accessible and working
"""

import socket
import subprocess
import sys
import time

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_port_open(ip, port):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🔍 BizPulse Mobile Connection Diagnostic")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"📍 Local IP Address: {local_ip}")
    
    # Check if port 5000 is open
    port_open = check_port_open(local_ip, 5000)
    print(f"🔌 Port 5000 Status: {'✅ OPEN' if port_open else '❌ CLOSED'}")
    
    # Check if Flask is running
    try:
        import requests
        response = requests.get(f"http://{local_ip}:5000/mobile-simple", timeout=5)
        print(f"🌐 Mobile App Status: ✅ ACCESSIBLE (Status: {response.status_code})")
    except ImportError:
        print("📦 Requests module not available, using basic check")
        if port_open:
            print("🌐 Mobile App Status: ✅ LIKELY ACCESSIBLE")
        else:
            print("🌐 Mobile App Status: ❌ NOT ACCESSIBLE")
    except Exception as e:
        print(f"🌐 Mobile App Status: ❌ ERROR - {str(e)}")
    
    print("\n📱 Mobile Access URLs:")
    print(f"   • http://{local_ip}:5000/mobile-simple")
    print(f"   • http://localhost:5000/mobile-simple")
    print(f"   • http://127.0.0.1:5000/mobile-simple")
    
    print("\n🔧 Troubleshooting Steps:")
    print("1. Make sure your mobile and PC are on the same WiFi network")
    print("2. Check Windows Firewall settings")
    print("3. Try accessing from PC browser first")
    print("4. Restart the Flask server if needed")
    
    # Check firewall (Windows)
    print("\n🛡️ Checking Windows Firewall...")
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                              capture_output=True, text=True, timeout=10)
        if 'ON' in result.stdout:
            print("⚠️  Windows Firewall is ON - may block mobile access")
            print("   Consider temporarily disabling or adding Python.exe exception")
        else:
            print("✅ Windows Firewall appears to be OFF")
    except:
        print("❓ Could not check Windows Firewall status")
    
    print(f"\n🎯 Try this URL on your mobile: http://{local_ip}:5000/mobile-simple")

if __name__ == "__main__":
    main()