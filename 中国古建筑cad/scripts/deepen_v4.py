#!/usr/bin/env python3
"""深化 gen_scr.py：添加立面图生成 + 新版式"""
import re

path = r'D:\CodexAutoClip\.codex\skills\chinese-arch-cad\scripts\gen_scr.py'
with open(path, encoding='utf-8') as f:
    content = f.read()
original = content
changes = []

# ===== 1. 版本号 =====
content = content.replace('V4.13', 'V4.14')
changes.append('version V4.13 -> V4.14')

# ===== 2. 添加生成立面图函数 =====
# 插入在 gen_hall_scr 之后，calc_paifang_params 之前

elevation_funcs = '''

# ──────────────────────────────────────────────────
# 立面图生成器
# ──────────────────────────────────────────────────
def gen_elevation_pavilion(p: dict, mode: str) -> str:
    """亭类正立面（沿X轴方向）"""
    B = p["B"]
    n = p["side_num"]
    H = p["H_col"]
    D = p["D_col"]
    h_plinth = p["H_plinth"]
    h_roof = p["h_roof"]
    eave = p["eave"]
    R = p["R_col"]
    
    lines = []
    lines.append(f"; 立面: {p['name']} 正立面（沿X轴）")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("_.ERASE All")
    lines.append("")
    
    for lyr, clr in [("AXIS",1),("BASE",8),("WOOD_FRAME",3),("ROOF",5),("DIM",2),("ANNOTATION",7)]:
        lines.append(f"LAYER NEW {lyr} COLOR {clr} CONTINUOUS")
    lines.append("")
    
    # 地坪线
    lines.append("LINE -{:.0f},0,0 {:.0f},0,0".format(B*3, B*3))
    lines.append("")
    
    # 台基
    lines.append("LAYER BASE")
    pw = B * 1.4
    lines.append(f"RECTANGLE -{pw:.1f},0 {pw:.1f},{h_plinth:.1f}")
    step_h = h_plinth / 3
    for j in range(3):
        off = 100 * (3-j)
        lines.append(f"RECTANGLE -{pw-off:.1f},{j*step_h:.1f} {pw-off:.1f},{(j+1)*step_h:.1f}")
    lines.append("")
    
    # 檐柱（正立面可见2根，左右对称）
    lines.append("LAYER WOOD_FRAME")
    col_w = D
    # 左柱（从正面看，取X轴方向的柱）
    lines.append(f"; 檐柱  高={H:.0f}mm  径={D:.0f}mm")
    lines.append(f"RECTANGLE -{R-col_w/2:.1f},{h_plinth:.1f} {-R+col_w/2:.1f},{h_plinth+H:.1f}")
    lines.append(f"RECTANGLE {R-col_w/2:.1f},{h_plinth:.1f} {R-col_w/2:.1f},{h_plinth+H:.1f}")
    # 前后柱（用虚线表示）
    lines.append("; 前后柱（虚线表示深度）")
    lines.append(f"LINE -{R:.1f},{h_plinth:.1f} -{R:.1f},{h_plinth+H:.1f}")
    lines.append(f"LINE {R:.1f},{h_plinth:.1f} {R:.1f},{h_plinth+H:.1f}")
    lines.append("")
    
    # 斗拱层
    doug_h = D * 0.3
    lines.append("LAYER DOUGONG")
    lines.append(f"RECTANGLE -{R+5:.1f},{h_plinth+H:.1f} {R+5:.1f},{h_plinth+H+doug_h:.1f}")
    lines.append("")
    
    # 屋面（三角形）
    lines.append("LAYER ROOF")
    roof_z = h_plinth + H + doug_h + h_roof
    eave_end = R + eave
    lines.append(f"; 屋面轮廓")
    lines.append(f"LINE -{eave_end:.1f},{h_plinth+H+doug_h:.1f} 0,{roof_z:.1f}")
    lines.append(f"LINE {eave_end:.1f},{h_plinth+H+doug_h:.1f} 0,{roof_z:.1f}")
    ridge_w = D * 2
    lines.append(f"LINE -{ridge_w:.1f},{roof_z:.1f} {ridge_w:.1f},{roof_z:.1f}")
    # 宝顶
    fin_h = 300
    lines.append(f"CIRCLE 0,{roof_z+fin_h/2:.1f} {D*0.4:.1f}")
    lines.append(f"LINE 0,{roof_z:.1f} 0,{roof_z+fin_h:.1f}")
    lines.append("")
    
    # 标注
    lines.append("LAYER DIM")
    lines.append(f"DIMLINEAR 0,{h_plinth:.1f} 0,{roof_z+fin_h:.1f} {pw+200:.0f}")
    lines.append("")
    
    # 文字
    lines.append("LAYER ANNOTATION")
    total_h = h_plinth + H + doug_h + h_roof + fin_h
    lines.append(f"TEXT {pw+200:.0f},{h_plinth/2:.0f} 55 0 H总={total_h:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{h_plinth+H+30:.0f} 55 0 柱高={H:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{roof_z+20:.0f} 55 0  roof={h_roof:.0f}mm")
    lines.append(f"TEXT 0,{roof_z+fin_h+80:.0f} 70 0 {p['name']} 正立面")
    lines.append("")
    lines.append("ZOOM ALL")
    
    return "\\n".join(lines)


def gen_elevation_hall(p: dict, mode: str) -> str:
    """殿类正立面（沿面阔方向）"""
    W = p["total_width"]
    bays = p["bays"]
    H_f = p["H_col_front"]
    H_b = p["H_col_back"]
    D_c = p["D_col"]
    eave_f = p["eave_front"]
    eave_b = p["eave_back"]
    h_roof = p["h_roof"]
    H_p = p["H_plinth"]
    spacing = p["bay_spacing"]
    depth = p.get("depth_bays", 3) * spacing
    
    lines = []
    lines.append(f"; 立面: {p.get('name','殿')} 正立面（沿面阔X轴）")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("_.ERASE All")
    lines.append("")
    
    for lyr, clr in [("AXIS",1),("BASE",8),("WOOD_FRAME",3),("DOUGONG",6),("ROOF",5),("DIM",2),("ANNOTATION",7)]:
        lines.append(f"LAYER NEW {lyr} COLOR {clr} CONTINUOUS")
    lines.append("")
    
    # 地坪
    xl = W + eave_f*2 + 2000
    lines.append(f"LINE -{xl:.0f},0,0 {xl:.0f},0,0")
    lines.append("")
    
    # 台基
    lines.append("LAYER BASE")
    pw = W/2 + eave_f + 300
    lines.append(f"RECTANGLE -{pw:.1f},0 {pw:.1f},{H_p:.1f}")
    step = H_p / 3
    for j in range(3):
        off = 150*(3-j)
        lines.append(f"RECTANGLE -{pw-off:.1f},{j*step:.1f} {pw-off:.1f},{(j+1)*step:.1f}")
    lines.append("")
    
    # 柱网（正面檐柱）
    lines.append("LAYER WOOD_FRAME")
    col_r = D_c / 2
    half_w = W / 2
    for i in range(bays + 1):
        x = -half_w + i * spacing
        lines.append(f"; 檐柱{i+1}  高={H_f:.0f}  径={D_c:.0f}")
        lines.append(f"RECTANGLE {x-col_r:.1f},{H_p:.1f} {x+col_r:.1f},{H_p+H_f:.1f}")
    lines.append("")
    
    # 斗拱层
    doug_h = D_c * 0.3
    lines.append("LAYER DOUGONG")
    for i in range(bays + 1):
        x = -half_w + i * spacing
        lines.append(f"RECTANGLE {x-col_r-5:.1f},{H_p+H_f:.1f} {x+col_r+5:.1f},{H_p+H_f+doug_h:.1f}")
    lines.append("")
    
    # 屋面轮廓（歇山顶）
    lines.append("LAYER ROOF")
    roof_z = H_p + H_f + doug_h + h_roof
    eave_end = half_w + eave_f
    lines.append(f"; 屋面轮廓: 檐口(±{eave_end:.0f}, {H_p+H_f+doug_h:.0f}) -> 正脊(0, {roof_z:.0f})")
    lines.append(f"LINE -{eave_end:.1f},{H_p+H_f+doug_h:.1f} 0,{roof_z:.1f}")
    lines.append(f"LINE {eave_end:.1f},{H_p+H_f+doug_h:.1f} 0,{roof_z:.1f}")
    ridge_w = W * 0.5
    lines.append(f"LINE -{ridge_w/2:.1f},{roof_z:.1f} {ridge_w/2:.1f},{roof_z:.1f}")
    fin_h = 400
    lines.append(f"CIRCLE 0,{roof_z+fin_h/2:.1f} {D_c*0.5:.1f}")
    lines.append(f"LINE 0,{roof_z:.1f} 0,{roof_z+fin_h:.1f}")
    lines.append("")
    
    # 标注
    lines.append("LAYER DIM")
    lines.append(f"DIMLINEAR 0,{H_p:.1f} 0,{roof_z+fin_h:.1f} {pw+200:.0f}")
    lines.append(f"DIMLINEAR -{W/2:.1f},0,0 {W/2:.1f},0,0 0,-{H_p+100:.0f}")
    lines.append("")
    
    # 文字
    lines.append("LAYER ANNOTATION")
    total_h = roof_z + fin_h
    lines.append(f"TEXT {pw+200:.0f},{H_p/2:.0f} 55 0 总高={total_h:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{H_p+H_f+30:.0f} 55 0 前柱高={H_f:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{roof_z+20:.0f} 55 0  roof={h_roof:.0f}mm")
    lines.append(f"TEXT 0,{roof_z+fin_h+80:.0f} 70 0 {p.get('name','殿')} 正立面")
    lines.append("")
    lines.append("ZOOM ALL")
    
    return "\\n".join(lines)


def gen_elevation_paifang(p: dict, mode: str) -> str:
    """牌楼正立面（沿面阔方向）"""
    W = p["W"]
    bays = p["bays"]
    H = p["H_col"]
    D = p["D_col"]
    e = p["eave"]
    h_r = p["h_roof"]
    H_p = p["H_plinth"]
    top_d = p["top_decor"]
    top_e = p["top_extra"]
    style = p["style"]
    is_wood = p["is_wood"]
    double_eave = p["double_eave"]
    
    # 柱位
    if bays == 1:
        col_xs = [-W/2, W/2]
    elif bays == 3:
        half_ming = p["W_ming"] / 2
        col_xs = [-W/2, -half_ming, half_ming, W/2]
    else:
        col_xs = []
        seg = W / (bays)
        for i in range(bays + 1):
            col_xs.append(-W/2 + i * seg)
    
    lines = []
    mat = "木" if is_wood else "石"
    lines.append(f"; 立面: {p.get('name','牌楼')} 正立面（沿面阔X轴） | {bays}间{mat}坊 {style}")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("_.ERASE All")
    lines.append("")
    
    for lyr, clr in [("AXIS",1),("BASE",8),("WOOD_FRAME",3),("DOUGONG",6),("ROOF",5),("DECO",10),("DIM",2),("ANNOTATION",7)]:
        lines.append(f"LAYER NEW {lyr} COLOR {clr} CONTINUOUS")
    lines.append("")
    
    # 地坪线
    xl = W + e*2 + 2000
    lines.append(f"LINE -{xl:.0f},0,0 {xl:.0f},0,0")
    lines.append("")
    
    # 台基
    lines.append("LAYER BASE")
    pw = W/2 + e + 300
    lines.append(f"RECTANGLE -{pw:.1f},0 {pw:.1f},{H_p:.1f}")
    step = H_p / 3
    for j in range(3):
        off = 100*(3-j)
        lines.append(f"RECTANGLE -{pw-off:.1f},{j*step:.1f} {pw-off:.1f},{(j+1)*step:.1f}")
    lines.append("")
    
    # 柱子（正面）
    lines.append("LAYER WOOD_FRAME")
    col_r = D / 2
    for i, cx in enumerate(col_xs):
        lines.append(f"; 柱{i+1}  高={H:.0f}  径={D:.0f}")
        lines.append(f"RECTANGLE {cx-col_r:.1f},{H_p:.1f} {cx+col_r:.1f},{H_p+H:.1f}")
    lines.append("")
    
    # 斗拱层
    doug_h = D * 0.35
    lines.append("LAYER DOUGONG")
    for cx in col_xs:
        lines.append(f"RECTANGLE {cx-col_r-5:.1f},{H_p+H:.1f} {cx+col_r+5:.1f},{H_p+H+doug_h:.1f}")
    lines.append("")
    
    # 一层檐口
    eave1_z = H_p + H + doug_h
    lines.append("LAYER ROOF")
    lines.append(f"; 一层檐口  标高={eave1_z:.0f}mm")
    lines.append(f"LINE -{e:.1f},{eave1_z:.1f} {e:.1f},{eave1_z:.1f}")
    
    if double_eave:
        H2 = p["H_col_upper"]
        e2 = p["eave_upper"]
        lines.append(f"; 二层檐口  标高={eave1_z+H2:.1f}mm")
        lines.append(f"LINE -{e2:.1f},{eave1_z+H2:.1f} {e2:.1f},{eave1_z+H2:.1f}")
        roof_top = eave1_z + H2 + doug_h + h_r + top_d
    else:
        roof_top = eave1_z + h_r + top_d
    
    # 屋面轮廓
    lines.append(f"; 屋面: 檐口(±{e:.0f}, {eave1_z:.0f}) -> 正脊(0, {roof_top:.0f})")
    lines.append(f"LINE -{e:.1f},{eave1_z:.1f} 0,{roof_top:.1f}")
    lines.append(f"LINE {e:.1f},{eave1_z:.1f} 0,{roof_top:.1f}")
    ridge_w = D * 3
    lines.append(f"LINE -{ridge_w:.1f},{roof_top:.1f} {ridge_w:.1f},{roof_top:.1f}")
    
    # 宝顶
    lines.append(f"; 宝顶  高={top_d:.0f}mm")
    lines.append(f"CIRCLE 0,{roof_top+top_d/2:.1f} {top_d/3:.1f}")
    lines.append(f"LINE 0,{roof_top:.1f} 0,{roof_top+top_d:.1f}")
    if top_e > 0:
        lines.append(f"; 冲天柱出头={top_e:.0f}mm")
        lines.append(f"LINE 0,{roof_top+top_d:.1f} 0,{roof_top+top_d+top_e:.1f}")
    lines.append("")
    
    # 匾额（明间）
    lines.append("LAYER DECO")
    plaque_h = H * 0.4
    plaque_w = p["W_ming"] * 0.6
    plaque_z = H_p + H * 0.55
    lines.append(f"; 匾额  位置: 明间柱中")
    lines.append(f"RECTANGLE -{plaque_w/2:.1f},{plaque_z:.1f} {plaque_w/2:.1f},{plaque_z+plaque_h:.1f}")
    lines.append("")
    
    # 标注
    lines.append("LAYER DIM")
    total_h = int(roof_top + top_d + top_e)
    lines.append(f"DIMLINEAR 0,{H_p:.1f} 0,{roof_top+top_d+top_e:.1f} {pw+200:.0f}")
    lines.append(f"DIMLINEAR -{W/2:.1f},0,0 {W/2:.1f},0,0 0,-{H_p+80:.0f}")
    if len(col_xs) >= 3:
        lines.append(f"DIMLINEAR {col_xs[0]:.1f},0,0 {col_xs[1]:.1f},0,0 0,-{H_p+40:.0f}")
    lines.append("")
    
    # 文字
    lines.append("LAYER ANNOTATION")
    lines.append(f"TEXT {pw+200:.0f},{H_p/2:.0f} 55 0 台基={H_p:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{H_p+H/2:.0f} 55 0 柱高={H:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{eave1_z+30:.0f} 55 0 一层檐={eave1_z-H_p:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{roof_top+20:.0f} 55 0  roof={h_r:.0f}mm")
    lines.append(f"TEXT {pw+200:.0f},{roof_top+top_d+top_e+30:.0f} 55 0  总高={total_h}mm")
    lines.append(f"TEXT 0,{roof_top+top_d+top_e+80:.0f} 70 0 {p.get('name','牌楼')} 正立面")
    lines.append("")
    lines.append("ZOOM ALL")
    
    return "\\n".join(lines)


# ──────────────────────────────────────────────────
'''

