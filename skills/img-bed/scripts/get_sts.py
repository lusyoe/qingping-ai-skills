#!/usr/bin/env python3
"""
青萍图床 STS 签名管理模块
负责签名的获取、缓存和验证
"""

import os
import json
import time
from pathlib import Path
from typing import Optional
from urllib import request, error
from dataclasses import dataclass, field


API_BASE_URL = "https://img.lusyoe.com"
SIGNATURE_EXPIRE_SECONDS = 3600


@dataclass
class Signature:
    policy: str
    x_oss_signature_version: str
    x_oss_credential: str
    x_oss_date: str
    signature: str
    host: str
    dir: str
    full_path_prefix: str
    date_path: str
    user_identifier: str
    security_token: str
    upload_url: str
    bucket: str
    endpoint: str
    region: str
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return time.time() - self.created_at > SIGNATURE_EXPIRE_SECONDS - 300


class SignatureManager:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.signature_file = cache_dir / "signature.json"
        self.api_key = os.environ.get("QINGPING_API_KEY")
        self.signature: Optional[Signature] = None

    def load_cache(self) -> bool:
        if not self.signature_file.exists():
            return False
        
        try:
            with open(self.signature_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.signature = Signature(
                policy=data['policy'],
                x_oss_signature_version=data['x_oss_signature_version'],
                x_oss_credential=data['x_oss_credential'],
                x_oss_date=data['x_oss_date'],
                signature=data['signature'],
                host=data['host'],
                dir=data['dir'],
                full_path_prefix=data['full_path_prefix'],
                date_path=data['date_path'],
                user_identifier=data['user_identifier'],
                security_token=data['security_token'],
                upload_url=data['upload_url'],
                bucket=data['bucket'],
                endpoint=data['endpoint'],
                region=data['region'],
                created_at=data.get('created_at', time.time()),
            )
            
            if self.signature.is_expired():
                self.signature = None
                return False
            
            return True
        except Exception as e:
            print(f"⚠️  加载签名缓存失败: {e}")
            self.signature = None
            return False

    def save_cache(self):
        if not self.signature:
            return
        
        try:
            data = {
                'policy': self.signature.policy,
                'x_oss_signature_version': self.signature.x_oss_signature_version,
                'x_oss_credential': self.signature.x_oss_credential,
                'x_oss_date': self.signature.x_oss_date,
                'signature': self.signature.signature,
                'host': self.signature.host,
                'dir': self.signature.dir,
                'full_path_prefix': self.signature.full_path_prefix,
                'date_path': self.signature.date_path,
                'user_identifier': self.signature.user_identifier,
                'security_token': self.signature.security_token,
                'upload_url': self.signature.upload_url,
                'bucket': self.signature.bucket,
                'endpoint': self.signature.endpoint,
                'region': self.signature.region,
                'created_at': self.signature.created_at,
            }
            
            with open(self.signature_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存签名缓存失败: {e}")

    def _http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: int = 60,
    ) -> dict:
        req_headers = headers or {}
        req_headers["User-Agent"] = "QingpingImgBed-Skill/1.0"

        req_data = None
        if data:
            req_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        req = request.Request(url, data=req_data, headers=req_headers, method=method)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with request.urlopen(req, timeout=timeout) as response:
                    response_body = response.read().decode("utf-8")
                    return json.loads(response_body)
            except error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else ""
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"HTTP {e.code}: {error_body}")
            except error.URLError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"网络错误: {str(e.reason)}")

        raise Exception("请求失败")

    def get_signature(self, file_size: int) -> Signature:
        if self.signature and not self.signature.is_expired():
            return self.signature

        url = f"{API_BASE_URL}/api/sts/upload_signature"
        headers = {"x-api-key": self.api_key}
        payload = {"path_prefix": "images/", "file_size": file_size}

        print("🔐 获取上传签名...")
        data = self._http_request(url, method="POST", headers=headers, data=payload)

        self.signature = Signature(
            policy=data['policy'],
            x_oss_signature_version=data['x_oss_signature_version'],
            x_oss_credential=data['x_oss_credential'],
            x_oss_date=data['x_oss_date'],
            signature=data['signature'],
            host=data['host'],
            dir=data['dir'],
            full_path_prefix=data['full_path_prefix'],
            date_path=data['date_path'],
            user_identifier=data['user_identifier'],
            security_token=data['security_token'],
            upload_url=data['upload_url'],
            bucket=data['bucket'],
            endpoint=data['endpoint'],
            region=data['region'],
        )

        self.save_cache()
        return self.signature

    def get_remaining_time(self) -> int:
        if not self.signature:
            return 0
        return int(SIGNATURE_EXPIRE_SECONDS - (time.time() - self.signature.created_at))
