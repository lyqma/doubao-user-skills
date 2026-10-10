#!/usr/bin/env python3
"""
古建参数化 SCR 脚本生成器 V4.14
读取 JSON 配置文件，输出 AutoCAD .scr 绘图脚本。
用法: python gen_scr.py <input.json> [--output <dir>] [--mode quick_shell|full_detail]
"""
import json
import math
import argparse
from pathlib import Path

# ──────────────────────────────────────────────────
# 清式比例公式（亭类，从 B 推导）
# ──────────────────────────────────────────────────
def calc_pavilion_params(B: float, side_num: int = 6) -> dict:
    W = B / math.sqrt(3) if side_num == 6 else B / 2.613
    H_col = B * 0.75
    D_col = H_col * 0.085
    eave = B * (0.32 if side_num == 6 else 0.30)
    h_roof = B * (0.40 if side_num == 6 else 0.38)
    H_plinth = max(B * 0.133, 400.0)
    R_col = B / 2.0 if side_num == 6 else B / 2.613
    Kau_h = H_col * 0.40
    return dict(
        B=B, W=W, H_col=H_col, D_col=D_col,
        eave=eave, h_roof=h_roof, H_plinth=H_plinth,
        R_col=R_col, Kau_h=Kau_h, side_num=side_num
    )

# ──────────────────────────────────────────────────
# 清式比例公式（殿类，从斗口 K 推导）
# ──────────────────────────────────────────────────
def calc_hall_params(bays: int, bay_spacing: float) -> dict:
    total_width = bays * bay_spacing
    K = total_width / 10.0
    H_col_front = total_width * 0.58
    H_col_back = total_width * 0.52
    D_col = H_col_front * 0.10
    eave_front = total_width * 0.28
    eave_back = total_width * 0.18
    h_roof = total_width * 0.55
    H_plinth = total_width * 0.10
    return dict(
        total_width=total_width, K=K,
        H_col_front=H_col_front, H_col_back=H_col_back,
        D_col=D_col, eave_front=eave_front, eave_back=eave_back,
        h_roof=h_roof, H_plinth=H_plinth,
        bays=bays, bay_spacing=bay_spacing
    )

