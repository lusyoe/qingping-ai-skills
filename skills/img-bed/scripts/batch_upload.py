#!/usr/bin/env python3
"""
青萍图床批量上传脚本
支持断点续传、多线程并发、实时日志、批量回调

功能特性：
1. 递归扫描指定文件夹，过滤图片文件
2. 多线程池控制并发，避免IO爆炸
3. 断点续传：从CSV记录读取已上传文件，避免重复
4. 百万级友好：分批扫描、懒加载
5. 实时CSV日志（单个文件最多10000行，超出自动分片）
6. 批量回调：每20张图片调用一次batch-callback
"""

import os
import sys
import csv
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import request, error
from dataclasses import dataclass
import threading

from get_sts import SignatureManager, Signature
from callback import CallbackManager


BATCH_SIZE = 20
DEFAULT_CONCURRENCY = 10
MAX_CSV_ROWS = 10000
BATCH_SLEEP_SECONDS = 10

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico'}
MIME_TYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
}

CSV_HEADERS = ['上传时间', '图片ID', '文件路径', '文件名', '文件大小', '状态', 'CDN链接', '错误信息', '耗时(ms)']

CSV_LOCK = threading.Lock()


@dataclass
class UploadResult:
    file_path: str
    file_size: int
    status: str
    cdn_url: str = ""
    error_message: str = ""
    duration_ms: int = 0
    oss_key: str = ""
    image_id: int = 0


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f}GB"


