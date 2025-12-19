#!/usr/bin/env python3
"""
Debug User Agent Detection
"""
import sys
import os
sys.path.append('BizPulse_Fresh_Deploy_20251211_015908')

from app import app

def debug_detection():
    """Debug device detection"""
    
    test_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    
    print(f"User Agent: {test_user_agent}")
    print(f"Lowercase: {test_user_agent.lower()}")
    
    user_agent_lower = test_user_agent.lower()
    
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
    tablet_keywords = ['ipad', 'tablet', 'kindle']
    
    print("\nMobile Detection:")
    for keyword in mobile_keywords:
        found = keyword in user_agent_lower
        print(f"  {keyword}: {found}")
    
    print("\nTablet Detection:")
    for keyword in tablet_keywords:
        found = keyword in user_agent_lower
        print(f"  {keyword}: {found}")
    
    is_mobile = any(device in user_agent_lower for device in mobile_keywords)
    is_tablet = any(device in user_agent_lower for device in tablet_keywords)
    
    print(f"\nResult:")
    print(f"  is_mobile: {is_mobile}")
    print(f"  is_tablet: {is_tablet}")
    print(f"  Should show mobile: {is_mobile or is_tablet}")

if __name__ == "__main__":
    debug_detection()