---
name: qingping-img-bed
description: '青萍图床批量上传工具。支持递归扫描、多线程并发、断点续传、实时日志。使用场景：(1) 批量上传图片到图床，(2) 提到"图床"、"批量上传"、"图片上传"、"qingping img"等关键词时触发。支持 jpg/png/gif/bmp/webp/ico 格式，每批20张自动回调，CSV日志记录。'
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

# 青萍图床批量上传

批量上传本地图片到青萍图床，支持断点续传、多线程并发、实时日志。

## 认证方式

配置 `QINGPING_API_KEY` 环境变量：

```bash
export QINGPING_API_KEY='your-api-key-here'
```

**获取 API Key**：https://auth.lusyoe.com/profile

## 快速开始

```bash
# 基础用法
python scripts/batch_upload.py /path/to/images

# 完整参数
python scripts/batch_upload.py /path/to/images \
  --concurrency 10 \
  --batch-size 20 \
  --category "风景" \
  --tags "自然,山水" \
  --visibility public

# 强制重新上传（忽略已上传记录）
python scripts/batch_upload.py /path/to/images --force
```

## 核心特性

1. **递归扫描** - 自动扫描指定文件夹及子文件夹中的所有图片
2. **多线程并发** - 使用线程池控制并发，默认 10 个线程
3. **断点续传** - 从 CSV 记录读取已上传文件，避免重复
4. **百万级友好** - 分批扫描、懒加载，不一次性加载全部路径
5. **实时日志** - 上传结果实时写入 CSV 文件
6. **签名缓存** - STS 签名缓存 1 小时，减少 API 调用
7. **批量回调** - 每 20 张图片自动回调注册

## 支持的图片格式

- jpg / jpeg
- png
- gif
- bmp
- webp
- ico

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `source_dir` | 必填 | 要上传的图片目录 |
| `--concurrency, -c` | 10 | 并发上传线程数 |
| `--batch-size, -b` | 20 | 批次大小（回调间隔） |
| `--category` | 未分类 | 图片分类 |
| `--tags` | 空 | 标签（逗号分隔） |
| `--visibility` | public | 可见性 |
| `--force, -f` | false | 强制重新上传 |

## 上传流程

```
1. 扫描文件夹 → 过滤图片文件（jpg/png/gif/bmp/webp/ico）
2. 检查 CSV 记录 → 跳过已上传文件（除非 --force）
3. 获取 STS 签名（缓存 1 小时）
4. 上传到阿里云 OSS（表单 POST 方式）
5. 累积到 20 张 → 调用 batch-callback 接口
6. 记录结果到 CSV
7. 等待 10 秒后继续下一批
```

## 输出文件

上传完成后，会在扫描目录下生成：

```
/path/to/images/
└── result/
    ├── qingping_upload_log.csv    # 上传日志
    └── cache/
        └── signature.json         # 签名缓存
```

### CSV 日志格式

```
上传时间,图片ID,文件路径,文件名,文件大小,状态,CDN链接,错误信息,耗时(ms)
2024-01-15 10:30:00,12345,/path/to/images,image.jpg,102.4KB,success,https://img-cdn.lusyoe.cn/...,,1234
```

### CSV 分片

单个 CSV 文件最多 10000 行，超出自动创建新文件：

```
qingping_upload_log.csv          # 当前日志
qingping_upload_log_20240115_103000.csv  # 历史日志
```

## 模块结构

```
scripts/
├── batch_upload.py    # 批量上传主逻辑
├── get_sts.py         # STS 签名管理
└── callback.py        # 批量回调管理
```

## API 端点

- **获取签名**: `POST https://img.lusyoe.com/api/sts/upload_signature`
- **批量回调**: `POST https://img.lusyoe.com/api/upload/batch-callback`

## 错误处理

- **未配置认证信息**: 提示 API Key 配置步骤
- **签名获取失败**: 自动重试 3 次（指数退避）
- **OSS 上传失败**: 记录失败原因，继续下一张
- **回调失败**: 记录错误，不中断流程
- **网络错误**: 指数退避重试（1s, 2s, 4s）

## 参考文档

- [STS 签名](docs/sts签名.md)
- [批量回调](docs/批量回调.md)
