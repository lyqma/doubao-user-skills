#!/usr/bin/env python3
"""修复 gen_scr.py 的 elev_path 定义问题"""
path = r'D:\CodexAutoClip\.codex\skills\chinese-arch-cad\scripts\gen_scr.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, l in enumerate(lines):
    new_lines.append(l)
    # After sec_path line, add elev_path
    if 'sec_path = out_dir' in l and 'elev' not in l:
        indent = len(l) - len(l.lstrip())
        new_lines.append(' ' * indent + 'elev_path = out_dir / f"{name}_elevation.scr"\n')
        print(f'Inserted elev_path after line {i+1}')

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

import ast
ast.parse(open(path, encoding='utf-8').read())
print('Syntax OK')
