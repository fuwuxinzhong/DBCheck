#!/usr/bin/env python3
import re

for fp in [r'D:\DBCheck\main_mysql.py', r'D:\DBCheck\main_pg.py']:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修复已损坏的 table'Table Grid' → table.style = 'Table Grid'
    content = content.replace("table'Table Grid'", "table.style = 'Table Grid'")
    content = content.replace("tbl'Table Grid'", "tbl.style = 'Table Grid'")

    # 2. 把所有剩下的 'Light Grid Accent 1' 替换为 'Table Grid'（带变量名）
    # 匹配 tbl.style = 'Light Grid Accent 1' 或 table.style = ... 或 obj.style = ...
    content = re.sub(r"(\w+)\.style\s*=\s*'Light Grid Accent 1'", r"\1.style = 'Table Grid'", content)

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

    broken = content.count("'Table Grid'")
    print(f'{fp}: fixed. Total Table Grid references: {broken}')

print('Done.')
