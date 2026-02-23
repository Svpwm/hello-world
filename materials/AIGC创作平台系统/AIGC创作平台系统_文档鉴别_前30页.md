# AIGC创作平台系统 V1.0

## 软件设计文档

**版本号：** V1.0  
**著作权人：** 南京初鑫信息科技有限公司  
**编制日期：** 2024年

---

# 目录

1. 概述
   1.1 项目背景
   1.2 开发目的
   1.3 适用范围
   1.4 术语定义
2. 需求分析
   2.1 业务需求
   2.2 功能需求
   2.3 非功能需求
   2.4 用户角色定义
3. 系统架构设计
   3.1 总体架构
   3.2 技术选型
   3.3 模块划分
   3.4 接口设计
4. 数据库设计
   4.1 数据库选型
   4.2 ER图
   4.3 数据表设计
5. 详细设计
   5.1 内容管理模块
   5.2 AI生成模块
   5.3 工作流引擎模块
   5.4 资产管理模块
6. API接口设计
7. 部署架构

---

# 第1页

## 1. 概述

### 1.1 项目背景

随着人工智能技术的快速发展，特别是大语言模型（LLM）和生成式AI技术的突破性进展，AIGC（AI Generated Content，人工智能生成内容）已成为内容产业变革的核心驱动力。企业在内容生产过程中面临着效率低、成本高、创意瓶颈等挑战，亟需一套完整的AIGC解决方案来提升内容生产能力。

本项目旨在构建一个企业级AIGC创作平台系统，整合多种AI生成能力，提供统一的内容创作、管理和发布工作流，帮助企业实现内容生产的智能化升级。

### 1.2 开发目的

AIGC创作平台系统的开发目标包括：

1. **提效降本**：通过AI辅助创作，大幅提升内容生产效率，降低人力成本
2. **能力整合**：整合文本、图像、音视频等多模态生成能力，提供一站式创作体验
3. **流程规范**：建立标准化的内容创作流程，支持多人协作与审核发布
4. **资产沉淀**：统一管理创作素材与内容资产，支持复用与追溯
5. **合规安全**：内置内容安全审核机制，确保生成内容符合法规要求

### 1.3 适用范围

本系统适用于以下场景和用户群体：

- **媒体与出版行业**：新闻资讯、专题内容、多媒体报道的智能生产
- **广告营销领域**：营销文案、创意图片、短视频广告的批量生成
- **教育培训机构**：课程内容、教学素材、测试题目的自动生成
- **电商内容运营**：商品描述、推广文案、营销海报的规模化生产
- **企业品牌部门**：品牌内容、社交媒体运营、内部传播物料的制作

---

# 第2页

### 1.4 术语定义

| 术语 | 英文 | 定义 |
|------|------|------|
| AIGC | AI Generated Content | 人工智能生成内容，指利用AI技术自动生成文本、图像、音视频等内容 |
| LLM | Large Language Model | 大语言模型，如GPT-4、Claude等，用于文本生成与理解 |
| Prompt | - | 提示词，用于指导AI模型生成特定内容的输入指令 |
| 工作流 | Workflow | 内容创作过程中的一系列有序任务步骤 |
| 素材 | Asset | 创作过程中使用的图片、视频、音频等资源文件 |
| 模板 | Template | 可复用的提示词或工作流配置 |
| Token | - | 文本处理的基本单位，用于计算模型输入输出量 |

## 2. 需求分析

### 2.1 业务需求

#### 2.1.1 业务目标

1. 构建企业级AIGC创作平台，支持多团队、多项目并行创作
2. 实现内容创作全流程线上化，包括创意、生成、编辑、审核、发布
3. 建立内容资产库，实现素材与内容的统一管理和复用
4. 提供可配置的工作流引擎，支持定制化创作流程
5. 确保内容合规，集成内容安全审核能力

#### 2.1.2 业务流程

典型的内容创作业务流程如下：

```
需求输入 → 创意策划 → AI生成 → 人工编辑 → 审核把关 → 内容发布 → 效果追踪
```

平台需要支持上述流程的全链路管理，并提供各环节的效率工具。

---

# 第3页

### 2.2 功能需求

#### 2.2.1 内容创作模块

| 需求编号 | 功能名称 | 功能描述 | 优先级 |
|----------|----------|----------|--------|
| F-CC-001 | 文本生成 | 基于提示词生成文章、文案、脚本等文本内容 | P0 |
| F-CC-002 | 图像生成 | 基于文字描述生成图片、海报、插画等视觉内容 | P0 |
| F-CC-003 | 内容编辑 | 提供富文本编辑器，支持对生成内容进行修改完善 | P0 |
| F-CC-004 | 版本管理 | 记录内容修改历史，支持版本对比和回退 | P1 |
| F-CC-005 | 多模态混排 | 支持图文混排、音视频嵌入等复合内容编辑 | P1 |
| F-CC-006 | 模板管理 | 管理提示词模板，支持参数化配置 | P1 |
| F-CC-007 | 批量生成 | 支持批量提交生成任务，提高生产效率 | P2 |

#### 2.2.2 工作流管理模块

