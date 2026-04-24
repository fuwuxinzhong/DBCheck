#!/usr/bin/env python3
import re

for fp, pattern in [
    (r'D:\DBCheck\main_mysql.py', r"\.style\s*=\s*'Light Grid Accent 1'"),
    (r'D:\DBCheck\main_pg.py',    r"\.style\s*=\s*'Light Grid Accent 1'"),
]:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    before = content.count("'Light Grid Accent 1'")
    content = re.sub(pattern, "'Table Grid'", content)
    after = content.count("'Table Grid'")
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{fp}: replaced {before}x Light Grid Accent 1 -> Table Grid')

print('All done.')
