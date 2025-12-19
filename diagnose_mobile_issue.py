#!/usr/bin/env python3
"""
Real-time mobile connection diagnostics
"""

import socket
import time
import threading
import subprocess
import sys

def monitor_connections():
    """Monitor incoming connections in real-time"""
    print("🔍 Monitoring Mobile Connections...")
    print("=" * 50)
    
    while True:
        try:
            # Check for connections to port 5000
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            connections = []
            for line in lines:
                if ':5000' in line and 'ESTABLISHED' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local = parts[1]
                        remote = parts[2]
                        connections.append(f"   📱 {remote} → {local}")
            
            if connections:
                print(f"\n⏰ {time.strftime('%H:%M:%S')} - Active Connections:")
                for conn in connections:
                    print(conn)
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

def test_mobile_urls():
    """Test all mobile URLs"""
    print("\n🧪 Testing All Mobile URLs")
    print("=" * 30)
    
    urls = [
        '/mobile-ultra-test',
        '/mobile-simple', 
        '/mobile-working',
        '/mobile-direct',
        '/mobile-test-connection'
    ]
    
    for url in urls:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('192.168.0.3', 5000))
            
            request = f"GET {url} HTTP/1.1\r\nHost: 192.168.0.3:5000\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            if '200 OK' in response:
                print(f"   ✅ {url} - Working")
            elif '404' in response:
                print(f"   ❌ {url} - Not Found")
            else:
                print(f"   ⚠️ {url} - Unknown Response")
                
        except Exception as e:
            print(f"   ❌ {url} - Error: {e}")

def check_firewall_rules():
    """Check if firewall rules are properly set"""
    print("\n🛡️ Checking Firewall Rules")
    print("=" * 25)
    
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                              capture_output=True, text=True, timeout=10)
        
        rules_found = []
        if 'BizPulse' in result.stdout:
            rules_found.append("✅ BizPulse rules found")
        if 'Python' in result.stdout:
            rules_found.append("✅ Python rules found")
        if '5000' in result.stdout:
            rules_found.append("✅ Port 5000 rules found")
            
        if rules_found:
            for rule in rules_found:
                print(f"   {rule}")
        else:
            print("   ❌ No BizPulse firewall rules found")
            print("   💡 Run COMPLETE_MOBILE_FIX.bat as Administrator")
            
    except Exception as e:
        print(f"   ❌ Could not check firewall: {e}")

def main():
    print("🔍 BizPulse Mobile Issue Diagnostics")
    print("=" * 40)
    
    # Test URLs first
    test_mobile_urls()
    
    # Check firewall
    check_firewall_rules()
    
    print(f"\n📱 Mobile URLs to Test:")
    print(f"   🧪 ULTRA SIMPLE: http://192.168.0.3:5000/mobile-ultra-test")
    print(f"   📱 MOBILE ERP:   http://192.168.0.3:5000/mobile-simple")
    print(f"   🔧 DIRECT:       http://192.168.0.3:5000/mobile-direct")
    
    print(f"\n🎯 Start with the ULTRA SIMPLE test first!")
    print(f"   If that works, the connection is fine.")
    print(f"   If not, it's a network/firewall issue.")
    
    # Ask if user wants to monitor connections
    try:
        choice = input("\n📊 Monitor connections in real-time? (y/n): ").lower()
        if choice == 'y':
            monitor_connections()
    except KeyboardInterrupt:
        print("\n👋 Diagnostics complete")

if __name__ == "__main__":
    main()