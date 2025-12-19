#!/usr/bin/env python3
"""
Find the exact location of unclosed triple quotes
"""

def find_unclosed_quote():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track triple quotes
    triple_quote_positions = []
    
    # Find all triple quotes (both """ and ''')
    i = 0
    while i < len(content) - 2:
        if content[i:i+3] in ['"""', "'''"]:
            # Find line number
            line_num = content[:i].count('\n') + 1
            triple_quote_positions.append((line_num, i, content[i:i+3]))
            i += 3
        else:
            i += 1
    
    print(f"Found {len(triple_quote_positions)} triple quotes:")
    
    # Check for balance
    quote_stack = []
    for line_num, pos, quote_type in triple_quote_positions:
        if not quote_stack:
            # Start of a string
            quote_stack.append((line_num, pos, quote_type))
        elif quote_stack[-1][2] == quote_type:
            # Matching closing quote
            opening = quote_stack.pop()
            print(f"✅ Matched: Line {opening[0]} to Line {line_num} ({quote_type})")
        else:
            # Different quote type, start new string
            quote_stack.append((line_num, pos, quote_type))
    
    # Check for unclosed quotes
    if quote_stack:
        print(f"\n❌ UNCLOSED QUOTES:")
        for line_num, pos, quote_type in quote_stack:
            print(f"   Line {line_num}: {quote_type} (position {pos})")
            
            # Show context around the unclosed quote
            lines = content.split('\n')
            start_line = max(0, line_num - 3)
            end_line = min(len(lines), line_num + 2)
            
            print(f"   Context:")
            for i in range(start_line, end_line):
                marker = ">>> " if i == line_num - 1 else "    "
                print(f"   {marker}Line {i+1}: {lines[i]}")
            print()
    else:
        print("✅ All quotes are balanced!")

if __name__ == '__main__':
    find_unclosed_quote()