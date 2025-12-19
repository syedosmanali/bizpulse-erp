#!/usr/bin/env python3
"""Find unmatched triple quotes"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

triple_single_count = 0
triple_double_count = 0

for i, line in enumerate(lines, 1):
    triple_single_count += line.count("'''")
    triple_double_count += line.count('"""')
    
    # Check if we have an odd number at any point around the error area
    if i >= 6870 and i <= 6950:
        if triple_single_count % 2 != 0:
            print(f"Line {i}: Odd triple single quotes count: {triple_single_count}")
            print(f"Line content: {line.strip()}")
            
print(f"Final counts - Triple single: {triple_single_count}, Triple double: {triple_double_count}")

# Find the exact line with unmatched quote
in_string = False
quote_type = None
for i, line in enumerate(lines, 1):
    if "'''" in line:
        count = line.count("'''")
        if count % 2 == 1:  # Odd number means it opens or closes a string
            if not in_string:
                in_string = True
                quote_type = "single"
                print(f"String starts at line {i}: {line.strip()}")
            elif quote_type == "single":
                in_string = False
                quote_type = None
                print(f"String ends at line {i}: {line.strip()}")
    
    if i > 6870 and i < 6950 and in_string:
        print(f"Still in string at line {i}")
        break