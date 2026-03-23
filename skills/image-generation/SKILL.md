---
name: qingping-image-generation
description: '青萍 AI 图片生成工具。通过 API 生成高质量图片并自动下载到本地。使用场景：(1) 用户需要生成 AI 图片，(2) 提到"青萍"、"qingping"、"生成图片"、"AI生图"等关键词时触发。支持多种模型、尺寸和比例配置，默认生成 16:9 比例图片。'
license: "MIT"
metadata:
  version: "1.0.0"
  homepage: "https://claw.lusyoe.com"
  repository: "https://github.com/lusyoe/qingping-ai-skills.git"
  authors: ["lusyoe"]
  requirements:
    environment_variables:
      - QINGPING_API_KEY
---

# 青萍 AI 图片生成

通过青萍 AI API 生成高质量图片并自动下载到本地 `qingping-ai` 目录。

## 认证方式

配置 `QINGPING_API_KEY` 环境变量：

```bash
# 临时配置（当前终端会话）
export QINGPING_API_KEY='your-api-key-here'

# 永久配置（添加到 shell 配置文件）
echo 'export QINGPING_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**获取 API Key**：
1. 登录青萍AI平台：https://auth.lusyoe.com/profile
2. 在个人信息页面，滚动到最下面
3. 点击生成或查看 API Key

## 快速开始

```bash
# 基础用法（使用默认模型 nano-banana）
python scripts/generate_image.py "一只可爱的金鱼"

# 指定模型
python scripts/generate_image.py "一只可爱的金鱼" nano-banana-2

# 完整参数
python scripts/generate_image.py "提示词" [模型] [数量] [比例] [尺寸]
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| prompt | 必填 | 图片描述提示词 |
| model | `nano-banana` | 模型名称 |
| count | `1` | 生成数量 |
| ratio | `16:9` | 图片比例 |
| size | `1K` | 图片尺寸 |

## 支持的模型

| 模型名称 | 说明 |
|---------|------|
| `nano-banana` | 默认模型，快速生成 |
| `nano-banana-2` | 增强版本，更高质量 |
| `nano-banana-pro` | 专业版本，最佳质量 |

## 支持的比例

| 比例 | 说明 |
|------|------|
| `1:1` | 正方形 |
| `16:9` | 默认，横屏，适合封面 |
| `9:16` | 竖屏，适合手机壁纸 |

## 支持的尺寸

| 尺寸 | 说明 |
|------|------|
| `1K` | 默认，1024px |
| `2K` | 2048px，更高质量 |
| `4K` | 4096px，最高质量 |

## API 端点

- **创建任务**: `POST https://video.lusyoe.com/api/img/generations`
- **查询状态**: `GET https://video.lusyoe.com/api/img/generations/{task_id}/status`
