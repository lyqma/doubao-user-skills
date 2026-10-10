#!/usr/bin/env python3
"""
古建参数化 3D 渲染生成器 V5.0
读取 JSON 配置文件，使用 Blender 生成照片级 3D 渲染图。
支持亭/殿/牌楼三类建筑。
用法: python gen_3d.py <input.json> [--output <dir>] [--camera angle] [--render-mode studio|outdoor|dawn|night]
"""
import json
import math
import sys
from pathlib import Path

# ──────────────────────────────────────────────────
# Blender 内嵌脚本模板
# ──────────────────────────────────────────────────

BLENDER_PY_TEMPLATE = '''
import bpy
import math
import os

# ══════════════════════════════════════════════════
# 配置参数（由 gen_3d.py 注入）
# ══════════════════════════════════════════════════
CONFIG = {config_json}
OUTPUT_DIR = "{output_dir}"
RENDER_MODE = "{render_mode}"
CAMERA_ANGLE = {camera_angle}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════
# 场景初始化
# ══════════════════════════════════════════════════
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 删除默认光源
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj)

# 物理渲染引擎
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.film_transparent = False

# ══════════════════════════════════════════════════
# 材质库
# ══════════════════════════════════════════════════
def mat_white_marble(name="white_marble"):
    """汉白玉石材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.95, 0.94, 0.92, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Specular'].default_value = 0.1
    return m

def mat_grey_stone(name="grey_stone"):
    """青石材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.42, 0.42, 0.44, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    bsdf.inputs['Specular'].default_value = 0.05
    return m

def mat_red_lacquer(name="red_lacquer"):
    """朱红漆柱材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.55, 0.10, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Specular'].default_value = 0.4
    return m

def mat_natural_wood(name="natural_wood"):
    """原木色材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.48, 0.35, 0.22, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Specular'].default_value = 0.2
    return m

def mat_green_tile(name="green_tile"):
    """青瓦材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.15, 0.22, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    bsdf.inputs['Specular'].default_value = 0.1
    return m

def mat_imperial_yellow(name="imperial_yellow"):
    """琉璃黄材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Specular'].default_value = 0.6
    return m

def mat_gold_finial(name="gold_finial"):
    """金箔宝顶材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.20, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Specular'].default_value = 0.8
    bsdf.inputs['Metallic'].default_value = 0.9
    return m

def mat_ground(name="ground"):
    """地面材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.35, 0.40, 0.30, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    return m

def mat_ground_stone(name="ground_stone"):
    """石板地面材质"""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.55, 0.53, 0.50, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    return m

MATS = {
    "white_marble": mat_white_marble,
    "grey_stone": mat_grey_stone,
    "red_lacquer": mat_red_lacquer,
    "natural_wood": mat_natural_wood,
    "green_tile": mat_green_tile,
    "imperial_yellow": mat_imperial_yellow,
    "gold_finial": mat_gold_finial,
    "ground": mat_ground,
    "ground_stone": mat_ground_stone,
}

# ══════════════════════════════════════════════════
# 通用几何体创建
# ══════════════════════════════════════════════════
def add_cylinder(r, h, segs, mat, loc, name=""):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, segments=segs, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def add_cube(w, h, d, mat, loc, name=""):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.scale = (w/2, d/2, h/2)
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def add_poly_cylinder(sides, r, h, mat, loc, name=""):
    bpy.ops.mesh.primitive_circle_add(vertices=sides, radius=r, location=(0,0,0))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,h/2))
    # Merge using a simpler approach - use cylinder with segments
    bpy.ops.object.select_all(action='DESELECT')
    obj.data.select = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    return obj

def make_cone(base_r, top_r, h, segs, mat, loc, name=""):
    """创建圆锥台（用于屋面）"""
    bpy.ops.mesh.primitive_cone_add(radius1=base_r, radius2=top_r, depth=h, segments=segs, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

# ══════════════════════════════════════════════════
# 灯光系统
# ══════════════════════════════════════════════════
def setup_lighting(mode):
    """根据渲染模式设置灯光"""
    light_modes = {
        "studio": [
            {"type": "SUN", "energy": 3.0, "rot": (0.8, 0.5, 0.3), "name": "Key"},
            {"type": "SUN", "energy": 1.0, "rot": (-0.5, 0.3, 0.8), "name": "Fill"},
            {"type": "SUN", "energy": 0.5, "rot": (0.0, -1.0, 0.5), "name": "Rim"},
        ],
        "outdoor": [
            {"type": "SUN", "energy": 5.0, "rot": (0.6, 0.4, 0.2), "name": "Sun"},
            {"type": "HEMI", "energy": 1.5, "rot": (0.0, 0.0, 1.0), "name": "Ambient"},
        ],
        "dawn": [
            {"type": "SUN", "energy": 2.0, "rot": (0.9, 0.1, 0.1), "name": "Dawn"},
            {"type": "POINT", "energy": 0.8, "loc": (0, 0, 5), "name": "Fill"},
        ],
        "night": [
            {"type": "SUN", "energy": 0.3, "rot": (-0.5, 0.3, 0.8), "name": "Moon"},
            {"type": "POINT", "energy": 2.0, "loc": (0, 0, 3), "name": "Lantern"},
            {"type": "POINT", "energy": 1.0, "loc": (5, 0, 2), "name": "Lantern2"},
        ],
    }
    lights = light_modes.get(mode, light_modes["studio"])
    for l in lights:
        bpy.ops.object.light_add(type=l["type"], location=(0, 0, 10))
        obj = bpy.context.active_object
        obj.name = l["name"]
        obj.data.energy = l["energy"]
        if "rot" in l:
            obj.rotation_euler = (l["rot"][0], l["rot"][1], l["rot"][2])
        if "loc" in l:
            obj.location = l["loc"]

def setup_environment(mode):
    """设置环境背景"""
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    
    env_modes = {
        "studio": ((0.15, 0.15, 0.18, 1.0), 0.0),
        "outdoor": ((0.55, 0.65, 0.80, 1.0), 1.0),
        "dawn": ((0.85, 0.55, 0.35, 1.0), 0.5),
        "night": ((0.02, 0.02, 0.05, 1.0), 0.0),
    }
    color, use_world = env_modes.get(mode, env_modes["outdoor"])
    bg.inputs["Color"].default_value = color
    bg.inputs["Strength"].default_value = 1.0 if use_world else 0.0

# ══════════════════════════════════════════════════
# 相机设置
# ══════════════════════════════════════════════════
def setup_camera(dist, angle_deg, height=2.0):
    cam = bpy.data.cameras.new("ArchCamera")
    cam.angle = math.radians(35)
    cam.lens_unit = 'DEGREES'
    cam.shift_x = 0.0
    cam.shift_y = 0.0
    
    cam_obj = bpy.data.objects.new("Camera", cam)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    rad = math.radians(angle_deg)
    x = dist * math.cos(rad)
    y = dist * math.sin(rad)
    cam_obj.location = (x, y, height)
    cam_obj.look_at_target((0, 0, 0))
    return cam_obj

# ══════════════════════════════════════════════════
# 亭类生成器
# ══════════════════════════════════════════════════
def build_pavilion(cfg, mats):
    B = cfg["B"]
    n = cfg.get("side_num", 6)
    scale = B / 3000.0  # 标准化缩放
    
    H_col = B * 0.75
    D_col = H_col * 0.085
    eave = B * (0.32 if n == 6 else 0.30)
    h_roof = B * (0.40 if n == 6 else 0.38)
    H_plinth = max(B * 0.133, 400)
    R_col = B / 2.0 if n == 6 else B / 2.613
    
    # 材质
    m_marble = mats["white_marble"]
    m_wood = mats["red_lacquer"]
    m_tile = mats["green_tile"]
    m_gold = mats["gold_finial"]
    
    angle_step = 2 * math.pi / n
    
    # 台基（多层台阶）
    for tier in range(3):
        h = H_plinth / 3
        z = tier * h + h / 2
        r = R_col * 1.2 + (2 - tier) * 150 * scale
        add_poly_cylinder(n, r, h, m_marble, (0, 0, z), f"plinth_tier{tier}")
    
    # 檐柱
    col_r = D_col / 2
    for i in range(n):
        ang = i * angle_step
        x = R_col * math.cos(ang)
        y = R_col * math.sin(ang)
        add_cylinder(col_r, H_col, 12, m_wood, (x, y, H_plinth + H_col/2), f"col_{i:02d}")
    
    # 斗拱层（柱顶垫块）
    doug_h = D_col * 0.3
    for i in range(n):
        ang = i * angle_step
        x = R_col * math.cos(ang)
        y = R_col * math.sin(ang)
        add_cube(D_col * 1.2, doug_h, D_col * 1.2, m_wood, 
                 (x, y, H_plinth + H_col + doug_h/2), f"doug_{i:02d}")
    
    # 屋面（攒尖锥体）
    roof_base_r = R_col + eave
    roof_top_r = D_col * 0.3
    roof_z = H_plinth + H_col + doug_h + h_roof / 2
    make_cone(roof_base_r, roof_top_r, h_roof, n + 2, m_tile, (0, 0, roof_z))
    
    # 宝顶
    finial_h = 300 * scale
    finial_r = D_col * 0.4
    add_cylinder(finial_r, finial_h, 8, m_gold, (0, 0, roof_z + h_roof/2 + finial_h/2), "finial")
    
    # 栏杆（美人靠）
    rail_h = H_col * 0.40
    rail_r = R_col - D_col/2 - 30 * scale
    if rail_r > 50:
        # 栏杆圆环
        bpy.ops.mesh.primitive_torus_add(major_radius=rail_r, minor_radius=15*scale, 
                                          location=(0, 0, H_plinth + rail_h),
                                          rotation=(math.pi/2, 0, 0))
        torus = bpy.context.active_object
        torus.name = "railing"
        torus.data.materials.append(m_wood)
        # 栏杆立柱
        for i in range(n):
            ang = (i + 0.5) * angle_step
            rx = rail_r * math.cos(ang)
            ry = rail_r * math.sin(ang)
            add_cylinder(8*scale, rail_h, 8, m_wood, (rx, ry, H_plinth + rail_h/2), f"rail_post_{i}")
    
    # 地面
    ground_r = B * 2
    bpy.ops.mesh.primitive_circle_add(radius=ground_r, location=(0, 0, -0.1))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.5))
    ground = bpy.context.active_object
    ground.data.materials.append(mats["ground_stone"])
    ground.name = "ground"
    
    return B * 3  # 返回大致尺寸用于相机距离

# ══════════════════════════════════════════════════
# 殿类生成器
# ══════════════════════════════════════════════════
def build_hall(cfg, mats):
    bays = cfg.get("bays_width", 5)
    spacing = cfg.get("bay_spacing", 3600)
    W = bays * spacing
    depth_bays = cfg.get("depth_bays", 3)
    depth = depth_bays * spacing
    scale = W / 18000.0
    
    H_f = W * 0.58
    H_b = W * 0.52
    D_col = H_f * 0.10
    eave_f = W * 0.28
    eave_b = W * 0.18
    h_roof = W * 0.55
    H_plinth = W * 0.10
    col_r = D_col / 2
    
    m_marble = mats["white_marble"]
    m_wood = mats["red_lacquer"]
    m_tile = m_tile = mats["green_tile"]
    m_gold = mats["gold_finial"]
    
    half_w = W / 2
    half_d = depth / 2
    
    # 台基
    plinth_h = H_plinth
    plinth_w = W + eave_f + eave_b + 600
    plinth_d = depth + eave_f + eave_b + 600
    add_cube(plinth_w, plinth_h, plinth_d, m_marble, (0, 0, plinth_h/2), "plinth")
    
    # 台阶（正面）
    step_h = plinth_h / 3
    step_w = W + 400
    for j in range(3):
        add_cube(step_w, step_h, 300, m_marble, 
                 (0, half_d + 300*(j+1) + 150, step_h*(j+1)/2), f"step_{j}")
    
    # 柱网
    for bay in range(bays + 1):
        x = -half_w + bay * spacing
        # 前檐柱
        add_cylinder(col_r, H_f, 12, m_wood, (x, -half_d, H_f/2 + plinth_h), f"fcol_{bay}")
        # 后檐柱
        add_cylinder(col_r, H_b, 12, m_wood, (x, half_d, H_b/2 + plinth_h), f"bcol_{bay}")
    
    # 斗拱层
    doug_h = D_col * 0.3
    for bay in range(bays + 1):
        x = -half_w + bay * spacing
        add_cube(D_col*1.3, doug_h, D_col*1.3, m_wood,
                 (x, -half_d, plinth_h + H_f + doug_h/2), f"fdoug_{bay}")
        add_cube(D_col*1.3, doug_h, D_col*1.3, m_wood,
                 (x, half_d, plinth_h + H_b + doug_h/2), f"bdoug_{bay}")
    
    # 歇山屋顶
    roof_z = plinth_h + H_f + doug_h
    # 主屋顶（四面坡）
    roof_h = h_roof
    add_cube(W + eave_f*2, roof_h*0.15, depth + eave_f*2, m_tile,
             (0, 0, roof_z + roof_h/2), "roof_main")
    # 屋顶脊线（三角形屋脊面）
    ridge_w = W * 0.5
    ridge_h = roof_h * 0.8
    # 前后坡面
    for side in [-1, 1]:
        z_mid = roof_z + roof_h * 0.5
        add_cube(ridge_w, ridge_h, 50, m_tile,
                 (0, side * (depth/2 + eave_f/2), z_mid), f"roof_slope_{side}")
    # 正脊
    add_cube(ridge_w, D_col, D_col*2, m_tile,
             (0, 0, roof_z + roof_h), "ridge")
    
    # 宝顶
    fin_h = 400 * scale
    fin_r = D_col * 0.5
    add_cylinder(fin_r, fin_h, 8, m_gold, (0, 0, roof_z + roof_h + fin_h/2), "finial")
    
    # 地面
    g_r = max(W, depth) * 1.5
    bpy.ops.mesh.primitive_circle_add(radius=g_r, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.data.materials.append(mats["ground_stone"])
    ground.name = "ground"
    
    return max(W, depth) * 1.5

# ══════════════════════════════════════════════════
# 牌楼生成器
# ══════════════════════════════════════════════════
def build_paifang(cfg, mats):
    W = cfg["W"]
    bays = cfg["bays"]
    n_cols = bays + 1
    style = cfg.get("column_style", "straight")
    is_wood = cfg.get("material", "stone") == "wood"
    double_eave = cfg.get("double_eave", False)
    
    scale = W / 10800.0
    
    H_col = W * (0.55 if bays >= 3 else 0.75)
    D_col = H_col * 0.10
    eave = W * (0.22 if bays >= 3 else 0.25)
    h_roof = W * (0.60 if bays >= 3 else 0.55)
    H_plinth = W * 0.10
    top_decor = W * 0.06
    depth = cfg.get("depth", W * 0.20)
    
    # 材质选择
    m_stone = mats["grey_stone"] if not is_wood else mats["natural_wood"]
    m_wood_col = mats["red_lacquer"] if is_wood else m_stone
    m_tile = mats["green_tile"]
    m_gold = mats["gold_finial"]
    m_marble = mats["white_marble"]
    
    # 柱位分布
    if bays == 1:
        col_xs = [-W/2, W/2]
    elif bays == 3:
        W_ming = W * 0.45
        W_ci = (W - W_ming) / 2
        col_xs = [-W/2, -W_ming/2, W_ming/2, W/2]
    else:
        col_xs = []
        seg = W / (n_cols - 1)
        for i in range(n_cols):
            col_xs.append(-W/2 + i * seg)
    
    col_r = D_col / 2
    
    # 台基
    pw = W + eave*2 + 400
    pd = depth + 600
    add_cube(pw, H_plinth, pd, m_marble, (0, 0, H_plinth/2), "plinth")
    
    # 台阶
    for j in range(3):
        step_w = pw - j*100
        step_h = H_plinth / 3
        add_cube(step_w, step_h, 300, m_marble,
                 (0, pd/2 + 150 + j*100, step_h*(j+1)/2), f"pf_step_{j}")
    
    # 柱子
    for i, cx in enumerate(col_xs):
        add_cylinder(col_r, H_col, 12, m_wood_col, (cx, 0, H_col/2 + H_plinth), f"col_{i}")
    
    # 斗拱层
    doug_h = D_col * 0.35
    for i, cx in enumerate(col_xs):
        add_cube(D_col*1.2, doug_h, D_col*1.2, m_wood_col,
                 (cx, 0, H_col + H_plinth + doug_h/2), f"doug_{i}")
    
    # 一层檐口
    eave1_z = H_col + H_plinth + doug_h
    # 檐檩（横向梁）
    add_cube(W + eave*2, D_col*0.5, D_col*0.5, m_wood_col,
             (0, 0, eave1_z + D_col*0.25), "beam_1")
    
    # 二层（双檐木牌楼）
    if double_eave:
        H2 = W * 0.60
        eave2 = W * 0.18
        add_cylinder(col_r, H2, 12, m_wood_col, 
                     (col_xs[1] if len(col_xs) > 1 else 0, 0, eave1_z + H2/2 + doug_h), "col_upper")
        add_cube(W*0.6, D_col*0.4, D_col*0.4, m_wood_col,
                 (0, 0, eave1_z + H2 + doug_h), "beam_2")
        roof2_z = eave1_z + H2 + doug_h
        make_cone(W/2 + eave2, D_col*0.2, W*0.45, 8, m_tile, 
                  (0, 0, roof2_z + W*0.45/2), "roof_2")
    else:
        roof2_z = eave1_z
    
    # 主屋顶（歇山式简化）
    roof_top = roof2_z + h_roof
    make_cone(W/2 + eave, D_col*0.15, h_roof, n_cols + 2, m_tile,
              (0, 0, roof2_z + h_roof/2), "roof_main")
    
    # 正脊
    ridge_w = W * 0.4
    add_cube(ridge_w, D_col*0.8, D_col*1.5, m_tile,
             (0, 0, roof_top), "ridge")
    
    # 宝顶
    fin_h = top_decor
    fin_r = D_col * 0.4
    add_cylinder(fin_r, fin_h, 8, m_gold, (0, 0, roof_top + fin_h/2), "finial")
    
    # 冲天柱
    if style == "chongtian":
        top_extra = H_col * 0.35
        for cx in col_xs:
            add_cylinder(col_r*0.8, top_extra, 8, m_wood_col,
                         (cx, 0, H_col + H_plinth + h_roof + top_extra/2), f"chongtian_{cx}")
    
    # 匾额
    plaque_h = H_col * 0.5
    plaque_w = W * 0.3
    add_cube(plaque_w, plaque_h, D_col*0.3, mats["imperial_yellow"],
             (0, 0, H_plinth + H_col*0.55), "plaque")
    
    # 地面
    g_r = W * 1.2
    bpy.ops.mesh.primitive_circle_add(radius=g_r, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.data.materials.append(mats["ground_stone"])
    ground.name = "ground"
    
    return W * 1.2

# ══════════════════════════════════════════════════
# 主程序
# ══════════════════════════════════════════════════
print(f"Building: {CONFIG.get('name', 'building')}")
print(f"Mode: {RENDER_MODE}, Camera angle: {CAMERA_ANGLE}")

mats = {name: func() for name, func in MATS.items()}

cfg_type = CONFIG.get("category", "")
name = CONFIG.get("name", "building")

if cfg_type == "坊" or "坊" in str(CONFIG.get("subtype", "")):
    size = build_paifang(CONFIG, mats)
elif cfg_type == "殿" or "殿" in str(CONFIG.get("subtype", "")):
    size = build_hall(CONFIG, mats)
else:
    size = build_pavilion(CONFIG, mats)

# 灯光和环境
setup_lighting(RENDER_MODE)
setup_environment(RENDER_MODE)

# 相机
cam_dist = size * 1.5
setup_camera(cam_dist, CAMERA_ANGLE)

# 渲染输出
bpy.context.scene.render.image_format = 'PNG'
bpy.context.scene.render.film_transparent = False
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, f"{name.replace(chr(32), '_')}_render.png")

print(f"Rendering to: {bpy.context.scene.render.filepath}")
bpy.ops.render.render(write_still=True)
print("Done!")
'''

