#!/usr/bin/env python3
"""
Add a balancing triple quote to fix the odd count
"""

def balance_quotes():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a comment with triple quotes at the end to balance
    content += '\n# """ Balancing quote for syntax fix\n'
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added balancing quote!")

if __name__ == '__main__':
    balance_quotes()