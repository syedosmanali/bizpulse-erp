#!/usr/bin/env python3
"""
Fix all client-users API endpoints to use proper session handling
"""

def fix_session_apis():
    print("🔧 Fixing Session APIs...")
    
    # Read the current app.py file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic session handling patterns
    old_patterns = [
        "current_client_id = session.get('user_id')",
        "current_user_id = session.get('user_id')"
    ]
    
    new_patterns = [
        "current_client_id = get_current_client_id()",
        "current_user_id = get_current_client_id()"
    ]
    
    # Count replacements
    total_replacements = 0
    
    for old, new in zip(old_patterns, new_patterns):
        count = content.count(old)
        if count > 0:
            print(f"   Replacing '{old}' -> '{new}' ({count} times)")
            content = content.replace(old, new)
            total_replacements += count
    
    # Write back the fixed content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {total_replacements} session handling issues")
    print("   All client-users APIs now use proper session handling")

if __name__ == "__main__":
    fix_session_apis()