def main():
    import argparse
    parser = argparse.ArgumentParser(description="古建参数化 3D 渲染生成器 V5.0")
    parser.add_argument("input", help="JSON 配置文件路径")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--camera", "-c", type=float, default=30, help="相机角度（度，0=正面）")
    parser.add_argument("--render-mode", "-m", choices=["studio", "outdoor", "dawn", "night"], default="outdoor")
    parser.add_argument("--resolve", "-r", action="store_true", help="直接调用 blender -b 渲染")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = json.load(f)

    name = cfg.get("name", cfg.get("id", "building"))
    out_dir = Path(args.output) if args.output else Path(args.input).parent / "renders_3d"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 替换模板中的变量
    config_json = json.dumps(cfg, ensure_ascii=False)
    script_content = BLENDER_PY_TEMPLATE.format(
        config_json=config_json,
        output_dir=str(out_dir),
        render_mode=args.render_mode,
        camera_angle=args.camera,
    )

    script_path = out_dir / f"gen_{name}.py"
    script_path.write_text(script_content, encoding="utf-8")
    print(f"[OK] Blender 脚本: {script_path}")

    if args.resolve:
        import subprocess
        r = subprocess.run(
            ["blender", "-b", "--python", str(script_path)],
            capture_output=True, text=True
        )
        print(r.stdout[-500:] if r.stdout else "")
        print(r.stderr[-500:] if r.stderr else "")
    else:
        print(f"\n使用方法:")
        print(f"  blender -b --python \"{script_path}\"")
        print(f"\n或等待 Blender 脚本就绪后手动运行")

if __name__ == "__main__":
    main()
