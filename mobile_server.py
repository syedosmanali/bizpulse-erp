#!/usr/bin/env python3
"""
BizPulse Mobile Server - Port 8080 for better mobile access
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main app
from app import app, init_db

def print_mobile_info():
    """Print mobile access information"""
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 70)
    print("🚀 BizPulse Mobile Server Starting...")
    print("=" * 70)
    print("📱 [MOBILE ACCESS - PORT 8080]:")
    print(f"   Mobile App: http://{local_ip}:8080/mobile-simple")
    print(f"   Dashboard: http://{local_ip}:8080/mobile-dashboard")
    print(f"   Login: bizpulse.erp@gmail.com / demo123")
    print()
    print("🖥️  [DESKTOP ACCESS]:")
    print(f"   Main Site: http://localhost:8080")
    print(f"   Network: http://{local_ip}:8080")
    print()
    print("⚠️  MOBILE TROUBLESHOOTING:")
    print("   1. Ensure mobile and laptop are on SAME WiFi")
    print("   2. Try different mobile browser")
    print("   3. Clear mobile browser cache")
    print("   4. Restart WiFi on mobile device")
    print("=" * 70)
    print()

if __name__ == '__main__':
    init_db()
    print_mobile_info()
    
    # Run on port 8080 for better mobile compatibility
    app.run(host='0.0.0.0', port=8080, debug=True)