# ──────────────────────────────────────────────────
# SCR 脚本生成器 — 六角/八角攒尖亭
# ──────────────────────────────────────────────────
def gen_pavilion_scr(p: dict, mode: str) -> tuple[str, str]:
    """返回 (plan_scr, section_scr)"""
    B = p["B"]
    n = p["side_num"]
    R = p["R_col"]
    D = p["D_col"]
    H = p["H_col"]
    h_plinth = p["H_plinth"]
    h_roof = p["h_roof"]
    eave = p["eave"]
    angle_step = 360.0 / n

    # ── 平面图 ──
    lines = []
    lines.append(f"; {p.get('name','亭')} | B={B:.0f}mm | {mode}")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("LAYER NEW AXIS COLOR 1 CENTER")
    lines.append("LAYER NEW BASE COLOR 8 CONTINUOUS")
    lines.append("LAYER NEW WOOD_FRAME COLOR 3 CONTINUOUS")
    lines.append("LAYER NEW ROOF COLOR 5 CONTINUOUS")
    lines.append("LAYER NEW RAIL COLOR 4 CONTINUOUS")
    lines.append("LAYER NEW DIM COLOR 2 CONTINUOUS")
    lines.append("LAYER NEW ANNOTATION COLOR 7 CONTINUOUS")
    lines.append("")

    # 轴线
    lines.append("_.ERASE All")
    lines.append("")
    lines.append("LAYER AXIS")
    axis_len = max(B * 5, 10000)
    lines.append(f"LINE -{axis_len},0,0 {axis_len},0,0")
    lines.append(f"LINE 0,-{axis_len},0 0,{axis_len},0")
    lines.append("")

    # 台基多边形
    lines.append("LAYER BASE")
    R_base = B * 1.2
    lines.append(f"_.POLYGON {n} 0,0,0 I {R_base:.1f}")
    lines.append("")

    # 柱定位圆
    lines.append("LAYER WOOD_FRAME")
    lines.append(f"CIRCLE 0,0,0 {R:.1f}")
    lines.append("")

    # 柱位 + 柱圈
    lines.append(f"; 柱位: {n}根, 半径={R:.1f}mm, 柱径={D:.1f}mm")
    col_r = D / 2.0
    for i in range(n):
        ang_deg = i * angle_step
        ang_rad = math.radians(ang_deg)
        x = R * math.cos(ang_rad)
        y = R * math.sin(ang_rad)
        lines.append(f"CIRCLE {x:.1f},{y:.1f},0 {col_r:.1f}")
    lines.append("")

    # 檐枋连线（相邻柱位）
    lines.append("; 檐枋连线")
    for i in range(n):
        a1 = math.radians(i * angle_step)
        a2 = math.radians((i + 1) * angle_step)
        x1, y1 = R * math.cos(a1), R * math.sin(a1)
        x2, y2 = R * math.cos(a2), R * math.sin(a2)
        lines.append(f"LINE {x1:.1f},{y1:.1f},0 {x2:.1f},{y2:.1f},0")
    lines.append("")

    # 出檐外轮廓（攒尖顶投影圆）
    lines.append("LAYER ROOF")
    R_roof = R + eave
    lines.append(f"CIRCLE 0,0,0 {R_roof:.1f}")
    lines.append("")

    # 尺寸标注
    lines.append("LAYER DIM")
    lines.append(f"DIMLINEAR -{R:.1f},0,0 {R:.1f},0,0 0,-{B*0.15:.0f}")
    lines.append("")

    # 标注文字
    lines.append("LAYER ANNOTATION")
    lines.append(f"TEXT 0,{R+200:.0f} 80 0 {p['name']} B={B:.0f}mm {n}角攒尖")
    lines.append(f"TEXT 0,{R+120:.0f} 60 0 檐柱高={H:.0f}mm  柱径={D:.0f}mm  出檐={eave:.0f}mm")
    lines.append(f"TEXT 0,{R+50:.0f} 60 0 屋面举高={h_roof:.0f}mm  台基高={h_plinth:.0f}mm")
    lines.append("")
    lines.append("ZOOM ALL")

    # ── full_detail 模式追加内容 ──
    if mode == "full_detail":
        # 斗拱层（每根柱顶方形垫块）
        lines.append("LAYER DOUGONG")
        for i in range(n):
            ang_deg = i * angle_step
            ang_rad = math.radians(ang_deg)
            x = R * math.cos(ang_rad)
            y = R * math.sin(ang_rad)
            dg_w = D * 0.4
            lines.append(f"RECTANGLE {x-dg_w:.1f},{y-dg_w:.1f},0 {x+dg_w:.1f},{y+dg_w:.1f},0")
        lines.append("")
        # 栏杆/美人靠（内圈圆弧 + 立柱）
        lines.append("LAYER RAIL")
        r_rail = R - col_r - 60
        if r_rail > 100:
            lines.append(f"CIRCLE 0,0,0 {r_rail:.1f}")
            for i in range(n):
                ang_deg = (i + 0.5) * angle_step
                ang_rad = math.radians(ang_deg)
                rx = r_rail * math.cos(ang_rad)
                ry = r_rail * math.sin(ang_rad)
                lines.append(f"CIRCLE {rx:.1f},{ry:.1f},0 {col_r*0.5:.1f}")
        lines.append("")
        # 台阶外扩
        lines.append("LAYER BASE")
        step_r = R_base + 300
        lines.append(f"_.POLYGON {n} 0,0,0 O {step_r:.1f}")

    plan_scr = "\n".join(lines)

    # ── 剖面图（沿 X 轴切，取正东-正西方向） ──
    sec = []
    sec.append(f"; 剖面: {p['name']} 沿 X 轴 (Y=0)")
    sec.append("; 底层单位: mm")
    sec.append("")
    sec.append("_.ERASE All")
    sec.append("")
    sec.append("LAYER NEW AXIS COLOR 1 CENTER")
    sec.append("LAYER NEW BASE COLOR 8 CONTINUOUS")
    sec.append("LAYER NEW WOOD_FRAME COLOR 3 CONTINUOUS")
    sec.append("LAYER NEW ROOF COLOR 5 CONTINUOUS")
    sec.append("LAYER NEW DIM COLOR 2 CONTINUOUS")
    sec.append("LAYER NEW ANNOTATION COLOR 7 CONTINUOUS")
    sec.append("")

    # 地坪线
    sec.append("LAYER AXIS")
    sec.append(f"LINE -{R_roof+500:.0f},0,0 {R_roof+500:.0f},0,0")
    sec.append("")

    # 台基
    sec.append("LAYER BASE")
    base_w = R_base + 300
    sec.append(f"RECTANGLE -{base_w:.1f},0 {base_w:.1f},{h_plinth:.1f}")
    # 台阶收分
    step_h = h_plinth / 3.0
    for j in range(3):
        y_bot = j * step_h
        y_top = (j + 1) * step_h
        offset = 100 * (3 - j)
        sec.append(f"RECTANGLE -{base_w-offset:.1f},{y_bot:.1f} {base_w-offset:.1f},{y_top:.1f}")
    sec.append("")

    # 檐柱（左右对称两根）
    sec.append("LAYER WOOD_FRAME")
    col_w = D
    sec.append(f"; 左柱  底标高={h_plinth:.0f}  顶标高={h_plinth+H:.0f}")
    sec.append(f"RECTANGLE -{R:.1f},{h_plinth:.1f} {-R+col_w:.1f},{h_plinth+H:.1f}")
    sec.append(f"RECTANGLE {R-col_w:.1f},{h_plinth:.1f} {R:.1f},{h_plinth+H:.1f}")
    sec.append("")

    # 檐枋
    sec.append("; 檐枋（连续梁）")
    eave_beam_h = D * 0.7
    eave_beam_w = R * 2 + eave * 2
    sec.append(f"RECTANGLE -{eave_beam_w/2:.1f},{h_plinth+H:.1f} {eave_beam_w/2:.1f},{h_plinth+H+eave_beam_h:.1f}")
    sec.append("")

    # 屋面（三角形轮廓，攒尖）
    sec.append("LAYER ROOF")
    roof_top_z = h_plinth + H + eave_beam_h + h_roof
    eave_end = R + eave
    sec.append(f"; 屋面轮廓: 檐口({eave_end:.0f}, {h_plinth+H+eave_beam_h:.0f}) → 正脊(0, {roof_top_z:.0f})")
    sec.append(f"LINE -{eave_end:.1f},{h_plinth+H+eave_beam_h:.1f} 0,{roof_top_z:.1f}")
    sec.append(f"LINE {eave_end:.1f},{h_plinth+H+eave_beam_h:.1f} 0,{roof_top_z:.1f}")
    # 正脊短线
    ridge_w = D * 2
    sec.append(f"LINE -{ridge_w:.1f},{roof_top_z:.1f} {ridge_w:.1f},{roof_top_z:.1f}")
    # 宝顶
    finial_h = 300
    finial_r = D * 0.6
    sec.append(f"CIRCLE 0,{roof_top_z+finial_h/2:.1f} {finial_r:.1f}")
    sec.append(f"LINE 0,{roof_top_z:.1f} 0,{roof_top_z+finial_h:.1f}")
    sec.append("")

    # 尺寸标注
    sec.append("LAYER DIM")
    sec.append(f"DIMLINEAR 0,{h_plinth:.1f} 0,{roof_top_z+finial_h:.1f} {base_w+200:.0f}")
    sec.append("")

    # 标注文字
    sec.append("LAYER ANNOTATION")
    sec.append(f"TEXT {base_w+200:.0f},{h_plinth/2:.0f} 60 0 H=柱{H:.0f}")
    sec.append(f"TEXT {base_w+200:.0f},{h_plinth+H/2:.0f} 60 0 h=檐{eave:.0f}")
    sec.append(f"TEXT {base_w+200:.0f},{roof_top_z:.0f} 60 0 H roof={h_roof:.0f}")
    sec.append(f"TEXT 0,{h_plinth+H+eave_beam_h+200:.0f} 70 0 {p['name']} 剖面")
    sec.append("")
    # ── full_detail 模式追加内容（剖面） ──
    if mode == "full_detail":
        sec.append("LAYER DOUGONG")
        sec.append(f"; 斗拱层  高≈{eave_beam_h:.0f}mm（详图加强）")
        sec.append(f"RECTANGLE -{R+eave/2:.1f},{h_plinth+H:.1f} {R+eave/2:.1f},{h_plinth+H+eave_beam_h:.1f}")
        sec.append("LAYER RAIL")
        rail_h = h_plinth + H * 0.35
        sec.append(f"LINE -{R:.1f},{rail_h:.1f} {R:.1f},{rail_h:.1f}")
    sec.append("ZOOM ALL")

    section_scr = "\n".join(sec)
    return plan_scr, section_scr

