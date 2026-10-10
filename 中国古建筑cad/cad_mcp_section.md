
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
