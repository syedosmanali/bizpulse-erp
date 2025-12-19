with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count triple quotes
triple_quote_count = content.count("'''")
print(f'Total triple quotes: {triple_quote_count}')
print(f'Should be even: {triple_quote_count % 2 == 0}')

# Find positions of triple quotes
import re
positions = []
for match in re.finditer(r"'''", content):
    line_num = content[:match.start()].count('\n') + 1
    positions.append((line_num, match.start()))

print('Triple quote positions:')
for i, (line, pos) in enumerate(positions):
    print(f'{i+1:2d}. Line {line:4d}')