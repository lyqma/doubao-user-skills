---
name: 视频上传
description: 多平台视频自动上传技能（lijingpan/video-uploader）。Playwright 浏览器自动化上传视频到抖音/快手/小红书/视频号/TikTok，含反检测、Cookie 管理、字段生成、批量上传。抖音支持缩略图、商品链接、定时发布、同步头条/西瓜。触发词："批量上传"、"发布到抖音"、"多平台分发"。
---

# Video Uploader Skill

Automated video upload to major Chinese and international social media platforms using browser automation with comprehensive anti-detection measures and field generation capabilities.

## Supported Platforms

- **Douyin (抖音)**: Full feature support including thumbnails, product links, scheduled publishing, and third-party sync to Toutiao/Xigua.
- **Kuaishou (快手)**: titles, hashtags (max 3), scheduled publishing with confirmation dialogs.
- **Xiaohongshu (小红书)**: image and video posts (requires signature service).
- **TikTok**: Firefox browser, titles, hashtags, scheduled publishing, privacy controls.
- **Tencent Video / WeChat Channels (视频号)**: short title formatting, collections, original content declaration, category selection.

## Prerequisites

- Python 3.8+ with pip
- Dependencies: `pip install playwright loguru requests PyYAML` + `playwright install chromium firefox`
- Account cookies per platform (Playwright storage state JSON). First-time use triggers browser login.

## Core Scripts

### 1. Direct Upload Script
```
python scripts/upload_video.py \
  --platform douyin \
  --title "Video Title" \
  --video /path/to/video.mp4 \
  --tags "tag1,tag2,tag3" \
  --account /path/to/cookie.json
```

Required: `--platform` (douyin/kuaishou/tiktok/tencent/xhs), `--title`, `--video`, `--tags`, `--account`
Optional: `--publish-date "YYYY-MM-DD HH:MM:SS"` (0=immediate), `--thumbnail`, `--product-link`, `--product-title`, `--category`

### 2. Configuration-Based Upload
```
python scripts/upload_from_config.py config.json        # 单条
python scripts/upload_from_config.py batch.json --batch # 批量
```
JSON 配置格式：
```json
{
  "platform": "douyin",
  "video": { "path": "/path/video.mp4", "title": "标题", "description": "描述", "tags": ["t1","t2"] },
  "account": { "cookie_file": "/path/cookie.json" },
  "options": { "publish_date": "2024-12-31 18:00:00", "thumbnail": "/path/cover.jpg" }
}
```

### 3. Field Generation Tool
```
python scripts/generate_upload_config.py --platform douyin --video /path/video.mp4 --output json
# 从文件名自动生成：标题、标签（停用词过滤）、描述、封面（取视频帧）
# --schedule-days 1 --schedule-hour 18 生成排期
```

## Douyin-Specific Fields

| 字段 | 必填 | 说明 |
|---|---|---|
| title | ✅ | 最多 30 字 |
| video_path | ✅ | MP4 |
| tags | ✅ | 逗号分隔，# 前缀可省略 |
| account_file | ✅ | Cookie JSON |
| product_link | ❌ | **商品链接（短剧付费组件挂载关键）** |
| product_title | ❌ | 商品短标题（最多 10 字） |
| publish_date | ❌ | 定时发布 |
| thumbnail | ❌ | 竖版封面 |
| description | ❌ | 描述 |
| sync_third_party | ❌ | 同步头条/西瓜 |

Notes: Two page versions (v1/v2) auto-detected, supports third-party sync to Toutiao/Xigua.

## Authentication & Cookie Management

- First-time login: script opens browser for manual login (QR), saves session cookies to file
- Cookie validation before each upload; auto-triggers login if expired
- Cookie reuse: valid files reusable until expiration (typically 7-30 days)
- Recommended organization:
```
/home/ubuntu/cookies/
├── douyin_account1.json
├── douyin_account2.json
└── ...
```

## OpenClaw/Agent Integration Workflow

1. **Prepare Video**: MP4, platform requirements (duration/size/resolution)
2. **Generate Config**: `generate_upload_config.py --platform douyin --video x.mp4 --output-file config.json`
3. **Review & Customize**: edit title/tags/description, add product_link for short-drama CPS
4. **Execute**: `upload_from_config.py config.json`
5. **Verify**: check console output, platform published video, scheduled time

**Batch Upload**: batch JSON array + `--batch`; summary shows total/success/fail.

## 本环境适配说明

本机用内置浏览器自动化（bu）执行抖音上传，Python/Playwright 脚本作为独立备选：
- 抖音上传：`bu.upload_file('input[type=file]', mp4)` → 发布页填标题/描述 → 挂商品链接（短剧组件）→ 发布
- 多账号矩阵：每号一份登录态，发布间隔≥3 分钟
- 商品链接：短剧商单任务用任务详情页"上传视频"入口（组件自动挂载），普通带货用 `--product-link`

## Anti-Detection (参考)

- Disable automation controlled flag, custom UA/viewport, geolocation spoofing (Beijing), timezone config
- Override navigator.webdriver / plugins / languages; add chrome property
- Non-headless mode for most platforms; browser window visible during upload

## Limitations

- Xiaohongshu needs separate Flask signature service
- Most platforms require non-headless mode
- First-time auth always needs manual interaction (QR) — cannot be fully automated
- Platform UI changes may break selectors; scripts may need updates

## Troubleshooting

| 错误 | 处理 |
|---|---|
| Cookie Expired | 删除 cookie 文件重新登录 |
| Upload Failed | 检查视频格式/大小/网络 |
| Browser Not Found | `playwright install chromium firefox` |
| Page Structure Changed | 检查脚本更新或手动检查页面结构 |
| Headless Issues | 平台多数要求非无头模式 |
