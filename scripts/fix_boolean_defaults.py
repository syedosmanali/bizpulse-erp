"""
Quick script to fix all BOOLEAN DEFAULT 1/0 to use get_boolean_default()
"""
import re

file_path = 'modules/shared/database.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace BOOLEAN DEFAULT 1 with {get_boolean_default(True)}
content = re.sub(
    r'is_active BOOLEAN DEFAULT 1',
    r'is_active BOOLEAN DEFAULT {get_boolean_default(True)}',
    content
)

# Replace BOOLEAN DEFAULT 0 with {get_boolean_default(False)}
content = re.sub(
    r'is_popular BOOLEAN DEFAULT 0',
    r'is_popular BOOLEAN DEFAULT {get_boolean_default(False)}',
    content
)

content = re.sub(
    r'send_daily_report BOOLEAN DEFAULT 1',
    r'send_daily_report BOOLEAN DEFAULT {get_boolean_default(True)}',
    content
)

# Also need to convert non-f-strings to f-strings for these tables
# Find all cursor.execute(''' that contain BOOLEAN DEFAULT {
lines = content.split('\n')
in_execute = False
execute_start = -1
needs_fstring = False

for i, line in enumerate(lines):
    if "cursor.execute('''" in line and 'cursor.execute(f' not in line:
        in_execute = True
        execute_start = i
        needs_fstring = False
    elif in_execute and '{get_boolean_default' in line:
        needs_fstring = True
    elif in_execute and "''')" in line:
        if needs_fstring:
            # Convert to f-string
            lines[execute_start] = lines[execute_start].replace("cursor.execute('''", "cursor.execute(f'''")
        in_execute = False
        execute_start = -1
        needs_fstring = False

content = '\n'.join(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all BOOLEAN DEFAULT values!")
print("   - Replaced BOOLEAN DEFAULT 1 with {get_boolean_default(True)}")
print("   - Replaced BOOLEAN DEFAULT 0 with {get_boolean_default(False)}")
print("   - Converted cursor.execute to f-strings where needed")
