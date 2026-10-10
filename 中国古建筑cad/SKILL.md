---
name: 中国古建筑CAD
version: "4.12"
description: >-
  中国传统古建筑 AutoCAD 参数化出图技能。
  根据建筑类型和尺寸参数，自动生成 .scr 绘图脚本（平面/剖面/立面）
  以及对应的 Blender 3D 模型脚本。
  支持亭、殿、廊、坊四大类，清式比例体系。
  当用户需要古建CAD图纸、参数化出图、或说"画个六角亭/八角亭/歇山殿"时激活。
user-invocable: true
tags:
  - auto-cad
  - chinese-architecture
  - parametric-drawing
  - traditional-buildings
  - gubuilding
metadata:
  openclaw:
    emoji: "🏯"
    requires:
      bins:
        - python
        - auto-cad-or-zwcad
---

# 古建参数化 CAD 技能 V4.12

## 核心职责

读取或生成符合 **清式营造则例** 参数的古建筑 AutoCAD 脚本（`.scr`），
并可选同步生成 Blender 3D 模型脚本。

底层单位：**毫米（mm）**，所有坐标、尺寸直接以 mm 输出。

---

## 输入识别

用户请求分三种情况，按优先级处理：

### 情况A：提供 JSON 配置文件
- 用户说"用这个配置画图"或提供 `*.json` 文件路径
- **直接读取** JSON，解析 `modulus_rules.formulas` 和 `components`，生成 `.scr`

### 情况B：文字描述建筑需求
- 用户说"画个六角亭，对边距3米"或"要一个歇山殿，面阔五间"
- **先查** `rreferences/building_types.md` 确定建筑类型和公式
- **再查** `rreferences/geometry_formulas.md` 计算各构件尺寸
- **最后生成** `.scr` 脚本写入目标目录

### 情况C：从零新建建筑类型
- 用户要创建一种全新的古建类型
- 先读取 `schema.json` 确认字段规范
- 参照现有 `examples/*.json` 模板生成新 JSON
- 再生成对应的 `.scr` 和 `.py`

---

## 生成清单（默认全部输出）

| 输出文件 | 用途 | 必须 |
|---------|------|-----|
| `{name}_plan.scr` | 平面图（俯视） | ✅ |
| `{name}_section.scr` | 剖面图（关键剖面） | ✅ |
| `building.json` | 参数数据集（供重新生成） | ✅ |
| `generate_blender.py` | 3D 模型脚本 | 可选 |

---

## SCR 脚本规范

### 图层顺序（严格按此顺序创建）

```
AXIS       — 定位轴线（红色，CENTER 线型）
BASE       — 台基轮廓（白色/灰）
WOOD_FRAME — 柱网梁枋（绿色）
DOUGONG    — 斗拱层（青莲，仅 full_detail 模式）
ROOF       — 屋面轮廓（青色）
RAIL       — 栏杆美人靠（蓝色）
DIM        — 尺寸标注（白色）
ANNOTATION — 文字说明（白色）
```

### 常用命令白名单

仅使用以下 AutoCAD 原生命令，保证 `.scr` 兼容性：

```
LAYER, LINE, CIRCLE, POLYGON, OFFSET, ARRAY, DIMLINEAR, DIMALIGNED,
TEXT, MTEXT, RECTANGLE, ARC, SPLINE, COPY, MOVE, ROTATE, SCALE,
TRIM, EXTEND, JOIN, UNION, SUBTRACT, INTERSECT
```

### 坐标系统

- 原点在建筑中心
- X 轴沿面阔方向（长方向）
- Y 轴沿进深方向（短方向）
- Z 轴向上（标高方向）
- 所有坐标为绝对坐标，不使用相对坐标（`@`）

---

## 平面图生成逻辑

### 六角亭平面图（quick_shell）

