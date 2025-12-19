#!/usr/bin/env python3
"""
Comprehensive Network Diagnostic for Mobile Access
"""
import socket
import subprocess
import sys
import requests
import time

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_port_listening(port):
    """Check if port is listening"""
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        return f":{port}" in result.stdout
    except:
        return False

def check_firewall_rules():
    """Check Windows Firewall rules"""
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                              capture_output=True, text=True, shell=True)
        return "Python" in result.stdout or "BizPulse" in result.stdout
    except:
        return False

def test_local_access(ip, port):
    """Test local access to server"""
    try:
        response = requests.get(f"http://{ip}:{port}/mobile-simple", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_network_interfaces():
    """Check all network interfaces"""
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        return result.stdout
    except:
        return "Unable to get network info"

def main():
    print("🔍 BizPulse Mobile Network Diagnostic")
    print("=" * 50)
    
    # Get IP addresses
    local_ip = get_local_ip()
    print(f"📡 Local IP: {local_ip}")
    
    # Check ports
    ports_to_check = [5000, 8080, 3000, 8000]
    print("\n🔌 Port Status:")
    for port in ports_to_check:
        listening = check_port_listening(port)
        status = "✅ LISTENING" if listening else "❌ NOT LISTENING"
        print(f"   Port {port}: {status}")
    
    # Check firewall
    print(f"\n🔥 Firewall Rules: {'✅ FOUND' if check_firewall_rules() else '❌ NOT FOUND'}")
    
    # Test local access
    print("\n🌐 Local Access Test:")
    for port in [5000, 8080]:
        if check_port_listening(port):
            accessible = test_local_access(local_ip, port)
            status = "✅ ACCESSIBLE" if accessible else "❌ NOT ACCESSIBLE"
            print(f"   http://{local_ip}:{port}: {status}")
    
    # Network interfaces
    print("\n📶 Network Interfaces:")
    interfaces = check_network_interfaces()
    for line in interfaces.split('\n'):
        if 'IPv4 Address' in line or 'Wi-Fi' in line or 'Ethernet' in line:
            print(f"   {line.strip()}")
    
    # Mobile URLs
    print(f"\n📱 Mobile URLs to try:")
    print(f"   http://{local_ip}:8080/mobile-simple")
    print(f"   http://{local_ip}:5000/mobile-simple")
    print(f"   http://192.168.1.{local_ip.split('.')[-1]}:8080/mobile-simple")
    print(f"   http://10.0.0.{local_ip.split('.')[-1]}:8080/mobile-simple")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not check_port_listening(8080):
        print("   ❗ Start server: python mobile_server.py")
    if not check_firewall_rules():
        print("   ❗ Add firewall rule (as admin):")
        print("     netsh advfirewall firewall add rule name=\"BizPulse\" dir=in action=allow protocol=TCP localport=8080")
    
    print("   📱 Mobile troubleshooting:")
    print("     1. Ensure same WiFi network")
    print("     2. Clear mobile browser cache")
    print("     3. Try different mobile browser")
    print("     4. Restart WiFi on mobile")
    print("     5. Try mobile hotspot temporarily")

if __name__ == "__main__":
    main()