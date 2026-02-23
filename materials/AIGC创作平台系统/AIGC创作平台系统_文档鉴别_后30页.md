# AIGC创作平台系统 V1.0

## 软件设计文档（续）

**版本号：** V1.0  
**著作权人：** 南京初鑫信息科技有限公司  

---

# 第N-29页

## 6. API接口设计

### 6.1 接口总览

| 模块 | 接口前缀 | 说明 |
|------|----------|------|
| 认证 | /api/v1/auth | 用户认证相关 |
| 用户 | /api/v1/users | 用户管理相关 |
| 内容 | /api/v1/contents | 内容管理相关 |
| 生成 | /api/v1/generate | AI生成相关 |
| 工作流 | /api/v1/workflows | 工作流管理相关 |
| 资产 | /api/v1/assets | 资产管理相关 |
| 项目 | /api/v1/projects | 项目管理相关 |

### 6.2 认证接口

#### 6.2.1 用户登录

**请求：**
```
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": "uuid",
            "username": "string",
            "nickname": "string",
            "role": "string"
        }
    }
}
```

---

# 第N-28页

#### 6.2.2 刷新令牌

**请求：**
```
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_in": 3600
    }
}
```

#### 6.2.3 用户登出

**请求：**
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**响应：**
```json
{
    "success": true,
    "message": "登出成功"
}
```

### 6.3 内容接口

#### 6.3.1 获取内容列表

**请求：**
```
GET /api/v1/contents?page=1&per_page=20&status=draft&keyword=测试
Authorization: Bearer {access_token}
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |
| content_type | string | 否 | 内容类型筛选 |
| status | string | 否 | 状态筛选 |
| keyword | string | 否 | 关键词搜索 |
| creator_id | string | 否 | 创建者ID筛选 |
| project_id | string | 否 | 项目ID筛选 |

---

# 第N-27页

**响应：**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "title": "文章标题",
                "content_type": "text",
                "status": "draft",
                "summary": "摘要内容...",
                "cover_image": "https://...",
                "tags": ["标签1", "标签2"],
                "creator": {
                    "id": "uuid",
                    "username": "creator",
                    "nickname": "创作者"
                },
                "view_count": 100,
                "like_count": 50,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5
    }
}
```

#### 6.3.2 创建内容

**请求：**
```
POST /api/v1/contents
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "title": "文章标题",
    "content_type": "text",
    "body": "文章内容...",
    "summary": "摘要",
    "tags": ["标签1", "标签2"],
    "project_id": "uuid"
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "title": "文章标题",
        "content_type": "text",
        "status": "draft",
        "body": "文章内容...",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

---

# 第N-26页

#### 6.3.3 获取内容详情

**请求：**
```
GET /api/v1/contents/{content_id}
Authorization: Bearer {access_token}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "title": "文章标题",
        "content_type": "text",
        "status": "draft",
        "body": "文章内容...",
        "summary": "摘要",
        "cover_image": "https://...",
        "tags": ["标签1", "标签2"],
        "prompt": "生成提示词",
        "model_name": "gpt-4",
        "creator": {...},
        "project": {...},
        "view_count": 100,
        "like_count": 50,
        "share_count": 20,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 6.3.4 更新内容

**请求：**
```
PUT /api/v1/contents/{content_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "title": "更新后的标题",
    "body": "更新后的内容",
    "tags": ["新标签"]
}
```

---

# 第N-25页

#### 6.3.5 提交审核

**请求：**
```
POST /api/v1/contents/{content_id}/submit
Authorization: Bearer {access_token}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "status": "pending",
        "message": "已提交审核"
    }
}
```

#### 6.3.6 审核内容

**请求：**
```
POST /api/v1/contents/{content_id}/review
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "approved": true,
    "comment": "审核通过，内容质量良好"
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "status": "approved",
        "reviewer": {...},
        "review_comment": "审核通过，内容质量良好",
        "reviewed_at": "2024-01-01T00:00:00Z"
    }
}
```

---

# 第N-24页

### 6.4 AI生成接口

#### 6.4.1 文本生成