```
1. 画出两条中心轴线（交叉于原点）
2. 画柱定位圆：半径 = B/2，圆心原点
3. 画六角台基外轮廓：正六边形，外接圆半径 = B×1.2
4. 在柱定位圆上标出6个柱位点（角度：0°, 60°, 120°, 180°, 240°, 300°）
5. 每柱位画直径圆圈（D_column）
6. 连接相邻柱位点，标注檐枋位置
7. 画外围尺寸标注（B 对边距）
8. 写文字标注：建筑名称 + 主要参数
```

### 八角亭平面图（quick_shell）

与六角亭相同逻辑，柱数=8，角度步长=45°，定位圆半径=B/2.613。

### 单檐歇山殿平面图（quick_shell）

```
1. 画出定位轴线网格（面阔方向 X，进深方向 Y）
2. 确定柱网：面阔 N 间 × 进深 M 架
3. 画外轮廓矩形（台基外边线）
4. 标出檐柱位置（圆）
5. 标出金柱位置（圆，直径略大于檐柱）
6. 画当心间（正间）突出标注
7. 标注各间面阔尺寸
8. 写文字：面阔 N 间，进深 M 架，总面阔=XXXXmm
```

---

## 剖面图生成逻辑

### 攒尖顶亭剖面（沿对角线切）

```
1. 画水平基准线（地坪 ±0.000）
2. 画出台基台阶轮廓（梯形，每阶高 H_plinth/3，出挑 200mm）
3. 画檐柱（矩形，高 H_column，宽 D_column）
4. 画檐枋（矩形，高 D_column，宽 D_column×0.7）
5. 画屋面三角形/锥形轮廓（底宽 = B/2 + eave，高 = H_column + D_column + roof_rise）
6. 画宝顶（小圆柱，高约 300mm）
7. 标注各层高度
```

### 歇山殿剖面（沿面阔当心间切）

```
1. 画台基（矩形，高 H_plinth）
2. 画前檐柱和后檐柱（高度略有差异）
3. 画梁架系统：檐枋→金枋→脊枋（逐层升高）
4. 画歇山顶剖面轮廓（九条脊线：正脊+四条垂脊+四条戗脊的投影）
5. 标注举高：正脊至檐口垂直距离 = h_roof
```

---

## 参数计算规则

### 亭类（六角/八角）

所有尺寸从 **B（对边距）** 推导，见 `rreferences/geometry_formulas.md` 第一节。

关键公式：
```
柱高 H_col  = B × 0.75
柱径 D_col  = H_col × 0.085
出檐 eave   = B × 0.32
 roof 高    = B × 0.40
台基高      = B × 0.133（或常值 400mm，取较大者）
```

### 殿类（歇山/庑殿）

所有尺寸从 **总面阔 W（mm）** 推导（K = W / 10 仅作中间参考）。

关键公式：
```
檐柱高(前) = W × 0.58
檐柱高(后) = W × 0.52
檐柱径     = 檐柱高 × 0.10
前出檐     = W × 0.28
后出檐     = W × 0.18
屋面举高   = W × 0.55
台基高     = W × 0.10
```

> 例：面阔五间（每间3600mm），W=18000mm → 前柱高10440mm、柱径1044mm、总高约23.7m

### 用户输入换算

用户可能输入：
- **米**：乘以 1000 转为 mm
- **清斗口**：直接作为 K 值（单位 mm）
- **营造尺**：1 营造尺 ≈ 320mm

在生成脚本前，先确认输入单位并换算。

---

## 快速模板命令（常用建筑一键生成）

将以下 JSON 模板存入 `assets/templates/`，用户说"画六角亭B3000"时直接实例化：

**六角亭模板** (`assets/templates/pavilion_hex_3m.json`):
```json
{
  "id": "pavilion_hex_3m",
  "name": "清式六角攒尖亭 B=3000mm",
  "B": 3000,
  "side_num": 6
}
```

**八角亭模板** (`assets/templates/pavilion_oct_3.6m.json`):
```json
{
  "id": "pavilion_oct_3.6m",
  "name": "清式八角攒尖亭 B=3600mm",
  "B": 3600,
  "side_num": 8
}
```

