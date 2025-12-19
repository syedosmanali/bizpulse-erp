#!/usr/bin/env python3
"""Count triple quotes to find imbalance"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count triple double quotes
triple_double = content.count('"""')
print(f"Triple double quotes: {triple_double}")

# Count triple single quotes  
triple_single = content.count("'''")
print(f"Triple single quotes: {triple_single}")

# Find lines with triple quotes
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if '"""' in line or "'''" in line:
        if i > 6870 and i < 6950:  # Focus on problem area
            print(f"Line {i}: {line.strip()}")