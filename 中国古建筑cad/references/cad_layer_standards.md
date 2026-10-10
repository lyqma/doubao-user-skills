# AutoCAD 图层颜色与线型速查

## 标准图层定义（SCR 脚本使用）

| 图层名 | 颜色索引 | 线型 | 用途 | 适用构件 |
|--------|---------|------|------|---------|
| AXIS | 1 (红) | CENTER | 定位轴线 | 中心线、对称轴 |
| BASE | 8 (白) | CONTINUOUS | 台基台阶 | 须弥座、阶条石、踏跺 |
| WOOD_FRAME | 3 (绿) | CONTINUOUS | 木构架 | 柱、梁、枋、檩、椽 |
| DOUGONG | 6 (青莲) | CONTINUOUS | 斗拱层 | 栌斗、交互斗、拱、翘、昂 |
| ROOF | 5 (青) | CONTINUOUS | 屋面 | 正脊、垂脊、戗脊、屋面轮廓 |
| RAIL | 4 (蓝) | CONTINUOUS | 栏杆 | 美人靠、栏杆、望柱 |
| DIM | 2 (白) | CONTINUOUS | 尺寸标注 | 标注线、尺寸数字 |
| ANNOTATION | 7 (白) | CONTINUOUS | 文字说明 | 标题、参数注释 |
| HIDDEN | 1 (红) | HIDDEN | 不可见轮廓 | 被遮挡的构件线 |

---

## SCR 图层创建语句模板

```
LAYER NEW AXIS COLOR 1 CENTER
LAYER NEW BASE COLOR 8 CONTINUOUS
LAYER NEW WOOD_FRAME COLOR 3 CONTINUOUS
LAYER NEW DOUGONG COLOR 6 CONTINUOUS
LAYER NEW ROOF COLOR 5 CONTINUOUS
LAYER NEW RAIL COLOR 4 CONTINUOUS
LAYER NEW DIM COLOR 2 CONTINUOUS
LAYER NEW ANNOTATION COLOR 7 CONTINUOUS
```

---

## 平面图常用命令序列

```
; ===== 六角亭平面图 =====
; 1. 创建图层
LAYER NEW AXIS COLOR 1 CENTER
LAYER NEW BASE COLOR 8 CONTINUOUS
LAYER NEW WOOD_FRAME COLOR 3 CONTINUOUS
LAYER NEW ROOF COLOR 5 CONTINUOUS
LAYER NEW DIM COLOR 2 CONTINUOUS
LAYER NEW ANNOTATION COLOR 7 CONTINUOUS

; 2. 中心轴线
LAYER AXIS
LINE -10000,0,0 10000,0,0
LINE 0,-10000,0 0,10000,0

; 3. 台基六边形轮廓（B=3000，外半径=3600）
LAYER BASE
POLYGON 6 0,0,0 I 3600

; 4. 柱定位圆（半径=B/2=1500）
LAYER WOOD_FRAME
CIRCLE 0,0,0 1500

; 5. 6根柱位（在定位圆上，角度间隔60°）
; 坐标计算公式：x = R×cos(θ), y = R×sin(θ)
; θ = 0°, 60°, 120°, 180°, 240°, 300°
; R = 1500
CIRCLE 1500,0,0 95.5     ; 柱位1，D_column=191mm，半径≈95.5
CIRCLE 750,1299,0 95.5   ; 柱位2
CIRCLE -750,1299,0 95.5  ; 柱位3
CIRCLE -1500,0,0 95.5    ; 柱位4
CIRCLE -750,-1299,0 95.5 ; 柱位5
CIRCLE 750,-1299,0 95.5  ; 柱位6

; 6. 连接柱位（檐枋位置）
LAYER WOOD_FRAME
LINE 1500,0,0 750,1299,0
LINE 750,1299,0 -750,1299,0
LINE -750,1299,0 -1500,0,0
LINE -1500,0,0 -750,-1299,0
LINE -750,-1299,0 750,-1299,0
LINE 750,-1299,0 1500,0,0

; 7. 尺寸标注
LAYER DIM
DIMLINEAR -1500,0,0 1500,0,0 0,-400

; 8. 文字标注
LAYER ANNOTATION
TEXT 0,2200,0 80 0 清式六角攒尖亭 B=3000mm

; 9. 缩放适应
ZOOM ALL
```

---

## 剖面图坐标参考

### 六角亭剖面（沿 X 轴切，Y=0）

```
标高参考（H_column=2250, D_column=191, roof_rise=1200, H_plinth=400）

地坪线：Y = -10000 到 Y = 10000，Z = 0

台基顶面：Z = 400
柱底：Z = 400
柱顶（檐枋底）：Z = 400 + 2250 = 2650
檐枋顶：Z = 2650 + 191 = 2841
屋面底：Z = 2841
屋面顶（正脊）：Z = 2841 + 1200 = 4041
宝顶点：Z = 4041 + 300 = 4341
```

---

## 常见坐标计算工具

### 正多边形顶点坐标（中心在原点，外接圆半径 R）

| 边数 n | 角度步长 | 顶点 k 的坐标 |
|--------|---------|-------------|
| 6 | 60° | (R·cos(k×60°), R·sin(k×60°)) |
| 8 | 45° | (R·cos(k×45°), R·sin(k×45°)) |

**六角亭（R=1500mm）精确坐标：**
```
柱位0: ( 1500,    0)
柱位1: (  750, 1299)
柱位2: ( -750, 1299)
柱位3: (-1500,    0)
柱位4: ( -750, -1299)
柱位5: (  750, -1299)
```

**八角亭（R=1376mm，B=3600时）精确坐标：**
```
柱位0: ( 1376,     0)
柱位1: (  973,  973)
柱位2: (    0, 1376)
柱位3: ( -973,  973)
柱位4: (-1376,     0)
柱位5: ( -973, -973)
柱位6: (    0, -1376)
柱位7: (  973, -973)
```