**歇山殿模板** (`assets/templates/hall_xieshan_5bay.json`):
```json
{
  "id": "hall_xieshan_5bay",
  "name": "清式单檐歇山殿 面阔五间",
  "category": "殿",
  "subtype": "单檐歇山",
  "bays_width": 5,
  "bay_spacing": 3600,
  "depth_bays": 3
}
```

**牌楼模板** (`assets/templates/paifang_*.json`)：

| 模板 | 名称 | W(面阔) | bays | style | material |
|------|------|---------|------|-------|----------|
| `paifang_1bay_stone.json` | 单间石牌坊 | 3600mm | 1 | straight | stone |
| `paifang_3bay_stone.json` | 三间石牌坊 | 10800mm | 3 | straight | stone |
| `paifang_3bay_chongtian.json` | 四柱三间冲天牌楼 | 12000mm | 3 | chongtian | stone |
| `paifang_3bay_wood.json` | 三间木牌楼 | 9000mm | 3 | straight | wood |

```json
{
  "id": "paifang_3bay_stone",
  "name": "清式三间石牌坊",
  "category": "坊",
  "subtype": "三间石牌楼",
  "W": 10800,
  "bays": 3,
  "bay_spacing": [3600,3600,3600],
  "depth": 2400,
  "column_style": "straight",
  "roof_type": "xieshan",
  "material": "stone"
}
```

**牌楼字段说明**：
- `W`：总面阔 mm（必填）
- `bays`：间数 1/3/5（必填）
- `column_style`：`straight`(屋盖式) / `chongtian`(冲天式)
- `material`：`stone`(石) / `wood`(木)
- `double_eave`：true=双檐（木牌楼专用）
- `depth`：进深 mm（可选，默认 W×0.2）
```json
{
  "id": "hall_xieshan_5bay",
  "name": "清式单檐歇山殿 面阔五间",
  "bays_width": 5,
  "bay_spacing": 3600,
  "depth_bays": 3
}
```

---

## 输出文件写入位置

- 默认写到用户指定的项目目录
- 如果用户没有指定，写到当前工作目录下的 `古建CAD输出/` 子目录
- 文件名格式：`{建筑名}_{参数}_plan.scr` 和 `{建筑名}_{参数}_section.scr`

---

## 错误处理

1. **B 值超出约束**：自动触发 fallback，使用 `fallback.default_params`，并在注释中注明
2. **JSON 校验失败**：对照 `schema.json` 报错，指出缺失字段
3. **用户输入无单位**：默认按毫米处理，并在脚本头注释中注明
4. **生成失败**：输出 `.scr` 文件内容到控制台，便于用户手动复制

---

## 参考文档索引

- `rreferences/geometry_formulas.md` — 清式比例公式全集（亭/殿/廊/坊）
- `rreferences/building_types.md` — 传统古建类型速查 + 图层命名规范
- `schema.json` — 数据集字段定义（新建建筑类型时必读）
- `template_lib.json` — 可用构件原子模板列表

---

## CAD 命令速查

- 
references/cad_commands.md — AutoCAD SCR命令全集（绘图/修改/图层/标注/坐标计算）
- 
references/drawing_standards.md — 制图规范（图层/比例/线宽/标注/图框）
- 
references/cad_layer_standards.md — 图层颜色与线型速查

## 批量出图

`ash
# 批量生成目录下所有JSON配置
python scripts/batch_gen.py 古建参数化_V4.12/assets/templates/ --output ./全部图纸

# 跳过已生成文件
python scripts/batch_gen.py ./config_dir/ --skip-existing
`

## SCR 脚本使用步骤