| 需求编号 | 功能名称 | 功能描述 | 优先级 |
|----------|----------|----------|--------|
| F-WF-001 | 工作流设计 | 可视化工作流编辑器，支持拖拽式流程设计 | P0 |
| F-WF-002 | 任务编排 | 支持串行、并行、条件分支等任务编排模式 | P0 |
| F-WF-003 | 工作流执行 | 一键执行工作流，自动完成多步骤任务 | P0 |
| F-WF-004 | 执行监控 | 实时展示工作流执行状态和进度 | P1 |
| F-WF-005 | 工作流模板 | 支持将工作流保存为模板供复用 | P1 |
| F-WF-006 | 定时触发 | 支持定时自动执行工作流 | P2 |

---

# 第4页

#### 2.2.3 资产管理模块

| 需求编号 | 功能名称 | 功能描述 | 优先级 |
|----------|----------|----------|--------|
| F-AM-001 | 文件上传 | 支持图片、视频、音频、文档等多类型文件上传 | P0 |
| F-AM-002 | 资产分类 | 支持多级分类目录管理资产 | P0 |
| F-AM-003 | 标签管理 | 支持为资产添加标签，便于检索 | P1 |
| F-AM-004 | 资产检索 | 支持按名称、标签、类型等多维度检索 | P0 |
| F-AM-005 | 缩略图预览 | 自动生成缩略图，支持快速预览 | P1 |
| F-AM-006 | 使用统计 | 统计资产使用次数和引用关系 | P2 |
| F-AM-007 | 版权管理 | 记录资产版权信息和授权范围 | P2 |

#### 2.2.4 审核发布模块

| 需求编号 | 功能名称 | 功能描述 | 优先级 |
|----------|----------|----------|--------|
| F-AP-001 | 提交审核 | 内容创作完成后提交审核 | P0 |
| F-AP-002 | 审核处理 | 审核人员审批通过或驳回 | P0 |
| F-AP-003 | 内容安全 | 集成敏感内容检测，自动标记风险内容 | P0 |
| F-AP-004 | 多级审核 | 支持配置多级审核流程 | P1 |
| F-AP-005 | 内容发布 | 审核通过后发布到指定渠道 | P0 |
| F-AP-006 | 发布渠道 | 支持配置多种发布渠道（网站、公众号等） | P1 |

---

# 第5页

#### 2.2.5 用户与权限模块

| 需求编号 | 功能名称 | 功能描述 | 优先级 |
|----------|----------|----------|--------|
| F-UP-001 | 用户注册登录 | 支持账号密码登录，第三方OAuth登录 | P0 |
| F-UP-002 | 角色管理 | 定义系统角色，如管理员、编辑、审核员等 | P0 |
| F-UP-003 | 权限配置 | 为角色分配功能权限和数据权限 | P0 |
| F-UP-004 | 部门管理 | 支持组织架构管理，按部门分配资源 | P1 |
| F-UP-005 | 操作日志 | 记录用户关键操作，支持审计追溯 | P1 |

### 2.3 非功能需求

#### 2.3.1 性能需求

| 指标 | 要求 |
|------|------|
| 页面响应时间 | 95%请求响应时间 < 2秒 |
| API响应时间 | 95%接口响应时间 < 500ms（不含AI生成） |
| 并发用户数 | 支持500+并发用户在线 |
| 文件上传 | 单文件最大100MB，批量上传最大1GB |
| AI生成队列 | 支持1000+任务排队，按优先级调度 |

#### 2.3.2 可用性需求

| 指标 | 要求 |
|------|------|
| 系统可用性 | SLA ≥ 99.9% |
| 数据备份 | 每日全量备份，实时增量备份 |
| 故障恢复 | RTO < 4小时，RPO < 1小时 |

---

# 第6页

#### 2.3.3 安全需求

| 类别 | 要求 |
|------|------|
| 身份认证 | 支持多因素认证，密码强度策略 |
| 访问控制 | 基于RBAC的细粒度权限控制 |
| 数据传输 | 全站HTTPS，敏感数据加密传输 |
| 数据存储 | 敏感信息加密存储，定期安全审计 |
| 内容安全 | AI生成内容实时审核，敏感词过滤 |

### 2.4 用户角色定义

#### 2.4.1 系统管理员

- **职责**：系统配置、用户管理、权限分配
- **权限**：全部功能权限
- **典型操作**：创建用户、配置角色权限、系统参数设置

#### 2.4.2 内容编辑

- **职责**：内容创作、编辑修改、素材管理
- **权限**：内容创作、资产管理、提交审核
- **典型操作**：AI生成内容、编辑内容、上传素材、提交审核

#### 2.4.3 内容审核员

- **职责**：内容审核、质量把关、发布管理
- **权限**：审核内容、发布内容、查看统计
- **典型操作**：审批内容、驳回修改、发布内容

#### 2.4.4 项目管理员

- **职责**：项目管理、工作流配置、团队协作
- **权限**：项目设置、工作流管理、成员管理
- **典型操作**：创建项目、配置工作流、分配任务

---

# 第7页

