---
name: qingping-ai-skills
description: "青萍 AI 工具集 - 包含图片生成和图床上传功能。使用场景：(1) 生成 AI 图片，(2) 批量上传图片到图床，(3) 提到"青萍"、"qingping"、"图床"、"批量上传"、"AI生图"等关键词。"
version: "1.1.0"
homepage: "https://claw.lusyoe.com"
repository: "https://github.com/lusyoe/qingping-ai-skills.git"
authors: ["lusyoe"]
license: "MIT"
---

# 青萍 AI 工具集

包含图片生成和图床上传功能的工具集。

## 子技能

本仓库包含多个可独立安装的子技能：

### 1. image-generation - AI 图片生成

通过青萍 AI API 生成高质量图片并自动下载到本地。

```bash
# 安装
# 将 skills/image-generation 目录作为独立 skill 安装

# 使用
python scripts/generate_image.py "一只可爱的金鱼"
```

**功能特点：**
- 多种模型支持（nano-banana, nano-banana-2, nano-banana-pro）
- 多种比例（1:1, 16:9, 9:16）
- 多种尺寸（1K, 2K, 4K）
- 自动下载到本地

### 2. img-bed - 图床批量上传

批量上传本地图片到青萍图床。

```bash
# 安装
# 将 skills/img-bed 目录作为独立 skill 安装

# 使用
python scripts/batch_upload.py /path/to/images --category "风景"
```

**功能特点：**
- 递归扫描、多线程并发（默认 10 线程）
- 断点续传（从 CSV 读取已上传记录）
- 实时 CSV 日志（单个文件最多 10000 行）
- STS 签名缓存（1 小时）
- 批量回调（每 20 张）
- 支持 jpg/png/gif/bmp/webp/ico 格式

## 认证方式

所有子技能共用同一个 API Key：

```bash
export QINGPING_API_KEY='your-api-key-here'
```

**获取 API Key**：https://auth.lusyoe.com/profile

## 目录结构

```
qingping-ai-skills/
├── SKILL.md                    # 主文档（索引）
├── skills/                     # 子技能目录
│   ├── image-generation/       # AI 图片生成
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── generate_image.py
│   │
│   └── img-bed/                # 图床批量上传
│       ├── SKILL.md
│       ├── docs/
│       │   ├── sts签名.md
│       │   └── 批量回调.md
│       └── scripts/
│           ├── batch_upload.py
│           ├── get_sts.py
│           └── callback.py
│
└── docs/                       # 共享文档（可选）
```

## 安装方式

### 方式 1：安装全部技能

将整个仓库作为 skill 安装。

### 方式 2：单独安装子技能

```bash
# 只安装图片生成
cp -r skills/image-generation ~/.skills/

# 只安装图床上传
cp -r skills/img-bed ~/.skills/
```

## 更新日志

### v1.1.0

- 重构为多技能 monorepo 结构
- 支持独立安装子技能
- image-generation: AI 图片生成
- img-bed: 图床批量上传（含签名管理、回调管理模块）