`
1. 生成 .scr 文件（自动生成 plan + section）
2. 打开 AutoCAD / 中望CAD
3. 命令行输入: SCRIPT
4. 选择生成的 .scr 文件
5. 图纸自动绘制完成，ZOOM ALL 适应视图
`

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| CENTER线型显示为实线 | 线型未加载 | CAD中执行 LOAD 命令加载 CENTER 线型 |
| 中文显示乱码 | 字体缺失 | 使用 SHX 简宋体或设置系统中文环境 |
| 尺寸标注位置不对 | 标注偏移量方向错误 | 偏移量负值在下方/左方，正值在上方/右方 |
| 图形超出视图 | ZOOM ALL 未执行 | 脚本末尾已包含 ZOOM ALL，无需额外操作 |
| POLYGON命令报错 | 版本兼容 | 使用 _.POLYGON 前缀（已有下划线）避免本地化问题 |

---

## 大师级命令参考

- 
references/cad_commands.md — AutoCAD SCR命令全集（绘图/修改/图层/标注）
- 
references/cad_master_commands.md — 大师级命令全集（3D建模/布局打印/图块属性/参数化约束/快速选择）
- 
references/drawing_standards.md — 制图规范（图层/比例/线宽/标注/图框）
- 
references/cad_layer_standards.md — 图层颜色与线型速查
---

## CAD-MCP 直接控制（实时绘图）

当 AutoCAD 已打开时，通过 CAD-MCP 直接发送绘图命令，无需先生成 .scr 文件。

### 前置检查

```
1. 确认 AutoCAD 正在运行：Get-Process acad
2. 确认 CAD-MCP 服务可用
3. 当前打开的图纸：list_entities 查看现有内容
```

### 快速绘图命令序列

#### 创建图层

```python
# 按顺序创建所有图层
create_layer(name="AXIS", color=1, linetype="CENTER")
create_layer(name="BASE", color=8, linetype="CONTINUOUS")
create_layer(name="WOOD_FRAME", color=3, linetype="CONTINUOUS")
create_layer(name="DOUGONG", color=6, linetype="CONTINUOUS")
create_layer(name="ROOF", color=5, linetype="CONTINUOUS")
create_layer(name="RAIL", color=4, linetype="CONTINUOUS")
create_layer(name="DIM", color=2, linetype="CONTINUOUS")
create_layer(name="ANNOTATION", color=7, linetype="CONTINUOUS")
```

#### 六角亭完整绘图流程（B=3000mm）

```python
# 1. 清空当前图纸
send_command("_.ERASE All")

# 2. 画中心轴线
set_current_layer("AXIS")
draw_line(0, 0, 15000, 0)       # X轴
draw_line(0, 0, 0, 15000)       # Y轴

# 3. 画六角台基（外接圆半径=3600mm）
set_current_layer("BASE")
pts = [(3600,0), (1800,3118), (-1800,3118), (-3600,0), (-1800,-3118), (1800,-3118)]
draw_polyline(pts, close=True)

# 4. 画柱定位圆（R=1500mm）
set_current_layer("WOOD_FRAME")
draw_circle(0, 0, 1500)

# 5. 画6根檐柱（柱径191mm）
import math
for angle_deg in [0, 60, 120, 180, 240, 300]:
    rad = math.radians(angle_deg)
    cx = 1500 * math.cos(rad)
    cy = 1500 * math.sin(rad)
    draw_circle(cx, cy, 95.6)

# 6. 画檐枋连线（相邻柱位）
for i in range(6):
    a1 = math.radians(i * 60)
    a2 = math.radians((i+1) * 60)
    draw_line(1500*math.cos(a1), 1500*math.sin(a1),
              1500*math.cos(a2), 1500*math.sin(a2))

# 7. 画屋面投影圆（R=2460mm）
set_current_layer("ROOF")
draw_circle(0, 0, 2460)

# 8. 尺寸标注
set_current_layer("DIM")
add_dimension(-1500, 0, 1500, 0, offset_y=-450)

# 9. 文字标注
set_current_layer("ANNOTATION")
draw_text(0, 1700, "清式六角攒尖亭 B=3000mm", height=80)
draw_text(0, 1620, "檐柱高=2250mm 柱径=191mm 出檐=960mm", height=60)

# 10. 缩放适应视图
send_command("_.ZOOM _ALL")
```