## 3. 系统架构设计

### 3.1 总体架构

AIGC创作平台系统采用分层架构设计，从上到下分为展示层、网关层、服务层、数据层和基础设施层。

```
┌─────────────────────────────────────────────────────────────┐
│                        展示层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Web端     │  │   移动端    │  │   开放API   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        网关层                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Gateway (认证、限流、路由、日志)                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        服务层                                │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ 内容服务  │ │ 工作流服务│ │ 资产服务  │ │ 用户服务  │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ AI服务    │ │ 审核服务  │ │ 消息服务  │ │ 统计服务  │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        数据层                                │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │  MySQL    │ │  Redis    │ │ 对象存储  │ │ 搜索引擎  │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

# 第8页

### 3.2 技术选型

#### 3.2.1 后端技术栈

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 开发语言 | Python 3.10+ | 主力开发语言，AI生态丰富 |
| Web框架 | Flask 2.x | 轻量级Web框架，灵活可扩展 |
| ORM | SQLAlchemy | 成熟的Python ORM框架 |
| 任务队列 | Celery | 分布式任务队列，处理异步任务 |
| 缓存 | Redis | 高性能缓存和消息队列 |
| 数据库 | MySQL 8.0 | 关系型数据库，存储业务数据 |
| 对象存储 | MinIO/S3 | 存储文件资产 |
| API文档 | Swagger/OpenAPI | 自动生成API文档 |

#### 3.2.2 AI能力集成

| 能力 | 提供商 | 说明 |
|------|--------|------|
| 文本生成 | OpenAI GPT-4 | 高质量文本生成 |
| 图像生成 | DALL-E 3 | 文生图能力 |
| 图像生成 | Stable Diffusion | 开源图像生成模型 |
| 内容安全 | 自研模型 | 敏感内容检测 |

#### 3.2.3 前端技术栈

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | Vue.js 3 | 渐进式JavaScript框架 |
| UI组件 | Element Plus | 企业级UI组件库 |
| 状态管理 | Pinia | Vue3官方推荐状态管理 |
| HTTP客户端 | Axios | HTTP请求库 |
| 富文本编辑器 | TipTap | 可扩展的富文本编辑器 |

---

# 第9页

### 3.3 模块划分

系统按业务领域划分为以下核心模块：

#### 3.3.1 模块架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      AIGC创作平台系统                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │             │  │             │  │             │             │
│  │  内容管理   │  │  工作流引擎 │  │  资产管理   │             │
│  │             │  │             │  │             │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                    │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐             │
│  │             │  │             │  │             │             │
│  │  AI生成服务 │  │  审核服务   │  │  用户权限   │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                       公共服务层                         │   │
│  │  文件存储 │ 消息队列 │ 缓存服务 │ 日志服务 │ 监控告警   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 模块职责说明

| 模块 | 职责 |
|------|------|
| 内容管理 | 内容的创建、编辑、版本管理、生命周期管理 |
| 工作流引擎 | 工作流定义、执行、监控、调度 |
| 资产管理 | 文件上传、分类、检索、版权管理 |
| AI生成服务 | 对接AI模型，执行生成任务，结果处理 |
| 审核服务 | 内容审核流程、内容安全检测 |
| 用户权限 | 用户管理、角色管理、权限控制 |

---

# 第10页

### 3.4 接口设计

#### 3.4.1 接口设计原则

1. **RESTful风格**：遵循REST架构风格，使用HTTP方法表示操作类型
2. **统一响应格式**：所有接口返回统一的JSON格式
3. **版本控制**：接口URL包含版本号，如 `/api/v1/`
4. **错误码规范**：定义统一的错误码体系
5. **幂等性**：关键操作接口保证幂等性

#### 3.4.2 统一响应格式

**成功响应：**

```json
{
    "success": true,
    "data": {
        // 业务数据
    },
    "message": "操作成功"
}
```

**失败响应：**

```json
{
    "success": false,
    "error": "错误描述",
    "code": "ERROR_CODE",
    "details": {
        // 错误详情（可选）
    }
}
```

#### 3.4.3 分页响应格式

```json
{
    "success": true,
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5
    }
}
```

---

# 第11页

#### 3.4.4 错误码定义

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| SUCCESS | 200 | 成功 |
| BAD_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMITED | 429 | 请求过于频繁 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| GENERATION_FAILED | 500 | AI生成失败 |
| CONTENT_UNSAFE | 400 | 内容安全检测不通过 |

## 4. 数据库设计

### 4.1 数据库选型

本系统采用MySQL 8.0作为主数据库，选型理由如下：

1. **成熟稳定**：MySQL是业界最广泛使用的开源关系型数据库
2. **功能丰富**：支持事务、索引、存储过程等完整特性
3. **性能优秀**：经过充分优化，满足中大型应用需求
4. **生态完善**：丰富的管理工具和监控方案

同时使用Redis作为缓存层和消息队列：

1. **缓存热点数据**：减轻数据库压力
2. **会话管理**：存储用户会话信息
3. **任务队列**：Celery任务队列后端
4. **限流计数**：API限流计数器

---

# 第12页

### 4.2 ER图

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   contents   │       │   projects   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │──┐    │ id           │   ┌───│ id           │
│ username     │  │    │ title        │   │   │ name         │
│ email        │  │    │ body         │   │   │ description  │
│ password_hash│  │    │ status       │   │   │ owner_id     │
│ role_id      │  ├────│ creator_id   │   │   │ created_at   │
│ department_id│  │    │ project_id   │───┘   └──────────────┘
│ created_at   │  │    │ created_at   │
└──────────────┘  │    └──────┬───────┘
       │          │           │
       │          │    ┌──────┴───────┐
       │          │    │  content_    │
┌──────┴──────┐   │    │  versions    │
│   roles     │   │    ├──────────────┤
├─────────────┤   │    │ id           │
│ id          │   │    │ content_id   │
│ name        │   │    │ version_num  │
│ permissions │   │    │ body         │
└─────────────┘   │    │ created_at   │
                  │    └──────────────┘
┌─────────────┐   │
│ departments │   │    ┌──────────────┐
├─────────────┤   │    │   assets     │
│ id          │   │    ├──────────────┤
│ name        │   │    │ id           │
│ parent_id   │   └────│ uploader_id  │
│ manager_id  │        │ name         │
└─────────────┘        │ file_path    │
                       │ asset_type   │
┌─────────────┐        │ created_at   │
│  workflows  │        └──────────────┘
├─────────────┤
│ id          │        ┌──────────────┐
│ name        │        │  workflow_   │
│ owner_id    │───────│  executions  │
│ definition  │        ├──────────────┤
│ status      │        │ id           │
│ created_at  │        │ workflow_id  │
└─────────────┘        │ status       │
                       │ started_at   │
                       └──────────────┘
```