# ──────────────────────────────────────────────────
# SCR 脚本生成器 — 歇山殿
# ──────────────────────────────────────────────────
def gen_hall_scr(p: dict, mode: str) -> tuple[str, str]:
    """返回 (plan_scr, section_scr)  歇山殿"""
    K = p["K"]
    W = p["total_width"]
    H_f = p["H_col_front"]
    H_b = p["H_col_back"]
    D_c = p["D_col"]
    eave_f = p["eave_front"]
    eave_b = p["eave_back"]
    h_roof = p["h_roof"]
    H_p = p["H_plinth"]
    bays = p["bays"]
    spacing = p["bay_spacing"]
    depth_bays = p.get("depth_bays", 3)
    depth = depth_bays * spacing

    lines = []
    lines.append(f"; {p.get('name','歇山殿')} | 面阔{bays}间 进深{depth_bays}架 | K={K:.0f}mm | {mode}")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("_.ERASE All")
    lines.append("")

    # 图层
    for layer, color, lt in [
        ("AXIS", 1, "CENTER"), ("BASE", 8, "CONTINUOUS"),
        ("WOOD_FRAME", 3, "CONTINUOUS"), ("ROOF", 5, "CONTINUOUS"),
        ("DIM", 2, "CONTINUOUS"), ("ANNOTATION", 7, "CONTINUOUS")
    ]:
        lines.append(f"LAYER NEW {layer} COLOR {color} {lt}")
    lines.append("")

    # 轴线网格
    lines.append("LAYER AXIS")
    x_len = W + eave_f + eave_b + 2000
    y_len = depth + 2000
    lines.append(f"LINE -{x_len:.0f},0,0 {x_len:.0f},0,0")
    lines.append(f"LINE 0,-{y_len:.0f},0 0,{y_len:.0f},0")
    # 面阔方向轴线
    for i in range(bays + 1):
        x = -W/2 + i * spacing
        lines.append(f"LINE {x:.0f},-{y_len:.0f},0 {x:.0f},{y_len:.0f},0")
    # 进深方向轴线
    lines.append(f"LINE -{x_len:.0f},0,0 {x_len:.0f},0,0")
    lines.append("")

    # 柱网（外檐柱）
    lines.append("LAYER WOOD_FRAME")
    col_r = D_c / 2.0
    half_w = W / 2.0
    for i in range(bays + 1):
        x = -half_w + i * spacing
        # 前檐柱
        lines.append(f"CIRCLE {x:.1f},{-depth/2:.1f},0 {col_r:.1f}")
        # 后檐柱
        lines.append(f"CIRCLE {x:.1f},{depth/2:.1f},0 {col_r:.1f}")
    lines.append("")

    # 台基轮廓
    lines.append("LAYER BASE")
    plinth_w = W + eave_f + eave_b + 600
    plinth_d = depth + eave_f + eave_b + 600
    lines.append(f"RECTANGLE -{plinth_w/2:.1f},{-plinth_d/2:.1f} {plinth_w/2:.1f},{plinth_d/2:.1f}")
    lines.append(f"RECTANGLE -{W/2:.1f},{-depth/2:.1f} {W/2:.1f},{depth/2:.1f}")
    lines.append("")

    # 屋面轮廓（歇山顶俯视简化）
    lines.append("LAYER ROOF")
    # 檐口投影（含出檐）
    roof_w = W + eave_f * 2
    roof_d = depth + eave_f * 2
    lines.append(f"RECTANGLE -{roof_w/2:.1f},{-roof_d/2:.1f} {roof_w/2:.1f},{roof_d/2:.1f}")
    # 正脊
    ridge_w = W * 0.6
    lines.append(f"LINE -{ridge_w/2:.1f},{depth/2+100:.1f} {ridge_w/2:.1f},{depth/2+100:.1f}")
    lines.append("")

    # 尺寸标注
    lines.append("LAYER DIM")
    lines.append(f"DIMLINEAR -{W/2:.1f},0,0 {W/2:.1f},0,0 0,-{depth/2+300:.0f}")
    lines.append(f"DIMLINEAR 0,{-depth/2:.1f},0 0,{depth/2:.1f},0 -{W/2+300:.0f},0")
    lines.append("")

    # 文字标注
    lines.append("LAYER ANNOTATION")
    lines.append(f"TEXT 0,{depth/2+200:.0f} 80 0 {p['name']}")
    lines.append(f"TEXT 0,{depth/2+120:.0f} 60 0 面阔{bays}间={W:.0f}mm  进深{depth_bays}架={depth:.0f}mm")
    lines.append(f"TEXT 0,{depth/2+60:.0f} 60 0 檐柱高={H_f:.0f}mm  后檐柱={H_b:.0f}mm  柱径={D_c:.0f}mm")
    lines.append(f"TEXT 0,{depth/2:.0f} 60 0 出檐前={eave_f:.0f}mm 后={eave_b:.0f}mm  举高={h_roof:.0f}mm")
    lines.append("")
    lines.append("ZOOM ALL")

    plan_scr = "\n".join(lines)

    # 剖面（沿当心间纵剖）
    sec = []
    sec.append(f"; 剖面: 沿当心间 YZ 剖切")
    sec.append("; 底层单位: mm")
    sec.append("")
    sec.append("_.ERASE All")
    sec.append("")
    for layer, color in [("AXIS", 1), ("BASE", 8), ("WOOD_FRAME", 3), ("ROOF", 5), ("DIM", 2), ("ANNOTATION", 7)]:
        sec.append(f"LAYER NEW {layer} COLOR {color} CONTINUOUS")
    sec.append("")

    # 地坪
    sec.append("LINE -3000,0,0 3000,0,0")
    sec.append("")

    # 台基
    sec.append("LAYER BASE")
    pw = W/2 + eave_f + 300
    sec.append(f"RECTANGLE -{pw:.1f},0 {pw:.1f},{H_p:.1f}")
    # 台阶
    step = H_p / 3.0
    for j in range(3):
        off = 150 * (3 - j)
        sec.append(f"RECTANGLE -{pw-off:.1f},{j*step:.1f} {pw-off:.1f},{(j+1)*step:.1f}")
    sec.append("")

    # 檐柱（当心间）
    sec.append("LAYER WOOD_FRAME")
    half_bay = spacing / 2.0
    sec.append(f"; 前檐柱  高={H_f:.0f}  径={D_c:.0f}")
    sec.append(f"RECTANGLE {-half_bay:.1f},{H_p:.1f} {half_bay:.1f},{H_p+H_f:.1f}")
    sec.append(f"; 后檐柱  高={H_b:.0f}（后方，Y轴偏移表示深度）")
    sec.append(f"RECTANGLE {-half_bay+50:.1f},{H_p:.1f} {half_bay+50:.1f},{H_p+H_b:.1f}")
    sec.append("")

    # 梁枋
    beam_h = D_c * 1.2
    sec.append("; 檐枋")
    sec.append(f"RECTANGLE {-half_bay-20:.1f},{H_p+H_f-beam_h/2:.1f} {half_bay+20:.1f},{H_p+H_f+beam_h/2:.1f}")
    sec.append("")

    # 歇山屋顶轮廓（简化为三角形+山花）
    sec.append("LAYER ROOF")
    ridge_z = H_p + H_f + beam_h + h_roof
    eave_z = H_p + H_f
    half_span = half_bay + eave_f
    sec.append(f"; 屋面: 檐口({half_span:.0f}, {eave_z:.0f}) → 正脊(0, {ridge_z:.0f})")
    sec.append(f"LINE -{half_span:.1f},{eave_z:.1f} 0,{ridge_z:.1f}")
    sec.append(f"LINE {half_span:.1f},{eave_z:.1f} 0,{ridge_z:.1f}")
    sec.append(f"; 正脊")
    sec.append(f"LINE -{D_c*2:.1f},{ridge_z:.1f} {D_c*2:.1f},{ridge_z:.1f}")
    sec.append(f"; 宝顶")
    fin_h = 300
    sec.append(f"CIRCLE 0,{ridge_z+fin_h/2:.1f} {D_c*0.5:.1f}")
    sec.append(f"LINE 0,{ridge_z:.1f} 0,{ridge_z+fin_h:.1f}")
    sec.append("")

    # 标注
    sec.append("LAYER DIM")
    sec.append(f"DIMLINEAR 0,{H_p:.1f} 0,{ridge_z+fin_h:.1f} {pw+300:.0f}")
    sec.append("")

    sec.append("LAYER ANNOTATION")
    sec.append(f"TEXT {pw+300:.0f},{H_p+100:.0f} 60 0 台基={H_p:.0f}mm")
    sec.append(f"TEXT {pw+300:.0f},{H_p+H_f+50:.0f} 60 0 前柱={H_f:.0f}mm")
    sec.append(f"TEXT {pw+300:.0f},{H_p+H_b:.0f} 60 0 后柱={H_b:.0f}mm")
    sec.append(f"TEXT {pw+300:.0f},{ridge_z+50:.0f} 60 0 总高={ridge_z+fin_h:.0f}mm")
    sec.append(f"TEXT 0,{ridge_z+fin_h+100:.0f} 70 0 {p['name']} 纵剖面")
    sec.append("")
    # ── full_detail 模式追加内容（剖面） ──
    if mode == "full_detail":
        sec.append("LAYER DOUGONG")
        sec.append(f"; 斗拱层  高≈{beam_h:.0f}mm（详图加强）")
        sec.append(f"RECTANGLE -{half_bay-10:.1f},{H_p+H_f-beam_h/2:.1f} {half_bay+10:.1f},{H_p+H_f+beam_h/2:.1f}")
        sec.append("LAYER RAIL")
        rail_h = H_p + H_f * 0.35
        sec.append(f"LINE -{half_bay:.1f},{rail_h:.1f} {half_bay:.1f},{rail_h:.1f}")
        sec.append("LAYER DECO")
        gable_z = ridge_z - h_roof * 0.25
        sec.append(f"LINE {-half_bay:.1f},{eave_z:.1f} 0,{gable_z:.1f}")
        sec.append(f"LINE {half_bay:.1f},{eave_z:.1f} 0,{gable_z:.1f}")
    sec.append("ZOOM ALL")

    return plan_scr, "\n".join(sec)



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
    
    return "\n".join(lines)


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
    
    return "\n".join(lines)


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
    
    return "\n".join(lines)


