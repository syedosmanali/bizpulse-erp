#!/usr/bin/env python3
"""
Comprehensive fix for all indentation and syntax issues in app.py
"""

def comprehensive_fix():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Track function nesting and fix indentation
    fixed_lines = []
    in_function = None
    function_indent = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix specific problematic functions
        if 'def retail_reports_direct():' in line:
            in_function = 'retail_reports_direct'
            function_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        if 'def get_reports_overview():' in line:
            in_function = 'get_reports_overview'
            function_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
            
        if 'def get_customers_report():' in line:
            in_function = 'get_customers_report'
            function_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Detect end of function
        if in_function and line.strip() and not line.startswith(' '):
            if line.startswith('def ') or line.startswith('@app.route') or line.startswith('#'):
                in_function = None
        
        # Fix indentation within problematic functions
        if in_function:
            if line.strip() == '':
                fixed_lines.append(line)
                continue
            
            # Calculate expected indentation
            if in_function == 'retail_reports_direct':
                if 'return """' in line:
                    fixed_lines.append('    return """')
                elif line.strip() == '"""':
                    fixed_lines.append('    """')
                elif line.startswith('            '):  # HTML content
                    # Keep HTML content with minimal indentation
                    fixed_lines.append('    ' + line[12:])
                else:
                    fixed_lines.append(line)
            
            elif in_function in ['get_reports_overview', 'get_customers_report']:
                # Fix function body indentation
                if line.startswith('            '):  # Over-indented
                    # Reduce to proper function body indentation (4 spaces)
                    fixed_lines.append('    ' + line[12:])
                elif line.startswith('        '):  # Slightly over-indented
                    # Keep as is or adjust if needed
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Comprehensive fix applied!")

if __name__ == '__main__':
    comprehensive_fix()