---

# 第13页

### 4.3 数据表设计

#### 4.3.1 用户表 (users)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 用户ID，UUID格式 |
| username | VARCHAR(64) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(128) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(256) | NOT NULL | 密码哈希 |
| nickname | VARCHAR(64) | - | 昵称 |
| avatar_url | VARCHAR(512) | - | 头像URL |
| phone | VARCHAR(20) | - | 手机号 |
| role_id | INT | FOREIGN KEY | 角色ID |
| department_id | INT | FOREIGN KEY | 部门ID |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| is_verified | BOOLEAN | DEFAULT FALSE | 是否已验证 |
| last_login_at | DATETIME | - | 最后登录时间 |
| last_login_ip | VARCHAR(64) | - | 最后登录IP |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

**索引：**
- PRIMARY KEY (id)
- UNIQUE INDEX idx_username (username)
- UNIQUE INDEX idx_email (email)
- INDEX idx_role_id (role_id)
- INDEX idx_department_id (department_id)

---

# 第14页

#### 4.3.2 角色表 (roles)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 角色ID |
| name | VARCHAR(64) | UNIQUE, NOT NULL | 角色名称 |
| description | VARCHAR(256) | - | 角色描述 |
| permissions | JSON | DEFAULT '{}' | 权限配置 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

**权限配置示例：**

```json
{
    "content.create": true,
    "content.edit": true,
    "content.delete": false,
    "content.review": false,
    "content.publish": false,
    "workflow.create": true,
    "workflow.execute": true,
    "asset.upload": true,
    "asset.delete": false,
    "user.manage": false
}
```

#### 4.3.3 部门表 (departments)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 部门ID |
| name | VARCHAR(64) | NOT NULL | 部门名称 |
| code | VARCHAR(32) | UNIQUE | 部门编码 |
| parent_id | INT | FOREIGN KEY | 父部门ID |
| manager_id | VARCHAR(36) | FOREIGN KEY | 部门负责人ID |
| description | VARCHAR(256) | - | 部门描述 |
| sort_order | INT | DEFAULT 0 | 排序序号 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

---

# 第15页

#### 4.3.4 内容表 (contents)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 内容ID |
| title | VARCHAR(256) | NOT NULL | 标题 |
| content_type | ENUM | NOT NULL | 内容类型 |
| status | ENUM | DEFAULT 'draft' | 内容状态 |
| body | LONGTEXT | - | 内容正文 |
| summary | VARCHAR(512) | - | 摘要 |
| cover_image | VARCHAR(512) | - | 封面图URL |
| tags | JSON | DEFAULT '[]' | 标签列表 |
| metadata | JSON | DEFAULT '{}' | 元数据 |
| prompt | TEXT | - | 生成提示词 |
| model_name | VARCHAR(64) | - | 使用的模型名称 |
| generation_params | JSON | DEFAULT '{}' | 生成参数 |
| creator_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 创建者ID |
| project_id | VARCHAR(36) | FOREIGN KEY | 所属项目ID |
| workflow_id | VARCHAR(36) | FOREIGN KEY | 关联工作流ID |
| reviewer_id | VARCHAR(36) | FOREIGN KEY | 审核人ID |
| review_comment | TEXT | - | 审核意见 |
| reviewed_at | DATETIME | - | 审核时间 |
| published_at | DATETIME | - | 发布时间 |
| publish_channels | JSON | DEFAULT '[]' | 发布渠道 |
| view_count | INT | DEFAULT 0 | 浏览次数 |
| like_count | INT | DEFAULT 0 | 点赞次数 |
| share_count | INT | DEFAULT 0 | 分享次数 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

