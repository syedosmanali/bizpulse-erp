#!/usr/bin/env python3
"""
Final encoding fix - ensure clean UTF-8 encoding
"""

def final_encoding_fix():
    # Read with error handling
    try:
        with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except:
        with open('app.py', 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Clean the content
    cleaned_lines = []
    for line in content.split('\n'):
        # Replace problematic characters
        line = line.replace('\x8f', '')  # Remove specific problematic byte
        line = line.replace('\ufffd', '')  # Remove replacement characters
        cleaned_lines.append(line)
    
    # Join and write back
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Write with clean UTF-8
    with open('app.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(cleaned_content)
    
    print("✅ Final encoding fix applied!")

if __name__ == '__main__':
    final_encoding_fix()