---
title: 默认模块
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# 默认模块

青萍图床系统后端API接口

Base URLs:

# Authentication

# 1、STS签名

<a id="opIdget_upload_signature_api_sts_upload_signature_post"></a>

## POST 获取临时上传签名（上传第1步-必调）

POST /api/sts/upload_signature

获取 OSS 表单上传签名，前端或外部第三方必调，签名有效期为1小时，可以自己缓存

> Body 请求参数

```json
{
  "path_prefix": "string",
  "file_size": 0
}
```

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|x-api-key|header|string| 否 ||none|
|body|body|[STSRequest](#schemastsrequest)| 否 | Request Data|none|

> 返回示例

> 200 Response

```json
{
  "policy": "string",
  "x_oss_signature_version": "string",
  "x_oss_credential": "string",
  "x_oss_date": "string",
  "signature": "string",
  "host": "string",
  "dir": "string",
  "full_path_prefix": "string",
  "date_path": "string",
  "user_identifier": "string",
  "security_token": "string",
  "upload_url": "string",
  "bucket": "string",
  "endpoint": "string",
  "region": "string",
  "plan_info": {
    "name": "string",
    "type": "string",
    "current_images": 0,
    "remaining_images": 0,
    "current_storage_bytes": 0,
    "remaining_storage_bytes": 0,
    "max_storage_bytes": 0,
    "daily_uploads_today": 0,
    "daily_upload_limit": 0,
    "remaining_daily_uploads": 0
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[STSResponse](#schemastsresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

# 数据模型

<h2 id="tocS_STSRequest">STSRequest</h2>

<a id="schemastsrequest"></a>
<a id="schema_STSRequest"></a>
<a id="tocSstsrequest"></a>
<a id="tocsstsrequest"></a>

```json
{
  "path_prefix": "string",
  "file_size": 0
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|path_prefix|string|true|none||上传的路径前缀，必须为：images/|
|file_size|integer|true|none||上传的文件大小，单位 byte|

<h2 id="tocS_STSResponse">STSResponse</h2>

<a id="schemastsresponse"></a>
<a id="schema_STSResponse"></a>
<a id="tocSstsresponse"></a>
<a id="tocsstsresponse"></a>

```json
{
  "policy": "string",
  "x_oss_signature_version": "string",
  "x_oss_credential": "string",
  "x_oss_date": "string",
  "signature": "string",
  "host": "string",
  "dir": "string",
  "full_path_prefix": "string",
  "date_path": "string",
  "user_identifier": "string",
  "security_token": "string",
  "upload_url": "string",
  "bucket": "string",
  "endpoint": "string",
  "region": "string",
  "plan_info": {
    "name": "string",
    "type": "string",
    "current_images": 0,
    "remaining_images": 0,
    "current_storage_bytes": 0,
    "remaining_storage_bytes": 0,
    "max_storage_bytes": 0,
    "daily_uploads_today": 0,
    "daily_upload_limit": 0,
    "remaining_daily_uploads": 0
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|policy|string|true|none||none|
|x_oss_signature_version|string|true|none||none|
|x_oss_credential|string|true|none||none|
|x_oss_date|string|true|none||none|
|signature|string|true|none||none|
|host|string|true|none||none|
|dir|string|true|none||none|
|full_path_prefix|string|true|none||none|
|date_path|string|true|none||none|
|user_identifier|string|true|none||none|
|security_token|string|true|none||none|
|upload_url|string|true|none||none|
|bucket|string|true|none||none|
|endpoint|string|true|none||none|
|region|string|true|none||none|
|plan_info|object|true|none||none|
|» name|string|true|none||none|
|» type|string|true|none||none|
|» current_images|integer|true|none||none|
|» remaining_images|integer|true|none||none|
|» current_storage_bytes|integer|true|none||none|
|» remaining_storage_bytes|integer|true|none||none|
|» max_storage_bytes|integer|true|none||none|
|» daily_uploads_today|integer|true|none||none|
|» daily_upload_limit|integer|true|none||none|
|» remaining_daily_uploads|integer|true|none||none|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>

<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|Detail|none|

<h2 id="tocS_ValidationError">ValidationError</h2>

<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|loc|[anyOf]|true|none|Location|none|

anyOf

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|string|false|none||none|

or

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|integer|false|none||none|

continued

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|msg|string|true|none|Message|none|
|type|string|true|none|Error Type|none|

