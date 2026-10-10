---
name: 银丝Blender建模
version: "5.0"
description: 召家班银丝古建筑 Blender 自动建模永久规范。参考图=施工图，先结构后网格，1mm钢丝+10×10mm正方形网格，大型承托平台，真实连接，多视角验证。
---

# 银丝古建 Blender 建模 V5.0 永久规范

## 核心原则
1. 参考图=施工图级几何依据，不是风格参考
2. 先理解建筑→再建结构→再建连接→再建网格→最后材质灯光
3. 大型平台必须完整托起所有立柱，明显大于主体
4. 所有构件真实三维连接，禁止视觉假连接
5. 1mm钢丝+10×10mm正方形网格，真实几何不是贴图

## 执行顺序
REFERENCE_ANALYSIS → PLATFORM → COLUMNS → BEAMS → ROOF → EAVES → RIDGE → GRID → DECORATION → VALIDATION

## 默认材质
- 银丝：Metallic=1.0, Roughness=0.28, BaseColor=(0.85,0.86,0.88)
- 金饰：Metallic=0.95, Roughness=0.15, BaseColor=(0.85,0.65,0.15)
- 台基：Metallic=0, Roughness=0.85

## 渲染
- Cycles, 32 samples, denoising
- Sun energy=5.0, 前上方45°
- Hosek-Wilkie天空, strength=0.7

## 禁止
菱形/六边形/三角网格、实体墙、塑料感、悬浮、穿模、随机加结构、修改相机掩盖错误
