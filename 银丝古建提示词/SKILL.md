---
name: 银丝古建提示词
description: >-
  生成不锈钢银丝古建（银丝古建）电影级图片提示词。
  核心材质锁定：40x40mm方管钢结构骨架 + 1mm不锈钢钢丝1cmx1cm密集方格网，
  银灰色哑光亮银不锈钢真实建筑质感。
  禁止木纹、实体瓦片、CG金属、发光线稿等错误材质。
version: "1.0.0"
license: MIT
user-invocable: true
tags:
  - architectural-visualization
  - stainless-steel
  - chinese-architecture
  - silver-wire
  - cinematic
  - prompt-engineering
  - material-lock
metadata:
  openclaw:
    emoji: "🏛️"
---

# 银丝古建提示词技能

## 核心材质定义（最高优先级，不可修改）

```
银丝古建 = 
40×40mm方管焊接钢结构骨架（承重主体）
+ 
1mm不锈钢钢丝编织1cm×1cm密集方格网（所有非立柱构件）
+ 
银灰色哑光亮银不锈钢真实建筑质感
```

**结构规则：**
- 立柱 = 实体不锈钢方管（有真实截面厚度与承重结构）
- 梁/檐口/斗拱/屋面轮廓/栏杆/门窗/装饰构件 = 1cm×1cm密集方格网镂空
- 整体 = 银灰色哑光亮银不锈钢，真实拉丝表面，真实焊接节点

## 使用方式

### A. 单栋亭台/牌楼（庭院、单体古建）
1. 用户提供场景描述（白天/夜晚/天气/角度等）
2. 从 `references/scenes.md` 选择对应场景变体
3. 严格遵循材质定义，不可替换材质
4. 生成完整 Midjourney 提示词

### B. 十座世界建筑跨街装置（丝路十城 / 世界文明长卷）
当用户要求"跨街装置 / 十座 / 丝路十城 / 世界文明 / 单座世界建筑"时，进入本分支：

1. 判断模式：**单座装置** 还是 **十座纵贯长卷**
2. 打开 `references/world-arch-cross-street/README.md`（总纲 + 序列 + 通用模板骨架）
3. 单座 → 打开对应 `0X-xxx.md` 取"专属"各节，套入总纲模板
4. 长卷 → 打开 `十城纵贯长卷模板.md`（地面/航拍二选一）+ 逐座 `0X-xxx.md`
5. 灯光/场景/材质/负面 → 对应 `lighting-standards.md` / `scene-standards.md` / `material-standards.md` / `negative-prompts-master.md`

**十座固定序列（顺序不可变）**：
01长安(重檐歇山顶唐式灯楼) → 02敦煌(三兔藻井莲花穹顶飞天) → 03喀什(连续尖拱廊洋葱穹顶) →
04撒马尔罕(雷吉斯坦肋纹蓝穹顶石榴灯) → 05波斯(双牛柱头波斯地毯圆盘) →
06巴格达(伊什塔尔门蓝琉璃狮子浮雕) → 07大马士革(倭马亚连拱廊宣礼塔星月灯) →
08伊斯坦布尔(圣索菲亚大穹顶细宣礼塔新月灯) → 09雅典(帕特农柱廊三角楣雕塑群) →
10罗马(斗兽场多层拱券罗马柱式四马战车)

**所有跨街装置统一硬约束**：
- 横跨约11米机动车道，进深≤2.5米，车行净空≥5.5米
- 仅8根圆形不锈钢立柱（左右各4，人行道/绿化带落地），机动车道中央/沥青路面零支撑
- 立柱直径约80mm，左右严格镜像对称
- 银丝古建：钢骨架 + 1cm×1cm不锈钢细丝方格网，全镂空透视
- 金属丝不发光，冰蓝白弱内透 + 各座专属2700K暖黄灯 + 特征色点缀
- 8K HDR 电影级夜景摄影，16-24mm广角，低机位仰拍（或无人机航拍）
- 文字标识仅各座对应汉字，规整毛笔镂空字体

## 快速提示词模板

```
一座完整的不锈钢银丝古建，飞檐斗拱、亭台楼阁，
采用40×40mm方管焊接钢结构骨架为承重主体，
所有梁、檐口、斗拱、屋面轮廓、栏杆、门窗及装饰构件，
均由1mm不锈钢钢丝紧密编织成1cm×1cm密集方格网镂空构成，
立柱为实体不锈钢方管具有真实截面厚度与承重结构，
整体材质为银灰色哑光亮银不锈钢，真实金属反射，
细腻拉丝表面，真实焊接节点，真实钢材厚度，
[补充场景描述...]
epic scale cinematic architecture photography,
low angle wide establishing shot,
shot on ARRI Alexa 65, 24mm anamorphic lens,
--ar 2.39:1 --style raw --s 500
```

## 严格禁止材质

```
木纹、木柱、木梁、仿木材质
实体瓦片、实体墙体、普通古建筑实体结构
铁艺、铝塑、塑料、玻璃钢
银色油漆、镜面银、CG金属、塑料金属
发光银线、单根银线、二维线稿
稀疏网格、过大网格孔洞、透明塑料网
黑色立柱、黑色立柱包边、黑色边框
```

## 详细参考文档

### 单栋亭台/牌楼
- `references/material-standards.md` — 材质标准详解
- `references/scenes.md` — 场景变体库（夜景/暴雨/日出等）
- `references/negative-prompts.md` — 负面提示词大全

### 跨街世界建筑装置（`references/world-arch-cross-street/`）
- `README.md` — 总纲、十座序列、通用模板骨架
- `十城纵贯长卷模板.md` — 十座一张图（地面/航拍二选一）
- `scene-standards.md` — 场景基底标准（敦煌沙州南路夜景）
- `lighting-standards.md` — 灯光标准（冰蓝白内透+2700K暖黄+特征色）
- `material-standards.md` — 跨街银丝材质专版
- `negative-prompts-master.md` — 负面提示词大全（综合版）
- `photography-standards.md` — 摄影/机位/画幅标准
- `01-changan.md` … `10-rome.md` — 十座建筑专属造型/灯饰/文字/完整提示词