**请求：**
```
POST /api/v1/generate/text
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "prompt": "写一篇关于人工智能的文章",
    "model": "gpt-4",
    "max_tokens": 2048,
    "temperature": 0.7,
    "save_as_content": true,
    "title": "AI文章"
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "content": "生成的文本内容...",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 500,
            "total_tokens": 600
        },
        "model": "gpt-4",
        "content_id": "uuid"
    }
}
```

#### 6.4.2 图像生成

**请求：**
```
POST /api/v1/generate/image
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "prompt": "一只可爱的猫咪在阳光下",
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1
}
```

---

# 第N-23页

**响应：**
```json
{
    "success": true,
    "data": {
        "images": [
            {
                "url": "https://...",
                "revised_prompt": "修订后的提示词..."
            }
        ],
        "model": "dall-e-3"
    }
}
```

#### 6.4.3 批量生成

**请求：**
```
POST /api/v1/generate/batch
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "tasks": [
        {
            "type": "text",
            "prompt": "写一个产品标题",
            "params": {"max_tokens": 100}
        },
        {
            "type": "text",
            "prompt": "写一段产品描述",
            "params": {"max_tokens": 500}
        },
        {
            "type": "image",
            "prompt": "产品展示图",
            "params": {"size": "512x512"}
        }
    ],
    "max_concurrent": 3
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "results": [
            {"success": true, "content": "..."},
            {"success": true, "content": "..."},
            {"success": true, "images": [...]}
        ],
        "total": 3,
        "success_count": 3,
        "fail_count": 0
    }
}
```

---

# 第N-22页

### 6.5 工作流接口

#### 6.5.1 获取工作流列表

**请求：**
```
GET /api/v1/workflows?page=1&per_page=20&status=active
Authorization: Bearer {access_token}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "name": "文章生成工作流",
                "description": "自动生成文章的工作流",
                "status": "active",
                "is_template": false,
                "run_count": 100,
                "success_count": 95,
                "owner": {...},
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 50,
        "page": 1,
        "per_page": 20,
        "pages": 3
    }
}
```

#### 6.5.2 创建工作流

**请求：**
```
POST /api/v1/workflows
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "name": "新工作流",
    "description": "工作流描述",
    "definition": {
        "tasks": [...],
        "connections": [...]
    },
    "variables": {
        "default_model": "gpt-4"
    },
    "is_template": false
}
```

---

# 第N-21页

#### 6.5.3 执行工作流

**请求：**
```
POST /api/v1/workflows/{workflow_id}/execute
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "params": {
        "topic": "人工智能",
        "style": "科普文章"
    }
}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "execution-uuid",
        "workflow_id": "workflow-uuid",
        "status": "pending",
        "params": {
            "topic": "人工智能",
            "style": "科普文章"
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 6.5.4 获取执行状态

**请求：**
```
GET /api/v1/workflows/executions/{execution_id}
Authorization: Bearer {access_token}
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "execution-uuid",
        "workflow_id": "workflow-uuid",
        "status": "completed",
        "params": {...},
        "result": {
            "task_1": {"success": true, "content": "..."},
            "task_2": {"success": true, "content": "..."}
        },
        "started_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:01:00Z",
        "duration_ms": 60000
    }
}
```

---

# 第N-20页

### 6.6 资产接口

#### 6.6.1 上传资产

**请求：**
```
POST /api/v1/assets/upload
Content-Type: multipart/form-data
Authorization: Bearer {access_token}

file: (binary)
name: 资产名称
description: 资产描述
category_id: 1
tags: ["标签1", "标签2"]
```

**响应：**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "资产名称",
        "asset_type": "image",
        "status": "active",
        "file_name": "original.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "width": 1920,
        "height": 1080,
        "thumbnail_path": "/thumbnails/...",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 6.6.2 获取资产列表

**请求：**
```
GET /api/v1/assets?asset_type=image&category_id=1&keyword=产品&page=1
Authorization: Bearer {access_token}
```

---

# 第N-19页

#### 6.6.3 下载资产

**请求：**
```
GET /api/v1/assets/{asset_id}/download
Authorization: Bearer {access_token}
```

**响应：**
```
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Disposition: attachment; filename="asset.jpg"

(binary data)
```

## 7. 部署架构

### 7.1 部署架构图

```
                         ┌─────────────────┐
                         │   负载均衡器    │
                         │   (Nginx/ALB)   │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │  Web服务1   │     │  Web服务2   │     │  Web服务3   │
       │  (Gunicorn) │     │  (Gunicorn) │     │  (Gunicorn) │
       └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       │                          │                          │
       ▼                          ▼                          ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│   MySQL     │            │   Redis     │            │  对象存储   │
