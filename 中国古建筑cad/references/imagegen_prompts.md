# AI 图片生成提示词 — 中国传统古建照片级渲染 V5.0

> 用于 ComfyUI / Midjourney / Stable Diffusion 等 AI 绘图工具
> 输入 JSON 参数，输出电影级照片提示词

---

## 亭类提示词模板

### 六角攒尖亭（清式）

```
Architectural photography of a traditional Chinese hexagonal pavilion,
Qing dynasty style, side distance B=3000mm.
The pavilion stands on a white marble plinth with three stepped tiers.
Six red lacquered wooden columns rise from the plinth, supporting a green-glazed tile cone roof
with elegantly upturned eaves at each corner.
A golden baoding finial crowns the roof peak.
Doungong brackets visible between column tops and roof.
A curved wooden railing (meiren-kao) encircles the interior.
Soft daylight, overcast sky, garden setting with moss and stone path.
Shot from 35-degree low angle, cinematic composition, photorealistic, 8K.
--ar 16:9 --v 6
```

### 八角攒尖亭（清式）

```
Architectural photography of a traditional Chinese octagonal pavilion,
Qing dynasty style, side distance B=3600mm.
White marble stepped plinth, eight vermilion lacquered columns,
dark grey-green roof tiles with pronounced corner upturns.
Golden pagoda finial at apex. Intricate doungong bracket sets.
Surrounded by classical Chinese garden — rockery, bamboo, koi pond.
Golden hour sunlight, lens flare, shallow depth of field.
Wide-angle architectural shot, photorealistic, architectural digest style.
--ar 16:9 --v 6
```

---

## 殿类提示词模板

### 单檐歇山殿（五间）

```
Architectural photography of a grand Chinese xiēshān hall,
Qing dynasty imperial style, 5-bay facade spanning 18 meters.
Massive white marble terrace platform with central staircase.
Rows of towering vermilion lacquered columns with stone drum bases.
Intricate doungong bracket complexes at each column capital.
Classic xiēshān (hip-and-gable) roof with green-glazed tiles,
curved eaves sweeping upward at corners, ornate ridge decorations.
Golden phoenix finials at ridge ends. Deep blue sky, dramatic clouds.
Shot at golden hour, volumetric light rays, ultra-detailed, 8K.
Architectural visualization, China Daily style.
--ar 21:9 --v 6
```

---

## 牌楼提示词模板

### 单间石牌坊

```
Architectural photography of a solitary Chinese stone paifang archway,
Qing dynasty memorial arch, white marble construction.
Two massive cylindrical stone pillars on carved plinths,
supporting a compact xiēshān roof with grey stone tiles.
Ornate carvings of dragons and clouds on the beam panels.
A rectangular plaque panel inscribed with Chinese calligraphy.
Set against a backdrop of ancient cypress trees and temple walls.
Overcast diffused light, misty atmosphere, serene mood.
Eye-level shot, symmetrical composition, photorealistic.
--ar 4:3 --v 6
```

### 三间石牌坊

```
Grand three-bay Chinese stone paifang, imperial cemetery style.
Massive grey granite pillars on multi-tiered stone platforms.
Dark slate roof with upturned eaves, intricate stone carving throughout.
Dragon motifs, floral patterns, and symbolic animals on every beam.
Flanking stone lions at the base. Ancient trees framing the scene.
Dawn light, atmospheric fog, sense of solemn grandeur.
Wide architectural perspective, shot on medium format film.
--ar 16:9 --v 6
```

### 四柱三间冲天式石牌坊

```
Soaring chōngtiān-style stone paifang, four pillars three bays.
Stone columns pierce through the roofline, topped with floral finials.
Grey stone construction with elaborate relief carvings.
Multiple roof tiers creating layered silhouette against sky.
Plaque panels with imperial calligraphy in each bay.
Mountain backdrop, golden hour backlight, ethereal atmosphere.
Low-angle heroic perspective, dramatic scale.
--ar 3:4 --v 6
```

### 三间木牌楼（双檐）

```
Magnificent three-bay timber paifang with double eaves,
Qing dynasty lacquered wood construction.
Vermilion and gold painted columns with intricate doungong brackets.
Two tiers of sweeping green-glazed tile roofs,
golden ridge ornaments and corner bells.
Imperial palace courtyard setting, red walls in background.
Bright midday sun, vivid colors, rich textures.
Architectural detail shot, National Geographic quality.
--ar 16:9 --v 6
```

---

## 通用材质关键词速查

| 材质 | 英文关键词 | 色值参考 |
|------|-----------|---------|
| 汉白玉石 | white marble, Carrara marble | #F2F0EC |
| 青石 | grey granite, bluestone | #6B6B6B |
| 朱红漆柱 | vermilion lacquered wood | #8B1A1A |
| 原木色 | natural teak, warm wood | #7B5B3A |
| 青瓦 | dark grey roof tiles | #333842 |
| 琉璃黄 | imperial yellow glaze | #D4A017 |
| 琉璃绿 | temple green glaze | #2E7D32 |
| 金箔装饰 | gold leaf ornament | #FFD700 |

---

## 通用光影关键词

| 场景氛围 | 关键词 |
|---------|--------|
| 清晨 | dawn light, soft golden hour, atmospheric haze |
| 正午 | bright midday, hard shadows, vivid colors |
| 黄昏 | golden hour, warm sidelight, long shadows |
| 阴天 | overcast, diffused light, moody atmosphere |
| 雪景 | winter snow, fresh powder, cold blue tones |
| 夜景 | night photography, lantern glow, moonlight |

---

## ComfyUI Workflow 节点说明

如需在 ComfyUI 中自动调用，配置如下：

```
Workload Prompt Template:
{type}_architectural_photography_prompt
Input: JSON config → 解析参数 → 替换模板中的 B/W/间数 等变量
Output: 完整提示词 → SDXL/SD3/Flux 模型生成
```

支持模型：SDXL 1.0, SD3 Medium, Flux.1, Midjourney v6