**内容类型枚举 (content_type)：**
- text: 文本
- image: 图像
- video: 视频
- audio: 音频
- mixed: 混合

**内容状态枚举 (status)：**
- draft: 草稿
- pending: 待审核
- approved: 审核通过
- rejected: 审核驳回
- published: 已发布
- archived: 已归档

---

# 第16页

#### 4.3.5 内容版本表 (content_versions)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 版本ID |
| content_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 内容ID |
| version_number | INT | NOT NULL | 版本号 |
| title | VARCHAR(256) | - | 标题 |
| body | LONGTEXT | - | 内容正文 |
| metadata | JSON | DEFAULT '{}' | 元数据 |
| comment | VARCHAR(256) | - | 版本说明 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| created_by | VARCHAR(36) | FOREIGN KEY | 创建者ID |

**索引：**
- PRIMARY KEY (id)
- INDEX idx_content_id (content_id)
- UNIQUE INDEX idx_content_version (content_id, version_number)

#### 4.3.6 工作流表 (workflows)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 工作流ID |
| name | VARCHAR(128) | NOT NULL | 工作流名称 |
| description | TEXT | - | 描述 |
| status | ENUM | DEFAULT 'draft' | 状态 |
| definition | JSON | DEFAULT '{}' | 工作流定义 |
| variables | JSON | DEFAULT '{}' | 变量定义 |
| is_template | BOOLEAN | DEFAULT FALSE | 是否为模板 |
| template_id | VARCHAR(36) | FOREIGN KEY | 源模板ID |
| owner_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 所有者ID |
| project_id | VARCHAR(36) | FOREIGN KEY | 所属项目ID |
| run_count | INT | DEFAULT 0 | 执行次数 |
| success_count | INT | DEFAULT 0 | 成功次数 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

---

# 第17页

#### 4.3.7 工作流任务表 (workflow_tasks)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 任务ID |
| workflow_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 工作流ID |
| name | VARCHAR(128) | NOT NULL | 任务名称 |
| task_type | VARCHAR(64) | NOT NULL | 任务类型 |
| config | JSON | DEFAULT '{}' | 任务配置 |
| position | JSON | DEFAULT '{}' | 画布位置 |
| sort_order | INT | DEFAULT 0 | 排序序号 |
| inputs | JSON | DEFAULT '[]' | 输入定义 |
| outputs | JSON | DEFAULT '[]' | 输出定义 |
| condition | TEXT | - | 条件表达式 |
| next_tasks | JSON | DEFAULT '[]' | 后续任务ID |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

**任务类型 (task_type)：**
- text_generation: 文本生成
- image_generation: 图像生成
- data_transform: 数据转换
- condition: 条件判断
- http_request: HTTP请求
- content_save: 内容保存
- notification: 通知发送

#### 4.3.8 工作流执行记录表 (workflow_executions)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 执行ID |
| workflow_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 工作流ID |
| status | ENUM | DEFAULT 'pending' | 执行状态 |
| params | JSON | DEFAULT '{}' | 执行参数 |
| result | JSON | DEFAULT '{}' | 执行结果 |
| error_message | TEXT | - | 错误信息 |
| started_at | DATETIME | - | 开始时间 |
| completed_at | DATETIME | - | 完成时间 |
| duration_ms | INT | - | 执行时长(ms) |
| triggered_by | VARCHAR(36) | FOREIGN KEY | 触发者ID |
| trigger_type | VARCHAR(32) | DEFAULT 'manual' | 触发类型 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

---

# 第18页

#### 4.3.9 资产表 (assets)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 资产ID |
| name | VARCHAR(256) | NOT NULL | 资产名称 |
| description | TEXT | - | 描述 |
| asset_type | ENUM | DEFAULT 'other' | 资产类型 |
| status | ENUM | DEFAULT 'uploading' | 状态 |
| file_path | VARCHAR(512) | NOT NULL | 文件路径 |
| file_name | VARCHAR(256) | - | 原始文件名 |
| file_size | BIGINT | - | 文件大小(字节) |
| mime_type | VARCHAR(128) | - | MIME类型 |
| file_hash | VARCHAR(64) | INDEX | 文件哈希 |
| width | INT | - | 宽度(像素) |
| height | INT | - | 高度(像素) |
| duration | FLOAT | - | 时长(秒) |
| thumbnail_path | VARCHAR(512) | - | 缩略图路径 |
| preview_path | VARCHAR(512) | - | 预览图路径 |
| tags | JSON | DEFAULT '[]' | 标签 |
| category_id | INT | FOREIGN KEY | 分类ID |
| use_count | INT | DEFAULT 0 | 使用次数 |
| download_count | INT | DEFAULT 0 | 下载次数 |
| copyright_info | JSON | DEFAULT '{}' | 版权信息 |
| license_type | VARCHAR(64) | - | 授权类型 |
| uploader_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 上传者ID |
| project_id | VARCHAR(36) | FOREIGN KEY | 所属项目ID |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

