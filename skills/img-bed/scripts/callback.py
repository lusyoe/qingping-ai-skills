#!/usr/bin/env python3
"""
青萍图床回调管理模块
负责批量回调接口调用
"""

import json
import time
from typing import Dict, List, Optional
from urllib import request, error


API_BASE_URL = "https://img.lusyoe.com"


class CallbackManager:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        timeout: int = 60,
    ) -> Dict:
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

    def batch_callback(self, images: List[Dict]) -> Dict:
        if not images:
            return {}

        url = f"{API_BASE_URL}/api/upload/batch-callback"
        headers = {"x-api-key": self.api_key}
        
        callback_images = []
        for info in images:
            callback_images.append({
                "oss_key": info.get("oss_key", ""),
                "filename": info.get("filename", ""),
                "file_size": info.get("file_size", 0),
                "mime_type": info.get("mime_type", ""),
                "category": info.get("category", "未分类"),
                "tags": info.get("tags", []),
                "visibility": info.get("visibility", "public"),
            })
        
        payload = {"images": callback_images}

        print(f"📞 批量回调 ({len(images)} 张图片)...")
        return self._http_request(url, method="POST", headers=headers, data=payload)

    def process_callback_result(self, callback_result: Dict, pending_images: List[Dict]) -> List[Dict]:
        results = []
        
        if not callback_result.get("success"):
            return results
        
        callback_images = callback_result.get("images", [])
        
        for img in callback_images:
            oss_key = img.get("oss_url", "").split(".com/")[-1] if img.get("oss_url") else ""
            cdn_url = img.get("cdn_url", "")
            image_id = img.get("id", 0)
            
            for info in pending_images:
                if info.get("oss_key") == oss_key or oss_key.endswith(info.get("oss_key", "").split("/")[-1]):
                    results.append({
                        "file_key": info.get("file_key", ""),
                        "image_id": image_id,
                        "cdn_url": cdn_url,
                        "oss_key": oss_key,
                    })
                    break
        
        return results
