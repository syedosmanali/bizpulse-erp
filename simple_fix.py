#!/usr/bin/env python3
"""Simple fix for the unmatched quote"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count triple single quotes
count = content.count("'''")
print(f"Current count: {count}")

if count % 2 == 1:  # Odd number means unmatched
    # Add one more at the end
    content += "\n'''"
    print("Added closing triple quote")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")