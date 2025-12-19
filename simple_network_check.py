#!/usr/bin/env python3
"""
Simple Network Check for Mobile Access
"""
import socket
import subprocess
import sys

def get_all_ips():
    """Get all possible IP addresses"""
    ips = []
    try:
        # Get hostname IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        ips.append(local_ip)
        
        # Get interface IPs
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'IPv4 Address' in line and ':' in line:
                ip = line.split(':')[1].strip()
                if ip not in ips and ip != '127.0.0.1':
                    ips.append(ip)
    except:
        ips = ['192.168.0.3']  # fallback
    
    return ips

def check_port_open(ip, port):
    """Check if port is open on IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🔍 BizPulse Mobile Network Check")
    print("=" * 40)
    
    # Get all IPs
    ips = get_all_ips()
    print(f"📡 Found IP addresses: {ips}")
    
    # Check ports on each IP
    ports = [5000, 8080]
    print(f"\n🔌 Checking ports {ports}:")
    
    working_urls = []
    for ip in ips:
        for port in ports:
            is_open = check_port_open(ip, port)
            status = "✅ OPEN" if is_open else "❌ CLOSED"
            print(f"   {ip}:{port} - {status}")
            
            if is_open:
                working_urls.append(f"http://{ip}:{port}/mobile-simple")
    
    # Show working URLs
    if working_urls:
        print(f"\n📱 Working Mobile URLs:")
        for url in working_urls:
            print(f"   {url}")
    else:
        print(f"\n❌ No working URLs found!")
        print(f"   Server might not be running or ports are blocked")
    
    # Alternative IPs to try
    print(f"\n🔄 Alternative IPs to try on mobile:")
    base_ips = ['192.168.0', '192.168.1', '10.0.0', '172.16.0']
    last_octet = ips[0].split('.')[-1] if ips else '3'
    
    for base in base_ips:
        alt_ip = f"{base}.{last_octet}"
        print(f"   http://{alt_ip}:8080/mobile-simple")
    
    print(f"\n💡 Troubleshooting Steps:")
    print(f"   1. Ensure server is running: python mobile_server.py")
    print(f"   2. Check same WiFi network on both devices")
    print(f"   3. Try different mobile browser")
    print(f"   4. Clear mobile browser cache")
    print(f"   5. Restart WiFi on mobile device")
    print(f"   6. Try mobile hotspot temporarily")

if __name__ == "__main__":
    main()