│  (主从复制) │            │  (Cluster)  │            │  (MinIO)    │
└─────────────┘            └─────────────┘            └─────────────┘
```

---

# 第N-18页

### 7.2 容器化部署

#### 7.2.1 Docker Compose配置

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_CONFIG=production
      - DATABASE_URL=mysql+pymysql://user:pass@db/aigc
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G

  celery_worker:
    build: .
    command: celery -A app.celery worker -l info
    environment:
      - FLASK_CONFIG=production
      - DATABASE_URL=mysql+pymysql://user:pass@db/aigc
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis
    deploy:
      replicas: 5

  celery_beat:
    build: .
    command: celery -A app.celery beat -l info
    depends_on:
      - redis

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=aigc
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

---

# 第N-17页

### 7.3 Kubernetes部署

#### 7.3.1 Deployment配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aigc-web
  namespace: aigc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aigc-web
  template:
    metadata:
      labels:
        app: aigc-web
    spec:
      containers:
      - name: web
        image: aigc-platform:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_CONFIG
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aigc-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

# 第N-16页

#### 7.3.2 Service配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aigc-web-service
  namespace: aigc
spec:
  type: ClusterIP
  selector:
    app: aigc-web
  ports:
  - port: 80
    targetPort: 5000

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aigc-ingress
  namespace: aigc
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - aigc.example.com
    secretName: aigc-tls
  rules:
  - host: aigc.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aigc-web-service
            port:
              number: 80
```

---

# 第N-15页

## 8. 测试报告

### 8.1 测试概述

本测试报告记录了AIGC创作平台系统V1.0版本的测试执行情况和结果。测试覆盖了功能测试、接口测试、性能测试和安全测试。

### 8.2 测试环境

| 项目 | 配置 |
|------|------|
| 服务器 | 阿里云ECS 4核8G |
| 操作系统 | CentOS 7.9 |
| Python版本 | Python 3.10.12 |
| 数据库 | MySQL 8.0.32 |
| 缓存 | Redis 7.0.11 |

### 8.3 功能测试结果

#### 8.3.1 用户管理模块

| 测试用例 | 测试内容 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|----------|------|
| TC-UM-001 | 用户注册 | 成功创建用户 | 成功创建用户 | 通过 |
| TC-UM-002 | 用户登录 | 返回有效token | 返回有效token | 通过 |
| TC-UM-003 | 密码错误登录 | 返回401错误 | 返回401错误 | 通过 |
| TC-UM-004 | 修改密码 | 密码更新成功 | 密码更新成功 | 通过 |
| TC-UM-005 | 获取用户信息 | 返回用户详情 | 返回用户详情 | 通过 |
| TC-UM-006 | 更新用户信息 | 信息更新成功 | 信息更新成功 | 通过 |
| TC-UM-007 | 角色权限验证 | 无权限返回403 | 无权限返回403 | 通过 |

---

# 第N-14页

#### 8.3.2 内容管理模块

| 测试用例 | 测试内容 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|----------|------|
| TC-CM-001 | 创建文本内容 | 内容创建成功 | 内容创建成功 | 通过 |
| TC-CM-002 | 创建图像内容 | 内容创建成功 | 内容创建成功 | 通过 |
| TC-CM-003 | 更新内容 | 内容更新成功 | 内容更新成功 | 通过 |
| TC-CM-004 | 删除内容 | 内容删除成功 | 内容删除成功 | 通过 |
| TC-CM-005 | 内容列表查询 | 返回分页数据 | 返回分页数据 | 通过 |
| TC-CM-006 | 关键词搜索 | 返回匹配结果 | 返回匹配结果 | 通过 |
| TC-CM-007 | 提交审核 | 状态变更为pending | 状态变更为pending | 通过 |
| TC-CM-008 | 审核通过 | 状态变更为approved | 状态变更为approved | 通过 |
| TC-CM-009 | 审核驳回 | 状态变更为rejected | 状态变更为rejected | 通过 |
| TC-CM-010 | 内容发布 | 状态变更为published | 状态变更为published | 通过 |
| TC-CM-011 | 版本创建 | 版本记录创建成功 | 版本记录创建成功 | 通过 |
| TC-CM-012 | 版本回退 | 内容恢复到指定版本 | 内容恢复到指定版本 | 通过 |