# ──────────────────────────────────────────────────
# ──────────────────────────────────────────────────
# 牌楼参数计算
# ──────────────────────────────────────────────────
def calc_paifang_params(W: float, bays: int = 3, style: str = "straight", is_wood: bool = False, double_eave: bool = False) -> dict:
    """计算牌楼各构件尺寸
    
    W: 总面阔 mm
    bays: 间数 1/3/5
    style: straight(屋盖式) / chongtian(冲天式)
    is_wood: True=木牌楼, False=石牌坊
    double_eave: True=双檐, False=单檐
    """
    K = W / 10.0
    
    if bays == 1:
        H_col = W * 0.75
        D_col = H_col * 0.10
        eave = W * 0.25
        h_roof = W * 0.55
        H_plinth = W * 0.12
        top_decor = W * 0.08
        depth = W * 0.50
    elif bays == 3:
        H_col = W * 0.55
        D_col = H_col * 0.10
        eave = W * 0.22
        h_roof = W * 0.60
        H_plinth = W * 0.10
        top_decor = W * 0.06
        depth = W * 0.20
    else:
        H_col = W * 0.50
        D_col = H_col * 0.10
        eave = W * 0.20
        h_roof = W * 0.65
        H_plinth = W * 0.10
        top_decor = W * 0.05
        depth = W * 0.18
    
    top_extra = H_col * 0.35 if style == "chongtian" else 0
    
    if is_wood and double_eave:
        H_col_upper = W * 0.60
        eave_upper = W * 0.18
        h_roof_upper = W * 0.45
    else:
        H_col_upper = H_col
        eave_upper = eave
        h_roof_upper = h_roof
    
    if bays >= 3:
        W_ming = W * 0.45
        W_ci = (W - W_ming) / 2
    else:
        W_ming = W
        W_ci = 0
    
    return dict(
        W=W, K=K, bays=bays, style=style,
        H_col=H_col, D_col=D_col, eave=eave,
        h_roof=h_roof, H_plinth=H_plinth,
        top_decor=top_decor, top_extra=top_extra,
        depth=depth,
        H_col_upper=H_col_upper, eave_upper=eave_upper, h_roof_upper=h_roof_upper,
        W_ming=W_ming, W_ci=W_ci,
        is_wood=is_wood, double_eave=double_eave
    )


