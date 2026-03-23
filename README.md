# 青萍 AI 工具集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/lusyoe/qingping-ai-skills)

包含图片生成和图床上传功能的 AI 工具集。

## 功能模块

### 🎨 AI 图片生成 (image-generation)

通过青萍 AI API 生成高质量图片并自动下载到本地。

```bash
python skills/image-generation/scripts/generate_image.py "一只可爱的金鱼"
```

**特性：**
- 多种模型支持（nano-banana, nano-banana-2, nano-banana-pro）
- 多种比例（1:1, 16:9, 9:16）
- 多种尺寸（1K, 2K, 4K）
- 自动下载到本地

### 📤 图床批量上传 (img-bed)

批量上传本地图片到青萍图床，支持断点续传和多线程并发。

```bash
python skills/img-bed/scripts/batch_upload.py /path/to/images --category "风景"
```

**特性：**
- 递归扫描、多线程并发（默认 10 线程）
- 断点续传（从 CSV 读取已上传记录）
- 实时 CSV 日志（单个文件最多 10000 行）
- STS 签名缓存（1 小时）
- 批量回调（每 20 张）
- 支持 jpg/png/gif/bmp/webp/ico 格式

## 快速开始

### 1. 获取 API Key

访问 [青萍 AI 平台](https://auth.lusyoe.com/profile) 获取 API Key。

### 2. 配置环境变量

```bash
export QINGPING_API_KEY='your-api-key-here'
```

### 3. 使用工具

```bash
# 生成图片
python skills/image-generation/scripts/generate_image.py "一只可爱的金鱼"

# 批量上传图片
python skills/img-bed/scripts/batch_upload.py /path/to/images
```

## 目录结构

```
qingping-ai-skills/
├── SKILL.md                    # 技能配置文件
├── README.md                   # 项目说明文档
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

## API 端点

### 图片生成
- 创建任务: `POST https://video.lusyoe.com/api/img/generations`
- 查询状态: `GET https://video.lusyoe.com/api/img/generations/{task_id}/status`

### 图床上传
- 获取签名: `POST https://img.lusyoe.com/api/sts/upload_signature`
- 批量回调: `POST https://img.lusyoe.com/api/upload/batch-callback`

## 更新日志

### v1.1.0
- 重构为多技能 monorepo 结构
- 支持独立安装子技能
- image-generation: AI 图片生成
- img-bed: 图床批量上传（含签名管理、回调管理模块）

## 许可证

[MIT](LICENSE)

## 作者

[lusyoe](https://github.com/lusyoe)

## 主页

[青萍 AI 平台](https://claw.lusyoe.com)