#### 8.3.3 AI生成模块

| 测试用例 | 测试内容 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|----------|------|
| TC-AI-001 | 文本生成 | 返回生成文本 | 返回生成文本 | 通过 |
| TC-AI-002 | 图像生成 | 返回图像URL | 返回图像URL | 通过 |
| TC-AI-003 | 批量生成 | 所有任务执行完成 | 所有任务执行完成 | 通过 |
| TC-AI-004 | 生成参数验证 | 参数错误返回400 | 参数错误返回400 | 通过 |
| TC-AI-005 | 生成结果保存 | 保存为内容成功 | 保存为内容成功 | 通过 |

---

# 第N-13页

#### 8.3.4 工作流模块

| 测试用例 | 测试内容 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|----------|------|
| TC-WF-001 | 创建工作流 | 工作流创建成功 | 工作流创建成功 | 通过 |
| TC-WF-002 | 更新工作流定义 | 定义更新成功 | 定义更新成功 | 通过 |
| TC-WF-003 | 激活工作流 | 状态变更为active | 状态变更为active | 通过 |
| TC-WF-004 | 执行工作流 | 任务按顺序执行 | 任务按顺序执行 | 通过 |
| TC-WF-005 | 并行任务执行 | 并行任务同时执行 | 并行任务同时执行 | 通过 |
| TC-WF-006 | 条件分支 | 根据条件选择分支 | 根据条件选择分支 | 通过 |
| TC-WF-007 | 执行失败重试 | 自动重试3次 | 自动重试3次 | 通过 |
| TC-WF-008 | 获取执行状态 | 返回实时状态 | 返回实时状态 | 通过 |

#### 8.3.5 资产管理模块

| 测试用例 | 测试内容 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|----------|------|
| TC-AM-001 | 上传图片 | 上传成功 | 上传成功 | 通过 |
| TC-AM-002 | 上传视频 | 上传成功 | 上传成功 | 通过 |
| TC-AM-003 | 上传文档 | 上传成功 | 上传成功 | 通过 |
| TC-AM-004 | 文件类型验证 | 不支持类型返回400 | 不支持类型返回400 | 通过 |
| TC-AM-005 | 缩略图生成 | 缩略图生成成功 | 缩略图生成成功 | 通过 |
| TC-AM-006 | 资产检索 | 返回匹配结果 | 返回匹配结果 | 通过 |
| TC-AM-007 | 资产下载 | 文件下载成功 | 文件下载成功 | 通过 |
| TC-AM-008 | 资产删除 | 资产删除成功 | 资产删除成功 | 通过 |

---

# 第N-12页

### 8.4 接口测试结果

#### 8.4.1 接口测试统计

| 模块 | 接口数 | 通过数 | 失败数 | 通过率 |
|------|--------|--------|--------|--------|
| 认证模块 | 5 | 5 | 0 | 100% |
| 用户模块 | 8 | 8 | 0 | 100% |
| 内容模块 | 12 | 12 | 0 | 100% |
| 生成模块 | 4 | 4 | 0 | 100% |
| 工作流模块 | 10 | 10 | 0 | 100% |
| 资产模块 | 8 | 8 | 0 | 100% |
| **合计** | **47** | **47** | **0** | **100%** |

#### 8.4.2 接口响应时间

| 接口类型 | 平均响应时间 | P95响应时间 | P99响应时间 |
|----------|--------------|-------------|-------------|
| 查询接口 | 45ms | 120ms | 200ms |
| 创建接口 | 80ms | 180ms | 300ms |
| 更新接口 | 60ms | 150ms | 250ms |
| 删除接口 | 50ms | 100ms | 180ms |
| 文件上传 | 500ms | 1200ms | 2000ms |
| AI生成 | 3000ms | 8000ms | 15000ms |

### 8.5 性能测试结果

#### 8.5.1 并发测试