# ──────────────────────────────────────────────────
# 牌楼 SCR 生成器
# ──────────────────────────────────────────────────
def gen_paifang_scr(p: dict, mode: str) -> tuple:
    """返回 (plan_scr, section_scr)"""
    W = p["W"]
    bays = p["bays"]
    n_cols = bays + 1
    D = p["D_col"]
    H = p["H_col"]
    H2 = p["H_col_upper"]
    e = p["eave"]
    e2 = p["eave_upper"]
    h_r = p["h_roof"]
    h_r2 = p["h_roof_upper"]
    H_p = p["H_plinth"]
    top_d = p["top_decor"]
    top_e = p["top_extra"]
    dep = p["depth"]
    W_m = p["W_ming"]
    W_c = p["W_ci"]
    style = p["style"]
    
    lines = []
    mat = "木" if p["is_wood"] else "石"
    lines.append(f"; {p.get('name','牌楼')} | {bays}间{mat}坊 {style} | {mode}")
    lines.append("; 底层单位: mm")
    lines.append("")
    lines.append("_.ERASE All")
    lines.append("")
    
    for lyr, clr, lt in [("AXIS",1,"CENTER"),("BASE",8,"CONTINUOUS"),("WOOD_FRAME",3,"CONTINUOUS"),
                          ("DOUGONG",6,"CONTINUOUS"),("ROOF",5,"CONTINUOUS"),("DECO",10,"CONTINUOUS"),
                          ("DIM",2,"CONTINUOUS"),("ANNOTATION",7,"CONTINUOUS")]:
        lines.append(f"LAYER NEW {lyr} COLOR {clr} {lt}")
    lines.append("")
    
    lines.append("LAYER AXIS")
    xl = W + e*2 + 2000
    yl = max(dep + 1000, 3000)
    lines.append(f"LINE -{xl:.0f},0,0 {xl:.0f},0,0")
    lines.append(f"LINE 0,-{yl:.0f},0 0,{yl:.0f},0")
    
    x_start = -W/2
    x_pos = []
    cx = x_start
    for i in range(n_cols):
        x_pos.append(cx)
        col_r = D / 2.0
        lines.append(f"CIRCLE {cx:.1f},{-dep/2:.1f},0 {col_r:.1f}")
        lines.append(f"CIRCLE {cx:.1f},{dep/2:.1f},0 {col_r:.1f}")
        if i == 0:
            cx += W_m
        elif i == 1 and bays >= 3:
            cx += W_c
        elif i == n_cols - 2 and bays >= 3:
            cx += W_c
        elif i == n_cols - 1:
            pass
        else:
            cx += W_c
    lines.append("")
    
    lines.append("LAYER BASE")
    pw = W + e*2 + 400
    pd = dep + 600
    lines.append(f"RECTANGLE -{pw/2:.1f},{-pd/2:.1f} {pw/2:.1f},{pd/2:.1f}")
    lines.append(f"RECTANGLE -{W/2:.1f},{-dep/2:.1f} {W/2:.1f},{dep/2:.1f}")
    lines.append("")
    
    lines.append("LAYER ROOF")
    rw = W + e*2
    rd = dep + e*0.5
    lines.append(f"RECTANGLE -{rw/2:.1f},{-rd/2:.1f} {rw/2:.1f},{rd/2:.1f}")
    ridge_w = W * 0.5
    lines.append(f"LINE -{ridge_w/2:.1f},{dep/2+50:.1f} {ridge_w/2:.1f},{dep/2+50:.1f}")
    lines.append("")
    
    lines.append("LAYER DECO")
    if bays == 1:
        lines.append(f"CIRCLE 0,{dep/2+50:.1f} {top_d/2:.1f}")
    else:
        for i in range(min(len(x_pos)-1, 5)):
            cx_seg = (x_pos[i] + x_pos[i+1]) / 2
            lines.append(f"CIRCLE {cx_seg:.1f},{dep/2+50:.1f} {top_d/3:.1f}")
    lines.append("")
    
    lines.append("LAYER DIM")
    lines.append(f"DIMLINEAR -{W/2:.1f},0,0 {W/2:.1f},0,0 0,-{dep/2+400:.0f}")
    if bays >= 3 and len(x_pos) >= 3:
        lines.append(f"DIMLINEAR {x_pos[0]:.1f},0,0 {x_pos[1]:.1f},0,0 -{dep/2+300:.0f}")
        lines.append(f"DIMLINEAR {x_pos[1]:.1f},0,0 {x_pos[2]:.1f},0,0 -{dep/2+200:.0f}")
    lines.append("")
    
    lines.append("LAYER ANNOTATION")
    total_h = H_p + H + e + h_r + top_d + top_e
    lines.append(f"TEXT 0,{dep/2+200:.0f} 80 0 {p['name']}")
    lines.append(f"TEXT 0,{dep/2+120:.0f} 60 0 面阔{W:.0f}mm {bays}间{mat}坊 {style}")
    lines.append(f"TEXT 0,{dep/2+60:.0f} 55 0 柱高={H:.0f}mm  柱径={D:.0f}mm  出檐={e:.0f}mm")
    lines.append(f"TEXT 0,{dep/2:.0f} 55 0 总高={total_h:.0f}mm  进深={dep:.0f}mm")
    lines.append("")
    lines.append("ZOOM ALL")
    plan_scr = "\n".join(lines)
    
    # Section
    sec = []
    sec.append(f"; 剖面: {p.get('name','牌楼')} 沿中线 YZ 剖切")
    sec.append("; 底层单位: mm")
    sec.append("")
    sec.append("_.ERASE All")
    sec.append("")
    for lyr, clr in [("AXIS",1),("BASE",8),("WOOD_FRAME",3),("DOUGONG",6),("ROOF",5),("DECO",10),("DIM",2),("ANNOTATION",7)]:
        sec.append(f"LAYER NEW {lyr} COLOR {clr} CONTINUOUS")
    sec.append("")
    
    sec.append("LINE -{:.0f},0,0 {:.0f},0,0".format(W+2000, W+2000))
    sec.append("")
    
    sec.append("LAYER BASE")
    pw2 = W/2 + e + 300
    sec.append(f"RECTANGLE -{pw2:.1f},0 {pw2:.1f},{H_p:.1f}")
    step = H_p / 3.0
    for j in range(3):
        off = 100 * (3-j)
        sec.append(f"RECTANGLE -{pw2-off:.1f},{j*step:.1f} {pw2-off:.1f},{(j+1)*step:.1f}")
    sec.append("")
    
    sec.append("LAYER WOOD_FRAME")
    sec.append(f"; 中柱  高={H:.0f}  径={D:.0f}")
    sec.append(f"RECTANGLE {-D/2:.1f},{H_p:.1f} {D/2:.1f},{H_p+H:.1f}")
    sec.append("")
    
    sec.append("LAYER DOUGONG")
    doug_h = D * 0.8
    sec.append(f"; 斗拱层  高≈{doug_h:.0f}mm")
    sec.append(f"RECTANGLE -{D/2+10:.1f},{H_p+H:.1f} {D/2+10:.1f},{H_p+H+doug_h:.1f}")
    sec.append("")
    
    sec.append("LAYER ROOF")
    eave1_z = H_p + H + doug_h
    sec.append(f"; 一层檐口  标高={eave1_z:.0f}mm")
    sec.append(f"LINE -{e:.1f},{eave1_z:.1f} {e:.1f},{eave1_z:.1f}")
    
    if p["double_eave"]:
        sec.append(f"; 二层檐口  标高={eave1_z+H2:.1f}mm")
        sec.append(f"LINE -{e2:.1f},{eave1_z+H2:.1f} {e2:.1f},{eave1_z+H2:.1f}")
        roof_top = eave1_z + H2 + doug_h + h_r2 + top_d
    else:
        roof_top = eave1_z + h_r + top_d
    
    sec.append(f"; 屋面: 檐口(±{e:.0f}, {eave1_z:.0f}) → 正脊(0, {roof_top:.0f})")
    sec.append(f"LINE -{e:.1f},{eave1_z:.1f} 0,{roof_top:.1f}")
    sec.append(f"LINE {e:.1f},{eave1_z:.1f} 0,{roof_top:.1f}")
    ridge_w2 = D * 3
    sec.append(f"LINE -{ridge_w2:.1f},{roof_top:.1f} {ridge_w2:.1f},{roof_top:.1f}")
    extra_note = f"  冲天柱高出屋面={top_e:.0f}mm" if top_e > 0 else ""
    sec.append(f"; 宝顶  高={top_d:.0f}mm{extra_note}")
    sec.append(f"CIRCLE 0,{roof_top+top_d/2:.1f} {top_d/3:.1f}")
    sec.append(f"LINE 0,{roof_top:.1f} 0,{roof_top+top_d:.1f}")
    if top_e > 0:
        sec.append(f"LINE 0,{roof_top+top_d:.1f} 0,{roof_top+top_d+top_e:.1f}")
    sec.append("")
    
    sec.append("LAYER DIM")
    sec.append(f"DIMLINEAR 0,{H_p:.1f} 0,{roof_top+top_d+top_e:.1f} {pw2+200:.0f}")
    sec.append("")
    
    sec.append("LAYER ANNOTATION")
    sec.append(f"TEXT {pw2+200:.0f},{H_p/2:.0f} 55 0 台基={H_p:.0f}mm")
    sec.append(f"TEXT {pw2+200:.0f},{H_p+H/2:.0f} 55 0 柱高={H:.0f}mm")
    sec.append(f"TEXT {pw2+200:.0f},{eave1_z+50:.0f} 55 0 檐高={eave1_z-H_p:.0f}mm")
    sec.append(f"TEXT {pw2+200:.0f},{roof_top+30:.0f} 55 0  roof={h_r:.0f}mm")
    sec.append(f"TEXT {pw2+200:.0f},{roof_top+top_d+50:.0f} 55 0  总高={int(roof_top+top_d+top_e)}mm")
    sec.append(f"TEXT 0,{roof_top+top_d+top_e+100:.0f} 70 0 {p['name']} 纵剖面")
    sec.append("")
    sec.append("ZOOM ALL")
    
    # ── full_detail 模式追加内容（剖面） ──
    if mode == "full_detail":
        sec.append("LAYER DOUGONG")
        sec.append(f"; 斗拱层  高≈{doug_h:.0f}mm（详图加强）")
        sec.append(f"RECTANGLE -{D/2+15:.1f},{H_p+H:.1f} {D/2+15:.1f},{H_p+H+doug_h:.1f}")
        sec.append("LAYER RAIL")
        rail_h = H_p + H * 0.30
        sec.append(f"LINE -{D*4:.1f},{rail_h:.1f} {D*4:.1f},{rail_h:.1f}")
        sec.append("LAYER DECO")
        plaque_h = H_p + H * 0.55
        plaque_w = D * 3
        sec.append(f"RECTANGLE -{plaque_w/2:.1f},{plaque_h:.1f} {plaque_w/2:.1f},{plaque_h+D:.1f}")
    sec.append("ZOOM ALL")

    return plan_scr, "\n".join(sec)