**资产类型枚举 (asset_type)：**
- image: 图片
- video: 视频
- audio: 音频
- document: 文档
- template: 模板
- model: 模型
- other: 其他

---

# 第19页

#### 4.3.10 资产分类表 (asset_categories)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 分类ID |
| name | VARCHAR(64) | NOT NULL | 分类名称 |
| code | VARCHAR(32) | UNIQUE | 分类编码 |
| parent_id | INT | FOREIGN KEY | 父分类ID |
| description | VARCHAR(256) | - | 分类描述 |
| icon | VARCHAR(64) | - | 图标 |
| sort_order | INT | DEFAULT 0 | 排序序号 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

#### 4.3.11 项目表 (projects)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 项目ID |
| name | VARCHAR(128) | NOT NULL | 项目名称 |
| description | TEXT | - | 项目描述 |
| status | ENUM | DEFAULT 'active' | 项目状态 |
| owner_id | VARCHAR(36) | FOREIGN KEY, NOT NULL | 所有者ID |
| department_id | INT | FOREIGN KEY | 所属部门ID |
| settings | JSON | DEFAULT '{}' | 项目配置 |
| start_date | DATE | - | 开始日期 |
| end_date | DATE | - | 结束日期 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

---

# 第20页

## 5. 详细设计

### 5.1 内容管理模块

#### 5.1.1 模块概述

内容管理模块是AIGC创作平台的核心模块，负责内容的全生命周期管理，包括创建、编辑、版本控制、审核、发布等功能。

#### 5.1.2 类图设计

```
┌────────────────────────────────────────────┐
│              ContentService                │
├────────────────────────────────────────────┤
│ - ai_service: AIService                    │
├────────────────────────────────────────────┤
│ + create_content(params) → Content         │
│ + update_content(id, params) → Content     │
│ + delete_content(id, soft_delete) → bool   │
│ + get_content(id) → Content                │
│ + list_contents(filters) → Pagination      │
│ + generate_content(params) → Dict          │
│ + submit_for_review(id) → Content          │
│ + review_content(id, params) → Content     │
│ + publish_content(id, channels) → Content  │
│ + get_content_stats(id) → Dict             │
└────────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌────────────────────────────────────────────┐
│                 AIService                  │
├────────────────────────────────────────────┤
│ - providers: Dict[str, BaseAIProvider]     │
│ - default_provider: str                    │
├────────────────────────────────────────────┤
│ + get_provider(name) → BaseAIProvider      │
│ + generate_text(params) → Dict             │
│ + generate_image(params) → Dict            │
│ + batch_generate(tasks) → List[Dict]       │
└────────────────────────────────────────────┘
                    │
                    │ implements
                    ▼
┌────────────────────────────────────────────┐
│            <<interface>>                   │
│            BaseAIProvider                  │
├────────────────────────────────────────────┤
│ + generate_text(prompt, **kwargs) → Dict   │
│ + generate_image(prompt, **kwargs) → Dict  │
└────────────────────────────────────────────┘
```

---

# 第21页

#### 5.1.3 内容创建流程

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户   │────▶│ ContentAPI  │────▶│ContentService│────▶│  Database  │
└─────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     │                │                    │                    │
     │  1.创建请求    │                    │                    │
     │───────────────▶│                    │                    │
     │                │  2.验证参数        │                    │
     │                │───────────────────▶│                    │
     │                │                    │  3.创建内容        │
     │                │                    │───────────────────▶│
     │                │                    │                    │
     │                │                    │  4.返回内容        │
     │                │                    │◀───────────────────│
     │                │  5.返回结果        │                    │
     │                │◀───────────────────│                    │
     │  6.响应        │                    │                    │
     │◀───────────────│                    │                    │
```

#### 5.1.4 AI内容生成流程

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户   │────▶│GenerationAPI│────▶│  AIService  │────▶│ AI Provider │
└─────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     │                │                    │                    │
     │  1.生成请求    │                    │                    │
     │───────────────▶│                    │                    │
     │                │  2.调用生成服务    │                    │
     │                │───────────────────▶│                    │
     │                │                    │  3.调用AI模型      │
     │                │                    │───────────────────▶│
     │                │                    │                    │
     │                │                    │  4.返回生成结果    │
     │                │                    │◀───────────────────│
     │                │  5.处理并返回      │                    │
     │                │◀───────────────────│                    │
     │  6.响应        │                    │                    │
     │◀───────────────│                    │                    │
```

---

# 第22页

#### 5.1.5 内容审核流程