| 并发用户数 | 平均响应时间 | 吞吐量(QPS) | 错误率 |
|------------|--------------|-------------|--------|
| 50 | 85ms | 580 | 0% |
| 100 | 120ms | 820 | 0% |
| 200 | 180ms | 1100 | 0.1% |
| 500 | 350ms | 1400 | 0.5% |
| 1000 | 680ms | 1450 | 1.2% |

---

# 第N-11页

#### 8.5.2 压力测试

连续24小时压力测试结果：

| 指标 | 结果 |
|------|------|
| 总请求数 | 12,580,000 |
| 成功请求数 | 12,567,420 |
| 失败请求数 | 12,580 |
| 成功率 | 99.9% |
| 平均响应时间 | 156ms |
| 最大响应时间 | 2.8s |
| CPU使用率 | 65-78% |
| 内存使用率 | 72-85% |

### 8.6 安全测试结果

#### 8.6.1 安全漏洞扫描

| 漏洞等级 | 发现数量 | 已修复数量 | 状态 |
|----------|----------|------------|------|
| 高危 | 0 | 0 | - |
| 中危 | 2 | 2 | 已修复 |
| 低危 | 5 | 5 | 已修复 |
| 信息 | 8 | 8 | 已处理 |

#### 8.6.2 安全测试项

| 测试项 | 测试结果 | 状态 |
|--------|----------|------|
| SQL注入 | 未发现漏洞 | 通过 |
| XSS攻击 | 未发现漏洞 | 通过 |
| CSRF攻击 | 已防护 | 通过 |
| 越权访问 | 未发现漏洞 | 通过 |
| 敏感信息泄露 | 未发现问题 | 通过 |
| 弱密码策略 | 已加强 | 通过 |
| Session管理 | 安全 | 通过 |
| 文件上传漏洞 | 未发现漏洞 | 通过 |

---

# 第N-10页

### 8.7 测试结论

经过全面的测试验证，AIGC创作平台系统V1.0各项功能正常，性能指标达到设计要求，安全性符合标准。系统具备上线运行条件。

**测试通过率：** 100%

**主要结论：**

1. 所有功能模块测试通过，功能完整性满足需求
2. 接口响应时间满足性能要求
3. 系统在500并发用户下稳定运行
4. 安全漏洞已全部修复
5. 系统具备生产环境部署条件

## 9. 用户手册

### 9.1 系统登录

#### 9.1.1 登录步骤

1. 打开浏览器，访问系统地址：https://aigc.example.com
2. 在登录页面输入用户名和密码
3. 点击「登录」按钮
4. 登录成功后进入系统首页

#### 9.1.2 忘记密码

1. 在登录页面点击「忘记密码」链接
2. 输入注册邮箱
3. 点击「发送验证码」
4. 输入邮箱收到的验证码
5. 设置新密码并确认
6. 点击「重置密码」完成操作

---

# 第N-9页

### 9.2 内容创作

#### 9.2.1 创建新内容

**步骤：**

1. 点击左侧菜单「内容管理」→「创建内容」
2. 填写内容标题
3. 选择内容类型（文本/图像/视频/音频）
4. 在编辑区域编写或生成内容
5. 添加标签和摘要（可选）
6. 点击「保存草稿」或「提交审核」

#### 9.2.2 使用AI生成内容

**文本生成步骤：**

1. 在内容编辑页面，点击工具栏「AI生成」按钮
2. 在弹出框中输入提示词，描述想要生成的内容
3. 选择生成模型和参数（可选）
4. 点击「生成」按钮
5. 等待生成完成，预览生成结果
6. 点击「使用」将内容插入编辑器，或点击「重新生成」

**图像生成步骤：**

1. 点击工具栏「AI绘图」按钮
2. 输入图像描述提示词
3. 选择图像尺寸和质量
4. 点击「生成」按钮
5. 从生成结果中选择满意的图像
6. 点击「插入」将图像添加到内容中

---

# 第N-8页

#### 9.2.3 内容版本管理

**查看版本历史：**

1. 打开内容编辑页面
2. 点击右上角「版本历史」按钮
3. 在侧边栏查看所有历史版本
4. 点击任意版本查看内容详情

**恢复历史版本：**

1. 在版本历史列表中选择目标版本
2. 点击「恢复此版本」按钮
3. 确认恢复操作
4. 系统自动将当前内容替换为历史版本

### 9.3 工作流使用

