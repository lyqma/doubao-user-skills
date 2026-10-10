#!/usr/bin/env python3
"""Fix all templates with proper UTF-8 category/subtype"""
import json, os

tpl_dir = r'D:\CodexAutoClip\.codex\skills\chinese-arch-cad\assets\templates'
fixes = {
    'paifang_1bay_stone.json': {'category': '坊', 'subtype': '单间石牌楼'},
    'paifang_1bay_chongtian.json': {'category': '坊', 'subtype': '单间冲天石牌楼'},
    'paifang_3bay_stone.json': {'category': '坊', 'subtype': '三间石牌楼'},
    'paifang_3bay_chongtian.json': {'category': '坊', 'subtype': '四柱三间冲天式'},
    'paifang_3bay_wood.json': {'category': '坊', 'subtype': '三间木牌楼'},
    'paifang_3bay_chongtian_wood.json': {'category': '坊', 'subtype': '四柱三间冲天式木牌楼'},
    'paifang_3bay_wood_double_eave.json': {'category': '坊', 'subtype': '三间双檐木牌楼'},
    'paifang_5bay_stone.json': {'category': '坊', 'subtype': '五间石牌楼'},
    'paifang_5bay_chongtian.json': {'category': '坊', 'subtype': '五间冲天石牌楼'},
    'hall_xieshan_3bay.json': {'category': '殿', 'subtype': '单檐歇山'},
    'hall_xieshan_5bay.json': {'category': '殿', 'subtype': '单檐歇山'},
    'hall_xieshan_7bay.json': {'category': '殿', 'subtype': '单檐歇山'},
    'hall_wudian_5bay.json': {'category': '殿', 'subtype': '单檐庑殿'},
    'corridor_3bay.json': {'category': '廊', 'subtype': '抄手游廊'},
    'pavilion_hex_2m.json': {'category': '亭', 'subtype': '六角攒尖'},
    'pavilion_hex_3m.json': {'category': '亭', 'subtype': '六角攒尖'},
    'pavilion_hex_4m.json': {'category': '亭', 'subtype': '六角攒尖'},
    'pavilion_hex_5m.json': {'category': '亭', 'subtype': '六角攒尖'},
    'pavilion_oct_3.6m.json': {'category': '亭', 'subtype': '八角攒尖'},
    'pavilion_oct_4m.json': {'category': '亭', 'subtype': '八角攒尖'},
    'pavilion_oct_5m.json': {'category': '亭', 'subtype': '八角攒尖'},
}

for fname, fix_dict in fixes.items():
    fpath = os.path.join(tpl_dir, fname)
    if not os.path.exists(fpath):
        print(f'MISSING: {fname}')
        continue
    with open(fpath, encoding='utf-8') as f:
        cfg = json.load(f)
    for k, v in fix_dict.items():
        cfg[k] = v
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f'OK {fname}: cat={cfg[\"category\"]} sid={cfg.get(\"subtype\",\"\")}')
