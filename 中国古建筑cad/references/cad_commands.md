# AutoCAD SCR 命令速查手册 V4.12

## 一、命令分类总览

### 1.1 绘图基本命令

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| LINE | `LINE x1,y1,z1 x2,y2,z2` | 绘制两点直线 | `LINE 0,0,0 1000,0,0` |
| CIRCLE | `CIRCLE x,y,z radius` | 画圆 | `CIRCLE 0,0,0 500` |
| POLYGON | `_.POLYGON n origin I/D length` | 正多边形(n≥3) | `_.POLYGON 6 0,0,0 I 3000` |
| RECTANGLE | `RECTANGLE x1,y1 x2,y2` | 画矩形(对角点) | `RECTANGLE -1000,-500 1000,500` |
| ARC | `ARC center start end` | 圆弧 | `ARC 0,0,0 500,0,0 0,500,0` |
| SPLINE | `SPLINE pt1 pt2 ... _C` | 样条曲线(加_C闭合) | `SPLINE 0,0,0 100,200,0 200,0,0 _C` |
| ELLIPSE | `ELLIPSE center axis_end minor_ratio` | 椭圆 | `ELLIPSE 0,0,0 500,0,0 0.5` |
| PLINE | `_.PLINE pt1 pt2 ... _C` | 多段线(加_C闭合) | `_.PLINE 0,0,0 100,0,0 100,100,0 0,100,0 _C` |

### 1.2 修改命令

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| OFFSET | `OFFSET distance source target` | 偏移复制 | `OFFSET 200 100,0,0 200,0,0` |
| COPY | `COPY select base dest` | 复制对象 | `COPY 1,0,0 0,0,0 2,0,0` |
| MOVE | `MOVE select base dest` | 移动对象 | `MOVE 1,0,0 0,0,0 500,0,0` |
| ROTATE | `ROTATE select base angle` | 旋转对象 | `ROTATE 0,0,0 90` |
| SCALE | `SCALE select base factor` | 缩放对象 | `SCALE 0,0,0 2` |
| ARRAY | `ARRAY select type params` | 阵列(暂未在SCR中完整支持) | - |
| TRIM | `TRIM boundary edges select` | 修剪 | `TRIM _F 0,0,0 0,1000,0 500,0,0 500,1000,0` |
| EXTEND | `EXTEND boundary edges select` | 延伸 | `EXTEND _F 0,0,0 0,1000,0 500,0,0 500,500,0` |
| BREAK | `BREAK obj pt1 pt2` | 打断对象 | `BREAK 0,0,0 100,0,0` |
| CHAMFER | `CHAMFER dist1 dist2 obj1 obj2` | 倒角 | - |
| FILLET | `FILLET radius obj1 obj2` | 圆角 | `FILLET 50 0,0,0 100,0,0` |

### 1.3 图层命令

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| LAYER NEW | `LAYER NEW name COLOR color LT type` | 新建图层 | `LAYER NEW AXIS COLOR 1 CENTER` |
| LAYER SET | `LAYER SET name` | 设置当前图层 | `LAYER AXIS` |
| LAYER ON | `LAYER ON name` | 打开图层 | `LAYER ON ALL` |
| LAYER OFF | `LAYER OFF name` | 关闭图层 | `LAYER OFF HIDDEN` |
| LAYER COLOR | `LAYER COLOR color name` | 改图层颜色 | `LAYER COLOR 3 WOOD_FRAME` |
| LAYER LT | `LAYER LT type name` | 改图层线型 | `LAYER LT DASHED HIDDEN` |
| LAYER FREEZE | `LAYER FREEZE name` | 冻结图层 | `LAYER FREEZE TEMP` |
| LAYER THAW | `LAYER THAW name` | 解冻图层 | `LAYER THAW ALL` |
| LAYER U | `LAYER U name` | 取消当前层(setvar Laycur) | `LAYER U AXIS` |

