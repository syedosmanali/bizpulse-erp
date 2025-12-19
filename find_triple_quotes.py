#!/usr/bin/env python3
"""
Find all triple quotes in app.py to identify unclosed ones
"""

def find_triple_quotes():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    triple_quote_count = 0
    in_string = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Count triple quotes in this line
        count = line.count('"""') + line.count("'''")
        
        if count > 0:
            print(f"Line {line_num}: {count} triple quotes - {repr(line.strip())}")
            triple_quote_count += count
    
    print(f"\nTotal triple quotes: {triple_quote_count}")
    if triple_quote_count % 2 != 0:
        print("❌ Odd number of triple quotes - there's an unclosed string!")
    else:
        print("✅ Even number of triple quotes - should be balanced")

if __name__ == '__main__':
    find_triple_quotes()