#### 三间石牌坊完整绘图流程（W=10800mm）

```python
# 1. 清空
send_command("_.ERASE All")

# 2. 轴线
set_current_layer("AXIS")
draw_line(-18000, 0, 18000, 0)
draw_line(0, -3000, 0, 3000)

# 3. 柱位（四柱，明间5400mm，次间2700mm）
set_current_layer("WOOD_FRAME")
col_xs = [-5400, -540, 2430, 5400]
for cx in col_xs:
    draw_circle(cx, -1200, 297)   # 前柱
    draw_circle(cx, 1200, 297)    # 后柱

# 4. 台基
set_current_layer("BASE")
draw_rectangle(-7976, -1500, 7976, 1500)
draw_rectangle(-5400, -1200, 5400, 1200)

# 5. 屋面
set_current_layer("ROOF")
draw_rectangle(-7776, -1794, 7776, 1794)
draw_line(-2700, 1250, 2700, 1250)  # 正脊

# 6. 装饰（匾额位置）
set_current_layer("DECO")
draw_circle(-2970, 1250, 216)
draw_circle(945, 1250, 216)
draw_circle(3915, 1250, 216)

# 7. 标注
set_current_layer("DIM")
add_dimension(-5400, 0, 5400, 0, offset_y=-1600)
add_dimension(-5400, 0, -540, 0, offset_y=-1500)

# 8. 文字
set_current_layer("ANNOTATION")
draw_text(0, 1400, "清式三间石牌坊", height=80)
draw_text(0, 1320, "面阔10800mm 3间石坊", height=60)

# 9. 适应视图
send_command("_.ZOOM _ALL")
```

### CAD-MCP 命令速查表

| 功能 | 命令 |
|------|------|
| 新建图层 | `create_layer(name, color, linetype)` |
| 切换当前图层 | `set_current_layer(name)` |
| 画直线 | `draw_line(x1, y1, x2, y2)` |
| 画圆 | `draw_circle(x, y, r)` |
| 画矩形 | `draw_rectangle(x1, y1, x2, y2)` |
| 画多段线 | `draw_polyline(points, close=True/False)` |
| 画文字 | `draw_text(x, y, text, height)` |
| 线性标注 | `add_dimension(x1, y1, x2, y2, offset_x, offset_y)` |
| 执行任意命令 | `send_command("命令字符串")` |
| 截图确认 | `screenshot()` |
| 列出所有图层 | `list_layers()` |
| 列出所有实体 | `list_entities()` |
| 擦除全部 | `send_command("_.ERASE All")` |
| 适应视图 | `send_command("_.ZOOM _ALL")` |
| 保存图纸 | `send_command("_.SAVE")` |

### 标准操作流程

```
1. send_command("_.ERASE All")        # 清空旧内容
2. create_layer(...) x N              # 按顺序创建所有图层
3. set_current_layer("AXIS")          # 切换到轴线层
4. draw_line(...)                     # 画轴线
5. set_current_layer("BASE")          # 切换到台基层
6. draw_rectangle(...) / draw_polyline(...)
7. set_current_layer("WOOD_FRAME")    # 切换到木构架层
8. draw_circle(...)                   # 画柱位
9. set_current_layer("ROOF")          # 切换到屋面层
10. draw_circle(...) / draw_line(...)
11. set_current_layer("DIM")          # 切换到标注层
12. add_dimension(...)
13. set_current_layer("ANNOTATION")   # 切换到文字层
14. draw_text(...)
15. screenshot()                      # 截图确认效果
16. send_command("_.ZOOM _ALL")       # 适应视图
17. send_command("_.SAVE")            # 保存
```

### 与 .scr 文件的关系

- **CAD-MCP**：适合交互式修改、快速验证、调试参数
- **.scr 文件**：适合批量出图、归档交付、离线复用
- **推荐工作流**：MCP 调试确认参数 → 生成 SCR 批量导出 → 归档

---