### 1.4 标注命令

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| DIMLINEAR | `DIMLINEAR p1 p2 offset` | 水平/垂直标注 | `DIMLINEAR 0,0,0 1000,0,0 0,-100` |
| DIMALIGNED | `DIMALIGNED p1 p2 offset` | 对齐标注(任意角度) | `DIMALIGNED 0,0,0 500,500,0 0,-100` |
| DIMDIAMETER | `DIMDIAMETER obj pt` | 直径标注 | `DIMDIAMETER 0,0,0 100,0,0` |
| DIMRADIUS | `DIMRADIUS obj pt` | 半径标注 | `DIMRADIUS 0,0,0 200,0,0` |
| DIMANGULAR | `DIMANGULAR obj1 obj2 pt` | 角度标注 | `DIMANGULAR 0,0,0 100,0,0 0,100,0 50,50,0` |
| DIMCONTINUE | `DIMCONTINUE p1 p2 offset` | 连续标注 | `DIMCONTINUE 0,0,0 300,0,0 0,-100` |
| DIMBASELINE | `DIMBASELINE p1 p2 offset` | 基线标注 | `DIMBASELINE 0,0,0 300,0,0 0,-100` |
| DIMORIGIN | `DIMORIGIN p1 p2` | 原点到点标注 | `DIMORIGIN 0,0,0 500,0,0` |

### 1.5 文字命令

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| TEXT | `TEXT h a c x,y,z text` | 单行文字(h高度,a角度,c对齐) | `TEXT 80 0 L 0,2000,0 标题` |
| MTEXT | `MTEXT point width text` | 多行文字 | `MTEXT 0,2000,0 2000 标题` |
| DTEXT | (同TEXT) | 旧版单行文字 | `DTEXT 80 0 0,2000,0 标题` |
| Mleader | (需交互，SCR中不常用) | 多行引线 | - |

### 1.6 视图与输出

| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| ZOOM | `ZOOM all/extent/window p1 p2` | 缩放视图 | `ZOOM ALL` |
| VIEW | `VIEW save name` | 保存视图 | `VIEW SAVE plan` |
| VIEW | `VIEW restore name` | 恢复视图 | `VIEW RESTORE plan` |
| PLOT | (需交互，不推荐在SCR中) | 打印 | - |

---

## 二、古建CAD专用命令模式

### 2.1 柱网生成模板（六角亭）

```
; 1. 轴网
LAYER AXIS
LINE -{axis_len},0,0 {axis_len},0,0
LINE 0,-{axis_len},0 0,{axis_len},0

; 2. 柱定位圆
LAYER WOOD_FRAME
CIRCLE 0,0,0 {R_col}

; 3. 柱位圆（6根）
CIRCLE {x1},{y1},0 {col_r}
CIRCLE {x2},{y2},0 {col_r}
CIRCLE {x3},{y3},0 {col_r}
CIRCLE {x4},{y4},0 {col_r}
CIRCLE {x5},{y5},0 {col_r}
CIRCLE {x6},{y6},0 {col_r}

; 4. 檐枋连线（相邻柱位）
LINE {x1},{y1},0 {x2},{y2},0
LINE {x2},{y2},0 {x3},{y3},0
...
```

### 2.2 台基台阶模板

```
; 三层台阶（自下而上收分）
LAYER BASE
; 最下层（最大）
RECTANGLE -{W1},-{D1} {W1},{D1}
; 中间层
RECTANGLE -{W2},-{D2} {W2},{D2}
; 最上层（最小，即台基顶面）
RECTANGLE -{W3},-{D3} {W3},{D3}
```

### 2.3 屋脊线模板（歇山顶）

```
; 正脊（水平，居中）
LAYER ROOF
LINE -{ridge_half},0,{ridge_z} {ridge_half},0,{ridge_z}

; 垂脊（从正脊两端斜向下到檐口）
LINE -{ridge_half},{depth/2},0,{ridge_z} -{eave_end},{-depth/2},0,{eave_z}
LINE {ridge_half},{depth/2},0,{ridge_z} {eave_end},{-depth/2},0,{eave_z}

; 戗脊（从垂脊下端分出，向外斜）
; （quick_shell模式下用简化线表示）
```

