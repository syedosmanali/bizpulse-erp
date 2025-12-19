#!/usr/bin/env python3
"""Fix duplicate triple quotes in app.py"""

import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix duplicate docstrings pattern: """text"""\n    """text"""
pattern = r'(    """[^"]*""")\s*\n\s*\1'
content = re.sub(pattern, r'\1', content)

# Also fix the pattern where they're on the same line
pattern2 = r'("""[^"]*""")\s*("""[^"]*""")'
content = re.sub(pattern2, r'\1', content)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed duplicate triple quotes in app.py")