class QingpingBatchUploader:
    def __init__(
        self,
        source_dir: str,
        concurrency: int = DEFAULT_CONCURRENCY,
        batch_size: int = BATCH_SIZE,
        category: str = "未分类",
        tags: Optional[List[str]] = None,
        visibility: str = "public",
        force: bool = False,
    ):
        self.source_dir = Path(source_dir).resolve()
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.category = category
        self.tags: List[str] = tags if tags is not None else []
        self.visibility = visibility
        self.force = force

        self.result_dir = self.source_dir / "result"
        self.cache_dir = self.result_dir / "cache"
        self.csv_file: Path = self.result_dir / "qingping_upload_log.csv"

        self.api_key = os.environ.get("QINGPING_API_KEY")
        if not self.api_key:
            self._print_api_key_help()
            sys.exit(1)

        self.signature_manager = SignatureManager(self.cache_dir)
        self.callback_manager = CallbackManager(self.api_key)
        
        self.uploaded: Dict[str, Dict] = {}
        self.pending_callback: List[Dict] = []
        self.callback_lock = threading.Lock()
        self.stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0}

    def _print_api_key_help(self):
        print("❌ 错误: 未找到认证信息")
        print("\n" + "=" * 70)
        print("🔑 获取 API Key 步骤：")
        print("=" * 70)
        print("\n1. 登录青萍AI平台:")
        print("   https://auth.lusyoe.com/profile")
        print("\n2. 在个人信息页面，滚动到最下面")
        print("\n3. 点击生成或查看 API Key")
        print("\n" + "=" * 70)
        print("⚙️  配置环境变量：")
        print("=" * 70)
        print("\n方法一: 临时配置")
        print("   export QINGPING_API_KEY='your-api-key-here'")
        print("\n方法二: 永久配置")
        print("   echo 'export QINGPING_API_KEY=\"your-api-key-here\"' >> ~/.zshrc")
        print("   source ~/.zshrc")

    def _init_cache(self):
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if self.signature_manager.load_cache():
            remaining = self.signature_manager.get_remaining_time()
            print(f"🔐 使用缓存签名（剩余 {remaining // 60} 分钟）")
        
        self._load_uploaded_from_csv()
        self._init_csv_file()

    def _load_uploaded_from_csv(self):
        if self.force:
            return
        
        csv_files = list(self.result_dir.glob("qingping_upload_log*.csv"))
        
        for csv_file in sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        file_name = row.get('文件名', '')
                        image_id = row.get('图片ID', '')
                        status = row.get('状态', '')
                        cdn_url = row.get('CDN链接', '')
                        
                        if file_name and image_id and status == 'success':
                            self.uploaded[file_name] = {
                                'image_id': int(image_id) if image_id else 0,
                                'cdn_url': cdn_url,
                            }
            except Exception as e:
                print(f"⚠️  加载 CSV 记录失败 {csv_file}: {e}")

    def _init_csv_file(self):
        if self.csv_file.exists():
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                row_count = sum(1 for _ in f) - 1
            
            if row_count >= MAX_CSV_ROWS:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"qingping_upload_log_{timestamp}.csv"
                new_path = self.result_dir / new_name
                self.csv_file.rename(new_path)
                self.csv_file = self.result_dir / "qingping_upload_log.csv"
        else:
            self.csv_file = self.result_dir / "qingping_upload_log.csv"
        
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

    def _get_csv_row_count(self) -> int:
        if not self.csv_file.exists():
            return 0
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f) - 1

    def _rotate_csv_if_needed(self):
        row_count = self._get_csv_row_count()
        if row_count >= MAX_CSV_ROWS:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_name = f"qingping_upload_log_{timestamp}.csv"
            new_path = self.result_dir / new_name
            
            self.csv_file.rename(new_path)
            self.csv_file = self.result_dir / "qingping_upload_log.csv"
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

    def _log_to_csv(self, result: UploadResult):
        file_path = Path(result.file_path)
        file_dir = str(file_path.parent)
        file_name = file_path.name
        
        with CSV_LOCK:
            self._rotate_csv_if_needed()
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    result.image_id if result.image_id else "",
                    file_dir,
                    file_name,
                    format_file_size(result.file_size),
                    result.status,
                    result.cdn_url,
                    result.error_message,
                    result.duration_ms,
                ])

    def _upload_to_oss(self, file_path: Path, signature: Signature) -> str:
        ext = file_path.suffix.lower()
        random_key = uuid.uuid4().hex[:12]
        oss_key = f"{signature.full_path_prefix}{random_key}{ext}"

        with open(file_path, 'rb') as f:
            file_content = f.read()

        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
        body_parts = []

        fields = [
            ('key', oss_key),
            ('policy', signature.policy),
            ('x-oss-signature-version', signature.x_oss_signature_version),
            ('x-oss-credential', signature.x_oss_credential),
            ('x-oss-date', signature.x_oss_date),
            ('x-oss-security-token', signature.security_token),
            ('x-oss-signature', signature.signature),
            ('success_action_status', '200'),
        ]

        for name, value in fields:
            body_parts.append(f'--{boundary}\r\n')
            body_parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
            body_parts.append(f'{value}\r\n')

        body_parts.append(f'--{boundary}\r\n')
        body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n')
        body_parts.append(f'Content-Type: {MIME_TYPES.get(ext, "application/octet-stream")}\r\n\r\n')

        body = ''.join(body_parts).encode('utf-8')
        body += file_content
        body += f'\r\n--{boundary}--\r\n'.encode('utf-8')

        req = request.Request(
            signature.upload_url,
            data=body,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'QingpingImgBed-Skill/1.0',
            },
            method='POST',
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with request.urlopen(req, timeout=120) as response:
                    if response.status == 200:
                        return oss_key
                    raise Exception(f"OSS上传失败: HTTP {response.status}")
            except error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else ""
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"OSS上传失败: HTTP {e.code} - {error_body}")
            except error.URLError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"网络错误: {str(e.reason)}")

        raise Exception("上传失败")

    def _scan_images(self) -> Generator[Path, None, None]:
        for root, dirs, files in os.walk(self.source_dir):
            dirs[:] = [d for d in dirs if d not in ('result', 'cache')]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                if ext in SUPPORTED_EXTENSIONS:
                    yield file_path

    def _upload_single(self, file_path: Path) -> UploadResult:
        start_time = time.time()
        file_size = file_path.stat().st_size
        file_key = file_path.name

        if not self.force and file_key in self.uploaded:
            return UploadResult(
                file_path=str(file_path),
                file_size=file_size,
                status="skipped",
                cdn_url=self.uploaded[file_key].get("cdn_url", ""),
                image_id=self.uploaded[file_key].get("image_id", 0),
            )

        try:
            signature = self.signature_manager.get_signature(file_size)
            oss_key = self._upload_to_oss(file_path, signature)

            duration = int((time.time() - start_time) * 1000)
            
            ext = file_path.suffix.lower()
            image_info = {
                "oss_key": oss_key,
                "filename": file_path.name,
                "file_size": file_size,
                "mime_type": MIME_TYPES.get(ext, "application/octet-stream"),
                "category": self.category,
                "tags": self.tags,
                "visibility": self.visibility,
                "file_key": file_key,
            }

            with self.callback_lock:
                self.pending_callback.append(image_info)

            return UploadResult(
                file_path=str(file_path),
                file_size=file_size,
                status="uploaded",
                duration_ms=duration,
                oss_key=oss_key,
            )

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return UploadResult(
                file_path=str(file_path),
                file_size=file_size,
                status="failed",
                error_message=str(e),
                duration_ms=duration,
            )

    def run(self):
        print("=" * 70)
        print("🚀 青萍图床批量上传工具")
        print("=" * 70)
        print(f"📁 扫描目录: {self.source_dir}")
        print(f"🔄 并发数: {self.concurrency}")
        print(f"📦 批次大小: {self.batch_size}")
        print(f"🏷️  分类: {self.category}")
        if self.tags:
            print(f"🔖 标签: {', '.join(self.tags)}")
        print("=" * 70)

        self._init_cache()

        print("\n📂 扫描图片文件...")
        image_files = list(self._scan_images())
        self.stats["total"] = len(image_files)
        print(f"   找到 {self.stats['total']} 张图片")

        if self.stats["total"] == 0:
            print("\n✨ 没有找到图片文件")
            return

        if self.uploaded:
            print(f"   已上传记录: {len(self.uploaded)} 张")

        print(f"\n⏳ 开始上传 (并发: {self.concurrency})...\n")

        upload_results: Dict[str, UploadResult] = {}
        
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = {executor.submit(self._upload_single, img): img for img in image_files}

            for future in as_completed(futures):
                result = future.result()
                file_key = Path(result.file_path).name
                upload_results[file_key] = result

                if result.status == "uploaded":
                    self.stats["success"] += 1
                    print(f"✅ [{self.stats['success']}/{self.stats['total']}] {Path(result.file_path).name}")
                elif result.status == "skipped":
                    self.stats["skipped"] += 1
                elif result.status == "failed":
                    self.stats["failed"] += 1
                    print(f"❌ {Path(result.file_path).name}: {result.error_message}")

        if self.pending_callback:
            print(f"\n📞 处理剩余 {len(self.pending_callback)} 张图片回调...")
            try:
                callback_result = self.callback_manager.batch_callback(self.pending_callback)
                callback_results = self.callback_manager.process_callback_result(callback_result, self.pending_callback)
                
                for item in callback_results:
                    file_key = item.get("file_key", "")
                    if file_key and file_key in upload_results:
                        upload_results[file_key].image_id = item.get("image_id", 0)
                        upload_results[file_key].cdn_url = item.get("cdn_url", "")
                        upload_results[file_key].status = "success"
                
                self.pending_callback = []
                print(f"⏳ 等待 {BATCH_SLEEP_SECONDS} 秒后继续...")
                time.sleep(BATCH_SLEEP_SECONDS)
            except Exception as e:
                import traceback
                print(f"⚠️  回调失败: {e}")
                traceback.print_exc()

        for result in upload_results.values():
            if result.status == "skipped":
                result.status = "success"
            self._log_to_csv(result)

        print("\n" + "=" * 70)
        print("📊 上传统计")
        print("=" * 70)
        print(f"   总计: {self.stats['total']} 张")
        print(f"   ✅ 成功: {self.stats['success']} 张")
        print(f"   ⏭️  跳过: {self.stats['skipped']} 张")
        print(f"   ❌ 失败: {self.stats['failed']} 张")
        print(f"\n📄 日志文件: {self.csv_file}")
        print("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="青萍图床批量上传工具")
    parser.add_argument("source_dir", help="要上传的图片目录")
    parser.add_argument("--concurrency", "-c", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"并发数，默认 {DEFAULT_CONCURRENCY}")
    parser.add_argument("--batch-size", "-b", type=int, default=BATCH_SIZE,
                        help=f"批次大小，默认 {BATCH_SIZE}")
    parser.add_argument("--category", default="未分类", help="图片分类")
    parser.add_argument("--tags", default="", help="标签（逗号分隔）")
    parser.add_argument("--visibility", default="public", help="可见性")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新上传")

    args = parser.parse_args()

    if not Path(args.source_dir).exists():
        print(f"❌ 错误: 目录不存在 {args.source_dir}")
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    uploader = QingpingBatchUploader(
        source_dir=args.source_dir,
        concurrency=args.concurrency,
        batch_size=args.batch_size,
        category=args.category,
        tags=tags,
        visibility=args.visibility,
        force=args.force,
    )

    uploader.run()


if __name__ == "__main__":
    main()