```
                    ┌──────────────┐
                    │    开始      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  创建内容    │
                    │  (草稿状态)  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  编辑完善    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  提交审核    │
                    │ (待审核状态) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
              ┌────│  内容安全    │────┐
              │    │   自动检测   │    │
              │    └──────────────┘    │
              │                        │
         检测通过                  检测不通过
              │                        │
              ▼                        ▼
       ┌──────────────┐         ┌──────────────┐
       │  人工审核    │         │  标记风险    │
       └──────┬───────┘         │  人工复核    │
              │                 └──────┬───────┘
         ┌────┴────┐                   │
         │         │                   │
      通过      驳回                   │
         │         │                   │
         ▼         ▼                   ▼
  ┌───────────┐ ┌───────────┐   ┌───────────┐
  │ 审核通过  │ │ 审核驳回  │   │ 审核驳回  │
  │  可发布   │ │  返修改   │   │  返修改   │
  └─────┬─────┘ └───────────┘   └───────────┘
        │
        ▼
  ┌───────────┐
  │   发布    │
  └───────────┘
```

---

# 第23页

### 5.2 AI生成模块

#### 5.2.1 模块概述

AI生成模块封装了对接各类AI模型的能力，提供统一的生成接口，支持文本生成、图像生成等多种生成任务。模块采用策略模式设计，便于扩展新的AI提供商。

#### 5.2.2 提供商抽象设计

```python
class BaseAIProvider(ABC):
    """AI提供商基类"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成图像"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI提供商实现"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_text(self, prompt, model='gpt-4', **kwargs):
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return {
            'success': True,
            'content': response.choices[0].message.content,
            'usage': {...}
        }


class AIService:
    """AI服务统一接口"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
        }
    
    async def generate_text(self, prompt, provider=None, **kwargs):
        ai_provider = self.get_provider(provider)
        return await ai_provider.generate_text(prompt, **kwargs)
```

---

# 第24页

#### 5.2.3 批量生成设计

批量生成支持并发控制，避免对AI服务造成过大压力：

```python
async def batch_generate(
    self,
    tasks: List[Dict[str, Any]],
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    批量生成内容
    
    使用信号量控制并发数，避免过载
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_task(task):
        async with semaphore:
            task_type = task.get('type', 'text')
            prompt = task['prompt']
            params = task.get('params', {})
            
            if task_type == 'text':
                return await self.generate_text(prompt, **params)
            elif task_type == 'image':
                return await self.generate_image(prompt, **params)
    
    results = await asyncio.gather(
        *[process_task(task) for task in tasks],
        return_exceptions=True
    )
    
    return results
```

#### 5.2.4 生成参数配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model | string | gpt-4 | 模型名称 |
| max_tokens | int | 2048 | 最大生成token数 |
| temperature | float | 0.7 | 温度参数，控制随机性 |
| top_p | float | 1.0 | 核采样参数 |
| frequency_penalty | float | 0.0 | 频率惩罚 |
| presence_penalty | float | 0.0 | 存在惩罚 |

---

# 第25页

### 5.3 工作流引擎模块

#### 5.3.1 模块概述

工作流引擎模块提供可视化的流程编排能力，支持将多个任务节点组合成自动化工作流。引擎支持串行、并行、条件分支等多种编排模式。

#### 5.3.2 工作流定义结构

```json
{
    "tasks": [
        {
            "id": "task_1",
            "name": "生成文章标题",
            "type": "text_generation",
            "config": {
                "model": "gpt-4",
                "max_tokens": 100
            },
            "inputs": {
                "prompt": "{{params.topic}}"
            },
            "outputs": ["title"]
        },
        {
            "id": "task_2",
            "name": "生成文章正文",
            "type": "text_generation",
            "config": {
                "model": "gpt-4",
                "max_tokens": 2000
            },
            "inputs": {
                "prompt": "根据标题{{results.task_1.title}}写一篇文章"
            },
            "outputs": ["content"]
        }
    ],
    "connections": [
        {"source": "task_1", "target": "task_2"}
    ]
}
```

---

# 第26页

#### 5.3.3 任务执行引擎

```python
@celery.task(bind=True, max_retries=3)
def execute_workflow(self, execution_id: str):
    """执行工作流任务"""
    execution = WorkflowExecution.query.get(execution_id)
    execution.start()
    
    try:
        workflow = execution.workflow
        definition = workflow.definition
        
        # 解析工作流定义
        tasks = definition.get('tasks', [])
        connections = definition.get('connections', [])
        
        # 构建任务执行顺序（拓扑排序）
        task_order = build_task_order(tasks, connections)
        
        # 初始化执行上下文
        context = {
            'params': execution.params,
            'variables': workflow.variables.copy(),
            'results': {}
        }
        
        # 按顺序执行任务
        for task_id in task_order:
            task = next((t for t in tasks if t['id'] == task_id), None)
            if not task:
                continue
            
            task_result = execute_task(execution.id, task, context)
            context['results'][task_id] = task_result
            
            if not task_result.get('success'):
                raise Exception(f"任务执行失败: {task_result.get('error')}")
        
        execution.complete(result=context['results'])
        
    except Exception as e:
        execution.fail(str(e))
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
```

---

# 第27页

#### 5.3.4 任务类型扩展

系统支持通过插件机制扩展任务类型：

