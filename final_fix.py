#!/usr/bin/env python3
"""
Final fix - Remove any hidden characters and ensure proper encoding
"""

def final_fix():
    # Read the file with explicit encoding
    with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Clean any potential hidden characters
    content = content.replace('\r\n', '\n')  # Fix Windows line endings
    content = content.replace('\r', '\n')    # Fix old Mac line endings
    
    # Remove any non-printable characters except newlines and tabs
    cleaned_content = ''
    for char in content:
        if char.isprintable() or char in ['\n', '\t']:
            cleaned_content += char
        else:
            # Replace non-printable characters with space
            cleaned_content += ' '
    
    # Write back with clean UTF-8 encoding
    with open('app.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(cleaned_content)
    
    print("✅ Final cleanup applied!")

if __name__ == '__main__':
    final_fix()