#### 9.3.1 创建工作流

1. 进入「工作流」→「我的工作流」
2. 点击「新建工作流」按钮
3. 输入工作流名称和描述
4. 在画布中拖拽添加任务节点
5. 连接节点建立执行顺序
6. 配置各节点参数
7. 点击「保存」

#### 9.3.2 可用任务类型

| 任务类型 | 图标 | 说明 |
|----------|------|------|
| 文本生成 | 📝 | 使用AI生成文本内容 |
| 图像生成 | 🖼️ | 使用AI生成图像 |
| 数据转换 | 🔄 | 转换和处理数据 |
| 条件判断 | ❓ | 根据条件选择分支 |
| HTTP请求 | 🌐 | 调用外部API |
| 内容保存 | 💾 | 保存结果为内容 |
| 通知发送 | 📧 | 发送通知消息 |

---

# 第N-7页

#### 9.3.3 执行工作流

1. 在工作流列表中选择要执行的工作流
2. 点击「执行」按钮
3. 填写执行参数（如有）
4. 点击「开始执行」
5. 在执行监控页面查看实时进度
6. 执行完成后查看结果

### 9.4 资产管理

#### 9.4.1 上传资产

**单文件上传：**

1. 进入「资产库」→「上传资产」
2. 点击上传区域或拖拽文件
3. 填写资产名称和描述
4. 选择分类和添加标签
5. 点击「上传」

**批量上传：**

1. 进入「资产库」→「批量上传」
2. 拖拽多个文件到上传区域
3. 统一设置分类和标签
4. 点击「开始上传」
5. 等待所有文件上传完成

#### 9.4.2 检索资产

1. 在资产库页面使用搜索框输入关键词
2. 使用筛选器按类型、分类、标签筛选
3. 点击资产卡片查看详情
4. 点击「使用」将资产添加到创作内容

---

# 第N-6页

### 9.5 审核发布

#### 9.5.1 提交审核

1. 在内容编辑页面完成内容创作
2. 点击「提交审核」按钮
3. 填写提交说明（可选）
4. 确认提交
5. 等待审核人员审批

#### 9.5.2 审核内容（审核员）

1. 进入「审核中心」→「待审核」
2. 选择需要审核的内容
3. 查看内容详情和系统安全检测结果
4. 点击「通过」或「驳回」
5. 填写审核意见
6. 确认提交审核结果

#### 9.5.3 发布内容

1. 进入已审核通过的内容
2. 点击「发布」按钮
3. 选择发布渠道
4. 设置发布时间（立即或定时）
5. 确认发布

---

# 第N-5页

## 10. 运维手册

### 10.1 系统启动

#### 10.1.1 启动顺序

1. 启动MySQL数据库
2. 启动Redis缓存
3. 启动Celery Worker
4. 启动Celery Beat
5. 启动Web应用

#### 10.1.2 启动命令

```bash
# 启动数据库
systemctl start mysql

# 启动Redis
systemctl start redis

# 启动Celery Worker
celery -A app.celery worker -l info -c 4 &

# 启动Celery Beat
celery -A app.celery beat -l info &

# 启动Web应用
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### 10.2 系统停止

```bash
# 停止Web应用
pkill -f gunicorn

# 停止Celery
pkill -f celery

# 停止Redis
systemctl stop redis

# 停止MySQL
systemctl stop mysql
```

---

# 第N-4页

### 10.3 日志管理

#### 10.3.1 日志位置

| 日志类型 | 路径 |
|----------|------|
| 应用日志 | /var/log/aigc/app.log |
| 访问日志 | /var/log/aigc/access.log |
| 错误日志 | /var/log/aigc/error.log |
| Celery日志 | /var/log/aigc/celery.log |
| Nginx日志 | /var/log/nginx/aigc_*.log |

#### 10.3.2 日志轮转配置

```
# /etc/logrotate.d/aigc
/var/log/aigc/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload aigc
    endscript
}
```

### 10.4 备份恢复

#### 10.4.1 数据库备份

```bash
# 全量备份
mysqldump -u root -p aigc > /backup/aigc_$(date +%Y%m%d).sql

