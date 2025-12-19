#!/usr/bin/env python3
"""
Get detailed network information for mobile connection troubleshooting
"""

import socket
import subprocess
import sys

def get_all_network_info():
    print("🌐 Complete Network Information")
    print("=" * 60)
    
    # Get all IP addresses
    print("📍 All Available IP Addresses:")
    try:
        hostname = socket.gethostname()
        print(f"   Computer Name: {hostname}")
        
        # Get all IP addresses
        ip_addresses = socket.getaddrinfo(hostname, None)
        unique_ips = set()
        
        for addr_info in ip_addresses:
            ip = addr_info[4][0]
            if not ip.startswith('::') and ip != '127.0.0.1':  # Skip IPv6 and localhost
                unique_ips.add(ip)
        
        for ip in sorted(unique_ips):
            print(f"   • {ip}")
            
    except Exception as e:
        print(f"   Error getting IPs: {e}")
    
    # Get network adapter info
    print("\n🔌 Network Adapter Information:")
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        
        current_adapter = ""
        for line in lines:
            line = line.strip()
            if 'adapter' in line.lower() and ':' in line:
                current_adapter = line
                print(f"\n   {current_adapter}")
            elif 'IPv4 Address' in line and '192.168' in line:
                ip = line.split(':')[-1].strip()
                print(f"      IP: {ip}")
                
                # Test if this IP works for mobile
                if test_ip_accessibility(ip):
                    print(f"      ✅ ACCESSIBLE - Use: http://{ip}:5000/mobile-simple")
                else:
                    print(f"      ❌ NOT ACCESSIBLE")
                    
    except Exception as e:
        print(f"   Error getting adapter info: {e}")
    
    # Check Windows Firewall status
    print("\n🛡️ Windows Firewall Status:")
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                              capture_output=True, text=True, timeout=10)
        if 'ON' in result.stdout:
            print("   ⚠️ Windows Firewall is ON - may block mobile access")
            print("   💡 Solution: Run fix_mobile_firewall.bat as Administrator")
        else:
            print("   ✅ Windows Firewall appears to be OFF")
    except:
        print("   ❓ Could not check firewall status")
    
    # Check if port 5000 is accessible from outside
    print("\n🔌 Port 5000 Accessibility Test:")
    try:
        # Try to bind to all interfaces
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', 5001))  # Use different port for test
        test_socket.listen(1)
        test_socket.close()
        print("   ✅ Can bind to 0.0.0.0 - External access should work")
    except Exception as e:
        print(f"   ❌ Cannot bind to 0.0.0.0: {e}")
    
    # Provide mobile URLs
    print("\n📱 Mobile URLs to Try:")
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.getaddrinfo(hostname, None)
        unique_ips = set()
        
        for addr_info in ip_addresses:
            ip = addr_info[4][0]
            if not ip.startswith('::') and ip != '127.0.0.1' and '192.168' in ip:
                unique_ips.add(ip)
        
        for ip in sorted(unique_ips):
            print(f"   🎯 http://{ip}:5000/mobile-simple")
            print(f"   🧪 http://{ip}:5000/mobile-test-connection")
            print(f"   🔧 http://{ip}:5000/mobile-direct")
            print()
            
    except Exception as e:
        print(f"   Error generating URLs: {e}")

def test_ip_accessibility(ip):
    """Test if an IP address is accessible for mobile connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 5000))
        sock.close()
        return result == 0
    except:
        return False

if __name__ == "__main__":
    get_all_network_info()