# ──────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="古建参数化 SCR 脚本生成器 V4.14")
    parser.add_argument("input", help="JSON 配置文件路径")
    parser.add_argument("--output", "-o", help="输出目录（默认同输入文件所在目录）")
    parser.add_argument("--mode", "-m", choices=["quick_shell", "full_detail"], default="quick_shell")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = json.load(f)

    # ── 输入范围校验 ──
    errors = []
    if "B" in cfg and cfg["B"] is not None:
        B = cfg["B"]
        if B < 1000:
            errors.append(f"B={B}mm 过小（最小 1000mm）")
        if B > 20000:
            errors.append(f"B={B}mm 过大（最大 20000mm）")
    if "bays_width" in cfg or "bay_spacing" in cfg:
        bays = cfg.get("bays_width", cfg.get("bays", 0))
        spacing = cfg.get("bay_spacing", 0)
        if isinstance(spacing, list):
            spacing = sum(spacing) / len(spacing) if spacing else 0
        if not (1 <= bays <= 13):
            errors.append(f"间数 bays={bays} 超出范围（1~13间）")
        if not (2000 <= spacing <= 6000):
            errors.append(f"开间 spacing={spacing}mm 超出范围（2000~6000mm）")
    if "W" in cfg and cfg["W"] is not None:
        W = cfg["W"]
        if W < 2000:
            errors.append(f"W={W}mm 过小（最小 2000mm）")
        if W > 30000:
            errors.append(f"W={W}mm 过大（最大 30000mm）")
        bays = cfg.get("bays", 3)
        if bays not in (1, 3, 5):
            errors.append(f"牌楼间数 bays={bays}，仅支持 1/3/5 间")
    if errors:
        print("[ERROR] 参数校验失败：")
        for e in errors:
            print(f"  - {e}")
        raise ValueError("; ".join(errors))

    # Validate required fields
    has_pavilion = "B" in cfg and cfg["B"] is not None
    has_paifang_w = "W" in cfg and cfg["W"] is not None
    has_hall = "bays_width" in cfg or "bay_spacing" in cfg
    has_corridor = cfg.get("category") == "廊" or "廊" in cfg.get("subtype", "")
    has_monument = cfg.get("category") == "坊" or "坊" in cfg.get("subtype", "")
    has_any = has_pavilion or has_paifang_w or has_hall or has_corridor or has_monument
    if not has_any:
        raise ValueError("JSON缺少必要字段：B或W(亭/坊), bays_width(殿/廊)。当前: " + str(list(cfg.keys())))

    name = cfg.get("name", cfg.get("id", "building"))
    cat = cfg.get("category", "")
    sid = cfg.get("subtype", "")

    out_dir = Path(args.output) if args.output else Path(args.input).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_path = out_dir / f"{name}_plan.scr"
    sec_path = out_dir / f"{name}_section.scr"
    elev_path = out_dir / f"{name}_elevation.scr"

    # 保存生成的 JSON（标准化）
    json_out = out_dir / f"{name}.json"
    cfg["mode"] = args.mode
    cfg["last_generate"] = "V4.14"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    if has_corridor:
        bays = cfg.get("bays_width", 3)
        spacing = cfg.get("bay_spacing", 3000)
        params = calc_hall_params(bays, spacing)
        params["name"] = name
        params["depth_bays"] = cfg.get("depth_bays", 1)
        params["is_corridor"] = True
        plan, section = gen_hall_scr(params, args.mode)
    elif has_monument:
        W = cfg.get("W", cfg.get("B", 3600))
        bays = cfg.get("bays", 1)
        style = cfg.get("column_style", "straight")
        is_wood = cfg.get("material", "stone") == "wood"
        double_eave = cfg.get("double_eave", False)
        params = calc_paifang_params(W, bays, style, is_wood, double_eave)
        params["name"] = name
        params["depth"] = cfg.get("depth", W * 0.2)
        plan, section = gen_paifang_scr(params, args.mode)
    elif cat == "亭" or "攒尖" in sid or "亭" in name:
        side = cfg.get("side_num", 6)
        B = cfg.get("B", 3000)
        params = calc_pavilion_params(B, side)
        params["name"] = name
        plan, section = gen_pavilion_scr(params, args.mode)
    elif cat == "殿" or "歇山" in sid or "庑殿" in sid or "殿" in name:
        bays = cfg.get("bays_width", cfg.get("bays", 5))
        spacing = cfg.get("bay_spacing", 3600)
        params = calc_hall_params(bays, spacing)
        params["name"] = name
        params["depth_bays"] = cfg.get("depth_bays", 3)
        plan, section = gen_hall_scr(params, args.mode)
    else:
        print(f"[WARN] 未识别建筑类型: category={cat}, subtype={sid}，尝试按亭类处理")
        side = cfg.get("side_num", 6)
        B = cfg.get("B", 3000)
        params = calc_pavilion_params(B, side)
        params["name"] = name
        plan, section = gen_pavilion_scr(params, args.mode)

    plan_path.write_text(plan, encoding="utf-8")
    sec_path.write_text(section, encoding="utf-8")
    
    # 生成立面图
    if has_corridor or cat == "廊" or "廊" in sid or "廊" in name:
        elev = gen_elevation_hall(params, args.mode)
    elif has_monument:
        elev = gen_elevation_paifang(params, args.mode)
    elif cat == "殿" or "歇山" in sid or "庱殿" in sid or "殿" in name:
        elev = gen_elevation_hall(params, args.mode)
    elif cat == "亭" or "攒尖" in sid or "亭" in name:
        elev = gen_elevation_pavilion(params, args.mode)
    else:
        elev = gen_elevation_pavilion(params, args.mode)
    elev_path.write_text(elev, encoding="utf-8")

    print(f"[OK] {name}")
    print(f"  平面图: {plan_path}")
    print(f"  剖面图: {sec_path}")
    print(f"  配置:  {json_out}")
    print(f"  模式:  {args.mode}")

if __name__ == "__main__":
    main()