### 2.4 栏杆/美人靠模板

```
; 望柱（栏杆立柱）
LAYER RAIL
CIRCLE {x},{y},0 {baluster_r}
; 栏板（连接望柱的水平线）
LINE {x1},{y1},0 {x2},{y2},0
; 扶手（顶部水平线）
LINE {x1},{y1+H},{0} {x2},{y2+H},{0}
```

---

## 三、坐标计算速查

### 3.1 正多边形柱位坐标

| 边数 | 角度 | 柱位坐标公式 |
|------|------|-------------|
| 4（四角） | 0°,90°,180°,270° | (R,0), (0,R), (-R,0), (0,-R) |
| 6（六角） | 0°,60°,120°,180°,240°,300° | (R,0), (R/2,R√3/2), (-R/2,R√3/2), (-R,0), (-R/2,-R√3/2), (R/2,-R√3/2) |
| 8（八角） | 0°,45°,90°,135°,180°,225°,270°,315° | (R,0), (R/√2,R/√2), (0,R), ... |

**六角亭 B=3000mm（R=1500mm）精确值：**
```
柱位0: ( 1500,     0)
柱位1: (  750,  1299)   ; 1500×sin(60°)
柱位2: ( -750,  1299)
柱位3: (-1500,     0)
柱位4: ( -750, -1299)
柱位5: (  750, -1299)
```

**八角亭 B=3600mm（R=1376mm）精确值：**
```
柱位0: ( 1376,     0)
柱位1: (  973,   973)   ; 1376/√2
柱位2: (    0,  1376)
柱位3: ( -973,   973)
柱位4: (-1376,     0)
柱位5: ( -973,  -973)
柱位6: (    0, -1376)
柱位7: (  973,  -973)
```

### 3.2 歇山殿开间轴线坐标

面阔五间（每间3600mm），原点居中：
```
轴1: x = -9000
轴2: x = -5400
轴3: x = -1800
轴4: x =  +1800
轴5: x =  +5400
轴6: x =  +9000
```

---

## 四、批处理常用序列

### 4.1 批量生成多个建筑

```batch
; 在Windows命令行中循环调用
for %f in (*.json) do python gen_scr.py "%f" --output .\output
```

### 4.2 SCR文件合并

```
; 多个建筑图纸合并到一个文件
; 方法：在每个建筑脚本末尾加上 _NEWFILE 命令（如支持）
; 或手动拼接：COPY plan1.scr+plan2.scr combined.scr
```

---

## 五、常用线型说明

| 线型名 | 用途 | 颜色建议 | 图层 |
|--------|------|---------|------|
| CONTINUOUS | 实线（默认） | 按图层定义 | 大多数构件 |
| CENTER | 中心线（点划线） | 红色(1) | AXIS |
| HIDDEN | 虚线（不可见轮廓） | 红色(1) | HIDDEN |
| DASHED | 短划线 | 按情况 | 辅助线 |
| BORDER | 粗实线边框 | 黑色(7) | 图框 |

---

## 六、AutoCAD SCR脚本注意事项

1. **所有坐标必须为绝对坐标**，不使用相对坐标（`@`符号）
2. **命令之间用换行分隔**，不能用分号注释在命令行中间
3. **注释以分号`;`开头**，放在独立行
4. **ZOOM ALL** 放在脚本末尾确保图形完整显示
5. **LAYER 命令需先创建再使用**，否则会报错
6. **POLYGON 命令用 `_.POLYGON`** 避免语言本地化问题
7. **坐标用逗号分隔**，不用空格
8. **Z坐标可省略**（二维图），但建议统一写 `,0` 避免3D误操作
