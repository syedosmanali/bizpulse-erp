#!/usr/bin/env python3
"""
Fix RBAC email checks to use is_super_admin flag instead of specific email
"""

def fix_rbac_routes():
    """Fix the RBAC routes file"""
    
    file_path = 'modules/rbac/routes.py'
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the specific email check with is_super_admin flag
        old_pattern = "session.get('email') == 'bizpulse.erp@gmail.com'"
        new_pattern = "session.get('is_super_admin', False)"
        
        # Count occurrences
        count = content.count(old_pattern)
        print(f"Found {count} occurrences of email check")
        
        # Replace all occurrences
        new_content = content.replace(old_pattern, new_pattern)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Successfully updated {count} email checks in {file_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_rbac_routes()