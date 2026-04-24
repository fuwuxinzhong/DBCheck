#!/usr/bin/env python3
"""修复 MySQL/PG/DM8 报告的 Word 表格样式，对齐 Oracle 配色"""

import re

# ── Oracle 标准色 ────────────────────────────────────────────────────────
HEADER_BG   = '336699'   # 深蓝表头背景
HEADER_FG   = (255, 255, 255)  # 白色字体

# ── MySQL / PG: 替换策略 ──────────────────────────────────────────────────
# 每个 `table.style = 'Light Grid Accent 1'` 后，
# 将表头行改为：深蓝背景 + 白色粗体居中

def patch_mysql_pg(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # 1. 在 saveDoc._t 方法后插入 _set_cell_bg
        if line.strip().startswith('def _t(self, key):'):
            new_lines.append(line)
            i += 1
            # 复制方法内容
            while i < len(lines) and not lines[i].strip().startswith('def '):
                new_lines.append(lines[i])
                i += 1
            # 插入 _set_cell_bg
            new_lines.append('\n')
            new_lines.append('    def _set_cell_bg(self, cell, hex_color):\n')
            new_lines.append('        from docx.oxml.ns import nsdecls\n')
            new_lines.append('        from docx.oxml import parse_xml\n')
            new_lines.append('        try:\n')
            new_lines.append("            shading = parse_xml(f'<w:shd {nsdecls(\"w\")} w:fill=\"{hex_color}\"/>')\n")
            new_lines.append('            cell._tc.get_or_add_tcPr().append(shading)\n')
            new_lines.append('        except Exception:\n')
            new_lines.append('            pass\n')
            continue

        # 2. 替换 table.style = 'Light Grid Accent 1' → 'Table Grid'
        if "table.style = 'Light Grid Accent 1'" in line:
            new_lines.append(line.replace("'Light Grid Accent 1'", "'Table Grid'"))
            i += 1
            continue

        if "tbl.style = 'Light Grid Accent 1'" in line:
            new_lines.append(line.replace("'Light Grid Accent 1'", "'Table Grid'"))
            i += 1
            continue

        # 3. 在 tbl.style = 'Table Grid'（由上面替换得到）后插入表头深蓝背景处理
        #    找到 `tbl.rows[0].cells` 的表头设置循环，在 `cell.width = col_w[j]` 前插入
        if ('tbl.style' in line and "'Table Grid'" in line) or ('table.style' in line and "'Table Grid'" in line):
            new_lines.append(line)
            i += 1
            # 跳过可能的 tbl.autofit = True
            if i < len(lines) and 'autofit' in lines[i]:
                new_lines.append(lines[i])
                i += 1
            # 找到表头循环 hdrs = [...]
            while i < len(lines) and 'hdrs' not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            if i < len(lines):
                new_lines.append(lines[i])  # hdrs = ...
                i += 1
            # 找到 for j,(cell,ht) 开始，插入深蓝背景
            while i < len(lines) and 'for j,' not in lines[i] and 'for j, ' not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            if i < len(lines):
                # 替换整个表头设置循环
                new_lines.append('                    for j, (cell, ht) in enumerate(zip(tbl.rows[0].cells, hdrs)):\n')
                i += 1
                # 跳过原来的 cell.text = ht
                while i < len(lines) and 'cell.text = ht' in lines[i]:
                    new_lines.append('                        cell.text = ht\n')
                    new_lines.append('                        try:\n')
                    new_lines.append('                            self._set_cell_bg(cell, \'336699\')\n')
                    new_lines.append('                        except Exception:\n')
                    new_lines.append('                            pass\n')
                    i += 1
                # 跳过原来的 bold+size，替换为 bold+size+white+center
                while i < len(lines) and ('runs[0].bold = True' in lines[i] or 'runs[0].font.size = Pt' in lines[i]):
                    i += 1  # skip original
                # 添加新的白色+居中+粗体+字号
                new_lines.append('                        cell.paragraphs[0].runs[0].bold = True\n')
                new_lines.append('                        cell.paragraphs[0].runs[0].font.size = Pt(9)\n')
                new_lines.append('                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)\n')
                new_lines.append('                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER\n')
                # 保留 cell.width = col_w[j]
                while i < len(lines) and 'cell.width = col_w[j]' not in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    new_lines.append(lines[i])  # cell.width = col_w[j]
                    i += 1
            continue

        # 4. tbl = doc2.add_table / doc.add_table（无 col_w 的普通表），在 style 后加表头处理
        #    匹配模式: tbl = doc.add_table(...) 后跟 tbl.style = 'Table Grid'
        if ('tbl = doc2.add_table' in line or 'tbl = doc.add_table' in line) and 'style' not in line:
            new_lines.append(line)
            i += 1
            # 可能跳过 autofit
            if i < len(lines) and 'autofit' in lines[i]:
                new_lines.append(lines[i])
                i += 1
            # 找 hdrs 或 headers
            while i < len(lines) and 'hdr' not in lines[i].lower() and 'header' not in lines[i].lower():
                new_lines.append(lines[i])
                i += 1
            if i < len(lines):
                new_lines.append(lines[i])  # hdrs = ...
                i += 1
            # 找 for j,(cell,ht) 或类似的表头循环
            while i < len(lines) and 'for j,' not in lines[i] and 'for j, ' not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            if i < len(lines) and 'for j,' in lines[i]:
                new_lines.append(lines[i])
                i += 1
                # 跳过原来的 cell.text = ht
                while i < len(lines) and 'cell.text = ht' in lines[i]:
                    new_lines.append('                        cell.text = ht\n')
                    new_lines.append('                        try:\n')
                    new_lines.append('                            self._set_cell_bg(cell, \'336699\')\n')
                    new_lines.append('                        except Exception:\n')
                    new_lines.append('                            pass\n')
                    i += 1
                while i < len(lines) and ('runs[0].bold = True' in lines[i] or 'runs[0].font.size = Pt' in lines[i]):
                    i += 1
                new_lines.append('                        cell.paragraphs[0].runs[0].bold = True\n')
                new_lines.append('                        cell.paragraphs[0].runs[0].font.size = Pt(9)\n')
                new_lines.append('                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)\n')
                new_lines.append('                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER\n')
                # 复制剩余内容直到回到正常流
                while i < len(lines) and 'cell.width = col_w[j]' not in lines[i] and lines[i].strip() and not lines[i].strip().startswith('#'):
                    new_lines.append(lines[i])
                    i += 1
                if i < len(lines) and 'cell.width = col_w[j]' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
            continue

        new_lines.append(line)
        i += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Patched: {filepath}")


def patch_dm8(filepath):
    """DM8: DCE6F1 → 336699, F2F2F2 → F2F2F2 (保持灰色标签列)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("'DCE6F1'", "'336699'")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched DM8 color: {filepath}")


if __name__ == '__main__':
    patch_mysql_pg(r'D:\DBCheck\main_mysql.py')
    patch_mysql_pg(r'D:\DBCheck\main_pg.py')
    patch_dm8(r'D:\DBCheck\main_dm.py')
    print('Done.')