# 增量备份（使用binlog）
mysqlbinlog /var/lib/mysql/mysql-bin.000001 > /backup/binlog_$(date +%Y%m%d).sql
```

#### 10.4.2 数据恢复

```bash
# 恢复全量备份
mysql -u root -p aigc < /backup/aigc_20240101.sql

# 应用增量备份
mysql -u root -p aigc < /backup/binlog_20240101.sql
```

---

# 第N-3页

### 10.5 监控告警

#### 10.5.1 监控指标

| 指标类别 | 监控项 | 告警阈值 |
|----------|--------|----------|
| 系统资源 | CPU使用率 | > 80% |
| 系统资源 | 内存使用率 | > 85% |
| 系统资源 | 磁盘使用率 | > 90% |
| 应用性能 | 请求响应时间 | > 2s |
| 应用性能 | 错误率 | > 1% |
| 数据库 | 连接数 | > 80% |
| 数据库 | 慢查询数 | > 10/min |
| 缓存 | Redis内存使用率 | > 80% |
| 队列 | 任务积压数 | > 1000 |

#### 10.5.2 告警配置

```yaml
# alertmanager配置
groups:
- name: aigc-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率过高"
      
  - alert: HighErrorRate
    expr: error_rate > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "错误率过高"
```

---

# 第N-2页

### 10.6 常见问题处理

#### 10.6.1 服务无法启动

**问题：** Web服务启动失败

**排查步骤：**
1. 检查端口是否被占用：`netstat -tlnp | grep 5000`
2. 检查配置文件是否正确
3. 查看错误日志：`tail -f /var/log/aigc/error.log`
4. 检查数据库连接是否正常

#### 10.6.2 AI生成超时

**问题：** AI生成任务超时失败

**处理方法：**
1. 检查AI服务商API状态
2. 检查网络连接
3. 增加超时时间配置
4. 检查Celery Worker是否正常

#### 10.6.3 文件上传失败

**问题：** 大文件上传失败

**处理方法：**
1. 检查Nginx配置 `client_max_body_size`
2. 检查磁盘空间
3. 检查文件权限
4. 增加上传超时时间

---

# 第N-1页

### 10.7 性能优化

#### 10.7.1 数据库优化

```sql
-- 添加必要索引
CREATE INDEX idx_contents_status ON contents(status);
CREATE INDEX idx_contents_created_at ON contents(created_at);
CREATE INDEX idx_assets_type ON assets(asset_type);

-- 查询优化
ANALYZE TABLE contents;
ANALYZE TABLE assets;
ANALYZE TABLE workflows;
```

#### 10.7.2 缓存优化

```python
# 热点数据缓存
CACHE_CONFIG = {
    'content_list': 300,      # 内容列表缓存5分钟
    'asset_list': 600,        # 资产列表缓存10分钟
    'user_info': 1800,        # 用户信息缓存30分钟
    'workflow_def': 3600,     # 工作流定义缓存1小时
}
```

#### 10.7.3 应用优化

- 启用Gzip压缩
- 静态资源CDN加速
- 数据库连接池配置
- 异步任务合理拆分

---

# 第N页（最后一页）

## 11. 版本更新记录

### V1.0.0 (2024-01-01)

**新增功能：**
- 内容创作与管理功能
- AI文本/图像生成能力
- 可视化工作流编辑器
- 资产库管理功能
- 内容审核发布流程
- 用户权限管理系统

**优化改进：**
- 首次发布，无历史优化项

**修复问题：**
- 首次发布，无历史问题

---

## 附录

### A. 系统配置参数

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| MAX_CONTENT_LENGTH | 100MB | 最大上传文件大小 |
| JWT_ACCESS_TOKEN_EXPIRES | 1h | 访问令牌有效期 |
| JWT_REFRESH_TOKEN_EXPIRES | 30d | 刷新令牌有效期 |
| CELERY_TASK_SOFT_TIME_LIMIT | 300s | 任务软超时 |
| CELERY_TASK_TIME_LIMIT | 600s | 任务硬超时 |
| AI_GENERATION_TIMEOUT | 120s | AI生成超时时间 |

### B. 联系方式

**技术支持：** support@chuxin.com  
**服务热线：** 400-XXX-XXXX  
**官方网站：** https://www.chuxin.com

---

**AIGC创作平台系统 V1.0 文档鉴别材料 后30页 完**

*第N-29页 至 第N页*