```python
class TaskExecutorRegistry:
    """任务执行器注册表"""
    
    _executors = {}
    
    @classmethod
    def register(cls, task_type: str):
        """注册任务执行器装饰器"""
        def decorator(executor_class):
            cls._executors[task_type] = executor_class
            return executor_class
        return decorator
    
    @classmethod
    def get_executor(cls, task_type: str):
        """获取任务执行器"""
        executor_class = cls._executors.get(task_type)
        if not executor_class:
            raise ValueError(f"未知的任务类型: {task_type}")
        return executor_class()


@TaskExecutorRegistry.register('text_generation')
class TextGenerationExecutor:
    """文本生成任务执行器"""
    
    async def execute(self, inputs: dict, config: dict) -> dict:
        ai_service = AIService()
        prompt = inputs.get('prompt', '')
        model = config.get('model', 'gpt-4')
        
        result = await ai_service.generate_text(
            prompt=prompt,
            model=model,
            **config
        )
        return result


@TaskExecutorRegistry.register('image_generation')
class ImageGenerationExecutor:
    """图像生成任务执行器"""
    
    async def execute(self, inputs: dict, config: dict) -> dict:
        ai_service = AIService()
        prompt = inputs.get('prompt', '')
        
        result = await ai_service.generate_image(
            prompt=prompt,
            **config
        )
        return result
```

---

# 第28页

### 5.4 资产管理模块

#### 5.4.1 模块概述

资产管理模块负责管理系统中的各类文件资源，包括图片、视频、音频、文档等。模块提供文件上传、分类管理、检索、预览等功能。

#### 5.4.2 文件上传流程

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户   │────▶│  AssetAPI   │────▶│AssetService │────▶│ FileStorage │
└─────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     │                │                    │                    │
     │  1.上传文件    │                    │                    │
     │───────────────▶│                    │                    │
     │                │  2.验证文件类型    │                    │
     │                │───────────────────▶│                    │
     │                │                    │  3.保存文件        │
     │                │                    │───────────────────▶│
     │                │                    │                    │
     │                │                    │  4.返回文件路径    │
     │                │                    │◀───────────────────│
     │                │                    │                    │
     │                │                    │  5.创建资产记录    │
     │                │                    │──────────┐         │
     │                │                    │          │         │
     │                │                    │◀─────────┘         │
     │                │                    │                    │
     │                │                    │  6.生成缩略图      │
     │                │                    │  (异步任务)        │
     │                │  7.返回结果        │                    │
     │                │◀───────────────────│                    │
     │  8.响应        │                    │                    │
     │◀───────────────│                    │                    │
```

---

# 第29页

#### 5.4.3 文件存储策略

```python
class FileStorageService:
    """文件存储服务"""
    
    def __init__(self, storage_type='local'):
        if storage_type == 'local':
            self.storage = LocalStorage()
        elif storage_type == 's3':
            self.storage = S3Storage()
        elif storage_type == 'minio':
            self.storage = MinioStorage()
    
    def save_file(self, file: FileStorage, path: str) -> str:
        """保存文件"""
        return self.storage.save(file, path)
    
    def get_file(self, path: str) -> bytes:
        """获取文件"""
        return self.storage.get(path)
    
    def delete_file(self, path: str) -> bool:
        """删除文件"""
        return self.storage.delete(path)


class LocalStorage:
    """本地文件存储"""
    
    def __init__(self):
        self.base_path = settings.UPLOAD_FOLDER
    
    def save(self, file: FileStorage, path: str) -> str:
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)
        return path


class S3Storage:
    """S3对象存储"""
    
    def __init__(self):
        self.client = boto3.client('s3')
        self.bucket = settings.S3_BUCKET
    
    def save(self, file: FileStorage, path: str) -> str:
        self.client.upload_fileobj(file, self.bucket, path)
        return f"s3://{self.bucket}/{path}"
```

---

# 第30页

#### 5.4.4 缩略图生成

```python
@celery.task
def generate_thumbnail(asset_id: str):
    """生成资产缩略图（异步任务）"""
    asset = Asset.query.get(asset_id)
    if not asset:
        return
    
    if asset.asset_type not in [AssetType.IMAGE, AssetType.VIDEO]:
        return
    
    source_path = os.path.join(settings.UPLOAD_FOLDER, asset.file_path)
    thumb_path = generate_thumb_path(asset.file_path)
    
    if asset.asset_type == AssetType.IMAGE:
        # 图片缩略图
        create_image_thumbnail(source_path, thumb_path, size=(200, 200))
    elif asset.asset_type == AssetType.VIDEO:
        # 视频封面截图
        create_video_thumbnail(source_path, thumb_path)
    
    asset.thumbnail_path = thumb_path
    db.session.commit()


def create_image_thumbnail(source: str, dest: str, size: tuple):
    """创建图片缩略图"""
    from PIL import Image
    
    with Image.open(source) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        img.save(dest, quality=85, optimize=True)


def create_video_thumbnail(source: str, dest: str, timestamp: float = 1.0):
    """创建视频封面截图"""
    import ffmpeg
    
    (
        ffmpeg
        .input(source, ss=timestamp)
        .output(dest, vframes=1)
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
```

---

**AIGC创作平台系统 V1.0 文档鉴别材料 前30页 完**

*第1页 至 第30页*

