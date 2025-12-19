#!/usr/bin/env python3
"""
Fix indentation issues in app.py
"""

def fix_indentation():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_get_reports_overview = False
    function_indent_level = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Detect start of get_reports_overview function
        if 'def get_reports_overview():' in line:
            in_get_reports_overview = True
            function_indent_level = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Detect end of get_reports_overview function
        if in_get_reports_overview and line.strip() and not line.startswith(' '):
            if line.startswith('def ') or line.startswith('@app.route') or line.startswith('#'):
                in_get_reports_overview = False
        
        # Fix indentation within get_reports_overview function
        if in_get_reports_overview:
            if line.strip():  # Non-empty line
                # Calculate current indentation
                current_indent = len(line) - len(line.lstrip())
                
                # If line is over-indented (more than 12 spaces), fix it
                if current_indent > 12:
                    # Reduce indentation to reasonable level
                    content = line.lstrip()
                    if content.startswith('try:') or content.startswith('except'):
                        new_line = '    ' + content  # 4 spaces for try/except
                    elif content.startswith('#') or content.startswith('"""'):
                        new_line = '        ' + content  # 8 spaces for comments/docstrings
                    else:
                        new_line = '        ' + content  # 8 spaces for regular code
                    fixed_lines.append(new_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write fixed content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Indentation fixed!")

if __name__ == '__main__':
    fix_indentation()