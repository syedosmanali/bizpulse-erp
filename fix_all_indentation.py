#!/usr/bin/env python3
"""
Fix all indentation issues in app.py
"""

def fix_all_indentation():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Find the retail_reports_direct function and fix its indentation
    in_html_block = False
    html_start_line = -1
    
    for i, line in enumerate(lines):
        # Detect start of HTML block in retail_reports_direct
        if 'def retail_reports_direct():' in line:
            print(f"Found retail_reports_direct at line {i+1}")
        
        if 'return """' in line and not in_html_block:
            in_html_block = True
            html_start_line = i
            print(f"HTML block starts at line {i+1}")
            continue
        
        # Fix indentation inside HTML block
        if in_html_block:
            if line.strip() == '"""':
                in_html_block = False
                print(f"HTML block ends at line {i+1}")
                # Fix the closing quote indentation
                lines[i] = '    """'
                continue
            
            # Don't change empty lines
            if line.strip() == '':
                continue
                
            # Fix indentation for HTML content (should be indented with 4 spaces from function level)
            if line.startswith('            '):  # 12 spaces
                # Remove extra indentation (keep only 4 spaces for function content)
                lines[i] = '    ' + line[12:]
    
    # Write back the fixed content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Fixed retail_reports_direct indentation!")

if __name__ == '__main__':
    fix_all_indentation()