# Insert before calc_paifang_params
marker = '# ──────────────────────────────────────────────────\n# 牌楼参数计算'
if marker in content and 'def gen_elevation_pavilion' not in content:
    content = content.replace(marker, elevation_funcs + marker)
    changes.append('added elevation generators')

# ===== 3. 更新 main() 添加立面输出 =====
old_main_out = '''    plan_path = out_dir / f"{name}_plan.scr"
    sec_path = out_dir / f"{name}_section.scr"

    # �������ɵ� JSON����׼����'''
new_main_out = '''    plan_path = out_dir / f"{name}_plan.scr"
    sec_path = out_dir / f"{name}_section.scr"
    elev_path = out_dir / f"{name}_elevation.scr"

    # �������ɵ� JSON����׼����'''
content = content.replace(old_main_out, new_main_out)

# Update the print output in main
old_print = '''    print(f"[OK] {name}")
    print(f"  ƽ��ͼ: {plan_path}")
    print(f"  ����ͼ: {sec_path}")
    print(f"  ����:  {json_out}")
    print(f"  ģʽ:  {args.mode}")'''
new_print = '''    print(f"[OK] {name}")
    print(f"  ƽ��ͼ: {plan_path}")
    print(f"  ����ͼ: {sec_path}")
    print(f"  ����ͼ: {elev_path}")
    print(f"  ����:  {json_out}")
    print(f"  ģʽ:  {args.mode}")'''
content = content.replace(old_print, new_print)

# Add elevation generation after plan/section
old_write = '''    plan_path.write_text(plan, encoding="utf-8")
    sec_path.write_text(section, encoding="utf-8")'''
new_write = '''    plan_path.write_text(plan, encoding="utf-8")
    sec_path.write_text(section, encoding="utf-8")
    
    # ���̽�ͼ���ɣ�
    if has_corridor or cat == "��" or "��" in sid or "��" in name:
        elev = gen_elevation_hall(params, args.mode)
    elif has_monument:
        elev = gen_elevation_paifang(params, args.mode)
    elif cat == "ͤ" or "�ܼ�" in sid or "ͤ" in name:
        elev = gen_elevation_pavilion(params, args.mode)
    else:
        elev = gen_elevation_pavilion(params, args.mode)
    elev_path.write_text(elev, encoding="utf-8")'''
content = content.replace(old_write, new_write)
changes.append('added elevation output in main()')

# ===== 4. 添加新模板 =====
templates = [
    ("paifang_5bay_chongtian.json", '''{
  "id": "paifang_5bay_chongtian",
  "name": "清式五间冲天石牌坊",
  "category": "坊",
  "subtype": "五间冲天石牌楼",
  "W": 24000,
  "bays": 5,
  "bay_spacing": [4800, 4800, 4800, 4800, 4800],
  "depth": 3200,
  "column_style": "chongtian",
  "roof_type": "xieshan",
  "material": "stone"
}'''),
    ("pavilion_hex_2m.json", '''{
  "id": "pavilion_hex_2m",
  "name": "清式六角攒尖亭 B=2000mm",
  "B": 2000,
  "side_num": 6
}'''),
    ("pavilion_hex_5m.json", '''{
  "id": "pavilion_hex_5m",
  "name": "清式六角攒尖亭 B=5000mm",
  "B": 5000,
  "side_num": 6
}'''),
    ("pavilion_oct_5m.json", '''{
  "id": "pavilion_oct_5m",
  "name": "清式八角攒尖亭 B=5000mm",
  "B": 5000,
  "side_num": 8
}'''),
    ("hall_wudian_5bay.json", '''{
  "id": "hall_wudian_5bay",
  "name": "清式单檐庑殿殿 面阔五间",
  "category": "殿",
  "subtype": "单檐庑殿",
  "bays_width": 5,
  "bay_spacing": 3600,
  "depth_bays": 3
}'''),
    ("corridor_3bay.json", '''{
  "id": "corridor_3bay",
  "name": "清式三间抄手游廊",
  "category": "廊",
  "subtype": "抄手游廊",
  "bays_width": 3,
  "bay_spacing": 3000,
  "depth_bays": 1
}'''),
    ("paifang_1bay_chongtian.json", '''{
  "id": "paifang_1bay_chongtian",
  "name": "清式单间冲天石牌坊",
  "category": "坊",
  "subtype": "单间冲天石牌楼",
  "W": 3600,
  "bays": 1,
  "depth": 1800,
  "column_style": "chongtian",
  "roof_type": "xieshan",
  "material": "stone"
}'''),
]

for fname, fcontent in templates:
    import json as json_mod
    try:
        json_mod.loads(fcontent)  # Validate JSON
    except:
        print(f"Invalid JSON in {fname}")
        continue
    tpl_path = rf'D:\CodexAutoClip\.codex\skills\chinese-arch-cad\assets\templates\{fname}'
    with open(tpl_path, 'w', encoding='utf-8') as f:
        f.write(fcontent)
    changes.append(f'added template: {fname}')

# Write back
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
import ast
try:
    ast.parse(content)
    print('Syntax OK')
except SyntaxError as e:
    print(f'SYNTAX ERROR: {e}')
    exit(1)

print(f'Applied {len(changes)} changes:')
for c in changes:
    print(f'  OK {c}')
