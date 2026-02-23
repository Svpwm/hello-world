# datacore数据中台系统 V1.0 设计说明书（续）

---

## 第31页

### 5. 数据库设计

#### 5.1 数据库架构

系统数据库分为以下几类：

| 数据库类型 | 用途 | 技术选型 |
|-----------|------|---------|
| 元数据库 | 存储系统元数据 | PostgreSQL |
| 业务数据库 | 存储业务配置数据 | PostgreSQL |
| 数据仓库 | 存储分析数据 | ClickHouse/Hive |
| 缓存数据库 | 存储缓存数据 | Redis |
| 搜索引擎 | 存储检索数据 | Elasticsearch |

#### 5.2 元数据库设计

##### 5.2.1 数据源管理表

```sql
-- 数据源配置表
CREATE TABLE datasource_config (
    id              BIGSERIAL PRIMARY KEY,
    source_id       VARCHAR(64) NOT NULL UNIQUE,
    source_name     VARCHAR(128) NOT NULL,
    source_type     VARCHAR(32) NOT NULL,
    host            VARCHAR(256),
    port            INTEGER,
    database_name   VARCHAR(128),
    username        VARCHAR(128),
    password_encrypted VARCHAR(512),
    connection_params JSONB,
    status          VARCHAR(16) DEFAULT 'active',
    created_by      VARCHAR(64),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据源类型索引
CREATE INDEX idx_datasource_type ON datasource_config(source_type);
-- 状态索引
CREATE INDEX idx_datasource_status ON datasource_config(status);

COMMENT ON TABLE datasource_config IS '数据源配置表';
COMMENT ON COLUMN datasource_config.source_id IS '数据源唯一标识';
COMMENT ON COLUMN datasource_config.source_type IS '数据源类型：mysql/oracle/postgresql/mongodb等';
COMMENT ON COLUMN datasource_config.connection_params IS '额外连接参数JSON';
```

---

## 第32页

##### 5.2.2 采集任务表

```sql
-- 采集任务配置表
CREATE TABLE collection_task (
    id              BIGSERIAL PRIMARY KEY,
    task_id         VARCHAR(64) NOT NULL UNIQUE,
    task_name       VARCHAR(128) NOT NULL,
    source_id       VARCHAR(64) NOT NULL,
    target_type     VARCHAR(32) NOT NULL,
    target_config   JSONB NOT NULL,
    task_type       VARCHAR(32) NOT NULL,
    sync_mode       VARCHAR(16) NOT NULL,
    schedule_type   VARCHAR(16),
    schedule_cron   VARCHAR(64),
    table_mapping   JSONB,
    column_mapping  JSONB,
    filter_condition TEXT,
    incremental_field VARCHAR(64),
    incremental_value VARCHAR(128),
    parallelism     INTEGER DEFAULT 1,
    batch_size      INTEGER DEFAULT 1000,
    status          VARCHAR(16) DEFAULT 'inactive',
    last_run_time   TIMESTAMP,
    last_run_status VARCHAR(16),
    created_by      VARCHAR(64),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_task_source FOREIGN KEY (source_id) 
        REFERENCES datasource_config(source_id)
);

-- 任务状态索引
CREATE INDEX idx_task_status ON collection_task(status);
-- 数据源索引
CREATE INDEX idx_task_source ON collection_task(source_id);
-- 调度类型索引
CREATE INDEX idx_task_schedule ON collection_task(schedule_type);

COMMENT ON TABLE collection_task IS '数据采集任务配置表';
COMMENT ON COLUMN collection_task.task_type IS '任务类型：full/incremental/cdc';
COMMENT ON COLUMN collection_task.sync_mode IS '同步模式：batch/realtime';
COMMENT ON COLUMN collection_task.schedule_type IS '调度类型：cron/interval/manual';
```

---

## 第33页

##### 5.2.3 元数据实体表

```sql
-- 元数据实体表
CREATE TABLE metadata_entity (
    id              BIGSERIAL PRIMARY KEY,
    entity_id       VARCHAR(64) NOT NULL UNIQUE,
    entity_type     VARCHAR(32) NOT NULL,
    qualified_name  VARCHAR(512) NOT NULL UNIQUE,
    name            VARCHAR(256) NOT NULL,
    display_name    VARCHAR(256),
    description     TEXT,
    owner           VARCHAR(64),
    parent_id       VARCHAR(64),
    source_id       VARCHAR(64),
    attributes      JSONB,
    properties      JSONB,
    status          VARCHAR(16) DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_entity_parent FOREIGN KEY (parent_id)
        REFERENCES metadata_entity(entity_id)
);

-- 实体类型索引
CREATE INDEX idx_entity_type ON metadata_entity(entity_type);
-- 父实体索引
CREATE INDEX idx_entity_parent ON metadata_entity(parent_id);
-- 限定名索引
CREATE INDEX idx_entity_qualified_name ON metadata_entity(qualified_name);
-- 全文检索索引
CREATE INDEX idx_entity_search ON metadata_entity 
    USING gin(to_tsvector('simple', name || ' ' || COALESCE(display_name, '') || ' ' || COALESCE(description, '')));

COMMENT ON TABLE metadata_entity IS '元数据实体表';
COMMENT ON COLUMN metadata_entity.entity_type IS '实体类型：database/schema/table/column/file等';
COMMENT ON COLUMN metadata_entity.qualified_name IS '完全限定名称，全局唯一';

-- 表统计信息表
CREATE TABLE table_statistics (
    id              BIGSERIAL PRIMARY KEY,
    entity_id       VARCHAR(64) NOT NULL,
    row_count       BIGINT,
    data_size_bytes BIGINT,
    partition_count INTEGER,
    last_access_time TIMESTAMP,
    last_ddl_time   TIMESTAMP,
    query_count_daily INTEGER DEFAULT 0,
    collected_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_stats_entity FOREIGN KEY (entity_id)
        REFERENCES metadata_entity(entity_id)
);

CREATE INDEX idx_stats_entity ON table_statistics(entity_id);
```

---

## 第34页

##### 5.2.4 数据血缘表

```sql
-- 血缘节点表
CREATE TABLE lineage_node (
    id              BIGSERIAL PRIMARY KEY,
    node_id         VARCHAR(64) NOT NULL UNIQUE,
    node_type       VARCHAR(32) NOT NULL,
    qualified_name  VARCHAR(512) NOT NULL,
    name            VARCHAR(256) NOT NULL,
    properties      JSONB,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lineage_node_type ON lineage_node(node_type);
CREATE INDEX idx_lineage_node_qualified ON lineage_node(qualified_name);

-- 血缘边表
CREATE TABLE lineage_edge (
    id              BIGSERIAL PRIMARY KEY,
    edge_id         VARCHAR(64) NOT NULL UNIQUE,
    source_node_id  VARCHAR(64) NOT NULL,
    target_node_id  VARCHAR(64) NOT NULL,
    edge_type       VARCHAR(32) NOT NULL,
    transformation  TEXT,
    properties      JSONB,
    job_id          VARCHAR(64),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_edge_source FOREIGN KEY (source_node_id)
        REFERENCES lineage_node(node_id),
    CONSTRAINT fk_edge_target FOREIGN KEY (target_node_id)
        REFERENCES lineage_node(node_id)
);

CREATE INDEX idx_lineage_edge_source ON lineage_edge(source_node_id);
CREATE INDEX idx_lineage_edge_target ON lineage_edge(target_node_id);
CREATE INDEX idx_lineage_edge_type ON lineage_edge(edge_type);

COMMENT ON TABLE lineage_node IS '血缘节点表';
COMMENT ON TABLE lineage_edge IS '血缘边表';
COMMENT ON COLUMN lineage_edge.edge_type IS '边类型：derives_from/transforms_to/reads_from/writes_to';
COMMENT ON COLUMN lineage_edge.transformation IS 'SQL转换逻辑';
```

---

## 第35页

##### 5.2.5 数据质量表

```sql
-- 质量规则表
CREATE TABLE quality_rule (
    id              BIGSERIAL PRIMARY KEY,
    rule_id         VARCHAR(64) NOT NULL UNIQUE,
    rule_name       VARCHAR(128) NOT NULL,
    rule_type       VARCHAR(32) NOT NULL,
    dimension       VARCHAR(32) NOT NULL,
    target_type     VARCHAR(32) NOT NULL,
    target_entity   VARCHAR(512) NOT NULL,
    target_column   VARCHAR(128),
    rule_expression TEXT NOT NULL,
    parameters      JSONB,
    severity        VARCHAR(16) DEFAULT 'warning',
    threshold       DECIMAL(5,2) DEFAULT 100.00,
    enabled         BOOLEAN DEFAULT true,
    schedule_cron   VARCHAR(64),
    created_by      VARCHAR(64),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rule_type ON quality_rule(rule_type);
CREATE INDEX idx_rule_target ON quality_rule(target_entity);
CREATE INDEX idx_rule_dimension ON quality_rule(dimension);

-- 质量检测结果表
CREATE TABLE quality_result (
    id              BIGSERIAL PRIMARY KEY,
    result_id       VARCHAR(64) NOT NULL UNIQUE,
    rule_id         VARCHAR(64) NOT NULL,
    execution_id    VARCHAR(64) NOT NULL,
    passed          BOOLEAN NOT NULL,
    total_count     BIGINT,
    failed_count    BIGINT,
    pass_rate       DECIMAL(5,4),
    error_samples   JSONB,
    execution_time_ms INTEGER,
    executed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_result_rule FOREIGN KEY (rule_id)
        REFERENCES quality_rule(rule_id)
);

CREATE INDEX idx_result_rule ON quality_result(rule_id);
CREATE INDEX idx_result_execution ON quality_result(execution_id);
CREATE INDEX idx_result_time ON quality_result(executed_at);

COMMENT ON TABLE quality_rule IS '数据质量规则表';
COMMENT ON COLUMN quality_rule.dimension IS '质量维度：completeness/accuracy/consistency/timeliness/uniqueness/validity';
COMMENT ON COLUMN quality_rule.severity IS '严重级别：info/warning/error/critical';
```

---

## 第36页

##### 5.2.6 API服务表

```sql
-- API配置表
CREATE TABLE api_config (
    id              BIGSERIAL PRIMARY KEY,
    api_id          VARCHAR(64) NOT NULL UNIQUE,
    api_name        VARCHAR(128) NOT NULL,
    api_path        VARCHAR(256) NOT NULL,
    api_method      VARCHAR(16) NOT NULL DEFAULT 'GET',
    api_version     VARCHAR(16) DEFAULT 'v1',
    description     TEXT,
    category        VARCHAR(64),
    status          VARCHAR(16) DEFAULT 'draft',
    auth_type       VARCHAR(32) DEFAULT 'api_key',
    rate_limit      INTEGER DEFAULT 100,
    timeout_seconds INTEGER DEFAULT 30,
    cache_ttl       INTEGER DEFAULT 0,
    query_template  TEXT,
    parameters      JSONB,
    response_mapping JSONB,
    sample_request  JSONB,
    sample_response JSONB,
    created_by      VARCHAR(64),
    published_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_api_path_method ON api_config(api_path, api_method, api_version);
CREATE INDEX idx_api_status ON api_config(status);
CREATE INDEX idx_api_category ON api_config(category);

-- API调用日志表
CREATE TABLE api_call_log (
    id              BIGSERIAL PRIMARY KEY,
    log_id          VARCHAR(64) NOT NULL,
    api_id          VARCHAR(64) NOT NULL,
    client_id       VARCHAR(64),
    client_ip       VARCHAR(64),
    request_path    VARCHAR(512),
    request_params  JSONB,
    response_status INTEGER,
    response_time_ms INTEGER,
    error_message   TEXT,
    called_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 按时间分区，便于历史数据清理
CREATE INDEX idx_api_log_api ON api_call_log(api_id);
CREATE INDEX idx_api_log_time ON api_call_log(called_at);
CREATE INDEX idx_api_log_client ON api_call_log(client_id);

COMMENT ON TABLE api_config IS 'API服务配置表';
COMMENT ON COLUMN api_config.status IS 'API状态：draft/published/deprecated/disabled';
```

---

## 第37页

##### 5.2.7 用户权限表

```sql
-- 用户表
CREATE TABLE sys_user (
    id              BIGSERIAL PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL UNIQUE,
    username        VARCHAR(64) NOT NULL UNIQUE,
    email           VARCHAR(128) UNIQUE,
    phone           VARCHAR(32),
    password_hash   VARCHAR(256),
    display_name    VARCHAR(64),
    avatar_url      VARCHAR(512),
    department      VARCHAR(128),
    is_active       BOOLEAN DEFAULT true,
    is_superuser    BOOLEAN DEFAULT false,
    last_login_at   TIMESTAMP,
    last_login_ip   VARCHAR(64),
    password_changed_at TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_username ON sys_user(username);
CREATE INDEX idx_user_email ON sys_user(email);

-- 角色表
CREATE TABLE sys_role (
    id              BIGSERIAL PRIMARY KEY,
    role_id         VARCHAR(64) NOT NULL UNIQUE,
    role_name       VARCHAR(64) NOT NULL UNIQUE,
    role_code       VARCHAR(64) NOT NULL UNIQUE,
    description     TEXT,
    is_system       BOOLEAN DEFAULT false,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE sys_user_role (
    id              BIGSERIAL PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    role_id         VARCHAR(64) NOT NULL,
    granted_by      VARCHAR(64),
    granted_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES sys_role(role_id),
    CONSTRAINT uk_user_role UNIQUE (user_id, role_id)
);

-- 权限表
CREATE TABLE sys_permission (
    id              BIGSERIAL PRIMARY KEY,
    permission_id   VARCHAR(64) NOT NULL UNIQUE,
    permission_name VARCHAR(128) NOT NULL,
    permission_code VARCHAR(64) NOT NULL UNIQUE,
    resource_type   VARCHAR(32),
    action          VARCHAR(32),
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色权限关联表
CREATE TABLE sys_role_permission (
    id              BIGSERIAL PRIMARY KEY,
    role_id         VARCHAR(64) NOT NULL,
    permission_id   VARCHAR(64) NOT NULL,
    
    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES sys_role(role_id),
    CONSTRAINT fk_rp_perm FOREIGN KEY (permission_id) REFERENCES sys_permission(permission_id),
    CONSTRAINT uk_role_permission UNIQUE (role_id, permission_id)
);
```

---

## 第38页

##### 5.2.8 审计日志表

```sql
-- 操作审计日志表
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    log_id          VARCHAR(64) NOT NULL,
    user_id         VARCHAR(64),
    username        VARCHAR(64),
    client_ip       VARCHAR(64),
    user_agent      VARCHAR(512),
    action          VARCHAR(64) NOT NULL,
    resource_type   VARCHAR(32),
    resource_id     VARCHAR(256),
    request_method  VARCHAR(16),
    request_path    VARCHAR(512),
    request_params  JSONB,
    response_status INTEGER,
    error_message   TEXT,
    duration_ms     INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 时间索引，支持按时间查询
CREATE INDEX idx_audit_time ON audit_log(created_at);
-- 用户索引
CREATE INDEX idx_audit_user ON audit_log(user_id);
-- 操作类型索引
CREATE INDEX idx_audit_action ON audit_log(action);
-- 资源索引
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);

-- 数据访问审计表
CREATE TABLE data_access_log (
    id              BIGSERIAL PRIMARY KEY,
    log_id          VARCHAR(64) NOT NULL,
    user_id         VARCHAR(64) NOT NULL,
    username        VARCHAR(64),
    client_ip       VARCHAR(64),
    access_type     VARCHAR(32) NOT NULL,
    database_name   VARCHAR(128),
    table_name      VARCHAR(256) NOT NULL,
    columns_accessed TEXT[],
    row_count       BIGINT,
    query_text      TEXT,
    query_hash      VARCHAR(64),
    data_masked     BOOLEAN DEFAULT false,
    masked_columns  TEXT[],
    execution_time_ms INTEGER,
    accessed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_access_time ON data_access_log(accessed_at);
CREATE INDEX idx_data_access_user ON data_access_log(user_id);
CREATE INDEX idx_data_access_table ON data_access_log(table_name);

COMMENT ON TABLE audit_log IS '操作审计日志表';
COMMENT ON TABLE data_access_log IS '数据访问审计表';
COMMENT ON COLUMN data_access_log.access_type IS '访问类型：query/export/api';
```

---

## 第39页

#### 5.3 ER图

##### 5.3.1 核心实体关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ER关系图                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐         ┌──────────────┐                        │
│   │ datasource   │ 1    n  │ collection   │                        │
│   │ _config      │─────────│ _task        │                        │
│   └──────────────┘         └──────────────┘                        │
│          │                        │                                 │
│          │ 1                      │ n                               │
│          │                        │                                 │
│          ▼ n                      ▼                                 │
│   ┌──────────────┐         ┌──────────────┐                        │
│   │ metadata     │◀────────│ task_        │                        │
│   │ _entity      │         │ execution    │                        │
│   └──────────────┘         └──────────────┘                        │
│          │                                                          │
│          │ 1                                                        │
│          │                                                          │
│   ┌──────┴──────┐                                                  │
│   │             │                                                   │
│   ▼ n           ▼ n                                                │
│ ┌──────────┐ ┌──────────┐      ┌──────────────┐                   │
│ │lineage   │ │quality   │ n  n │ asset_       │                   │
│ │_node     │ │_rule     │──────│ tag          │                   │
│ └──────────┘ └──────────┘      └──────────────┘                   │
│      │              │                                               │
│      │ n            │ 1                                            │
│      │              │                                               │
│      ▼              ▼ n                                            │
│ ┌──────────┐ ┌──────────┐                                         │
│ │lineage   │ │quality   │                                         │
│ │_edge     │ │_result   │                                         │
│ └──────────┘ └──────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 第40页

##### 5.3.2 用户权限关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                      用户权限ER关系图                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        ┌──────────────┐                            │
│                        │   sys_user   │                            │
│                        └──────┬───────┘                            │
│                               │                                     │
│                               │ n                                   │
│                               │                                     │
│                        ┌──────▼───────┐                            │
│                        │sys_user_role │                            │
│                        └──────┬───────┘                            │
│                               │                                     │
│                               │ n                                   │
│                               │                                     │
│                        ┌──────▼───────┐                            │
│                        │   sys_role   │                            │
│                        └──────┬───────┘                            │
│                               │                                     │
│                               │ n                                   │
│                               │                                     │
│                        ┌──────▼───────┐                            │
│                        │sys_role_     │                            │
│                        │permission    │                            │
│                        └──────┬───────┘                            │
│                               │                                     │
│                               │ n                                   │
│                               │                                     │
│                        ┌──────▼───────┐                            │
│                        │sys_permission│                            │
│                        └──────────────┘                            │
│                                                                     │
│   关系说明：                                                         │
│   - 用户(User) N:N 角色(Role) 通过 user_role 关联                   │
│   - 角色(Role) N:N 权限(Permission) 通过 role_permission 关联       │
│   - 支持用户多角色、角色多权限的灵活配置                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 第41页

### 6. 接口设计

#### 6.1 接口规范

##### 6.1.1 RESTful API规范

系统API遵循RESTful设计规范：

| 规范项 | 说明 | 示例 |
|-------|------|------|
| URL命名 | 使用名词复数，小写，横线分隔 | /api/v1/data-sources |
| HTTP方法 | GET查询、POST创建、PUT更新、DELETE删除 | GET /api/v1/tables |
| 版本控制 | URL路径包含版本号 | /api/v1/... |
| 分页参数 | page（页码）、page_size（每页数量） | ?page=1&page_size=20 |
| 排序参数 | sort（排序字段）、order（排序方向） | ?sort=created_at&order=desc |
| 过滤参数 | 字段名作为参数名 | ?status=active |

##### 6.1.2 响应格式

**成功响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  },
  "timestamp": "2024-03-15T10:23:45.123Z",
  "request_id": "req_abc123"
}
```

**分页响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 156,
      "total_pages": 8
    }
  },
  "timestamp": "2024-03-15T10:23:45.123Z"
}
```

**错误响应：**

```json
{
  "code": 40001,
  "message": "参数验证失败",
  "errors": [
    {"field": "source_name", "message": "名称不能为空"}
  ],
  "timestamp": "2024-03-15T10:23:45.123Z",
  "request_id": "req_abc123"
}
```

---

## 第42页

##### 6.1.3 错误码定义

| 错误码范围 | 类别 | 说明 |
|-----------|------|------|
| 0 | 成功 | 请求成功 |
| 40000-40099 | 参数错误 | 请求参数验证失败 |
| 40100-40199 | 认证错误 | 认证失败、令牌过期 |
| 40300-40399 | 权限错误 | 无权访问资源 |
| 40400-40499 | 资源错误 | 资源不存在 |
| 50000-50099 | 系统错误 | 系统内部错误 |
| 50100-50199 | 服务错误 | 依赖服务异常 |

**详细错误码：**

```yaml
error_codes:
  # 参数错误
  - code: 40001
    message: "参数验证失败"
  - code: 40002
    message: "参数格式错误"
  - code: 40003
    message: "必填参数缺失"
  
  # 认证错误
  - code: 40101
    message: "未提供认证信息"
  - code: 40102
    message: "令牌已过期"
  - code: 40103
    message: "令牌无效"
  - code: 40104
    message: "用户名或密码错误"
  
  # 权限错误
  - code: 40301
    message: "无权访问该资源"
  - code: 40302
    message: "操作被拒绝"
  
  # 资源错误
  - code: 40401
    message: "资源不存在"
  - code: 40402
    message: "资源已被删除"
  - code: 40409
    message: "资源已存在"
  
  # 系统错误
  - code: 50001
    message: "系统内部错误"
  - code: 50002
    message: "数据库错误"
  - code: 50101
    message: "依赖服务不可用"
```

---

## 第43页

#### 6.2 数据源管理接口

##### 6.2.1 创建数据源

```yaml
POST /api/v1/datasources

Request:
  Headers:
    Authorization: Bearer <token>
    Content-Type: application/json
  
  Body:
    source_name: string (required)      # 数据源名称
    source_type: string (required)      # 数据源类型
    host: string (required)             # 主机地址
    port: integer (required)            # 端口号
    database: string                    # 数据库名
    username: string (required)         # 用户名
    password: string (required)         # 密码
    connection_params: object           # 额外连接参数
    description: string                 # 描述

Response:
  Success (201):
    {
      "code": 0,
      "message": "success",
      "data": {
        "source_id": "ds_001",
        "source_name": "业务主库",
        "source_type": "mysql",
        "status": "active",
        "created_at": "2024-03-15T10:00:00Z"
      }
    }
  
  Error (400):
    {
      "code": 40001,
      "message": "参数验证失败",
      "errors": [
        {"field": "source_name", "message": "名称已存在"}
      ]
    }
```

##### 6.2.2 测试数据源连接

```yaml
POST /api/v1/datasources/{source_id}/test

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "connected": true,
        "latency_ms": 23,
        "server_version": "8.0.28",
        "message": "连接成功"
      }
    }
  
  Error (200):
    {
      "code": 0,
      "data": {
        "connected": false,
        "error": "Connection refused",
        "message": "无法连接到数据库服务器"
      }
    }
```

---

## 第44页

##### 6.2.3 获取数据源列表

```yaml
GET /api/v1/datasources

Query Parameters:
  page: integer (default: 1)
  page_size: integer (default: 20, max: 100)
  source_type: string              # 按类型筛选
  status: string                   # 按状态筛选
  keyword: string                  # 关键词搜索
  sort: string (default: created_at)
  order: string (default: desc)

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "items": [
          {
            "source_id": "ds_001",
            "source_name": "业务主库",
            "source_type": "mysql",
            "host": "192.168.1.100",
            "port": 3306,
            "database": "business_db",
            "status": "active",
            "last_connected_at": "2024-03-15T09:30:00Z",
            "created_at": "2024-03-01T10:00:00Z"
          }
        ],
        "pagination": {
          "page": 1,
          "page_size": 20,
          "total": 15,
          "total_pages": 1
        }
      }
    }
```

##### 6.2.4 获取数据源元数据

```yaml
GET /api/v1/datasources/{source_id}/metadata

Query Parameters:
  refresh: boolean (default: false)  # 是否刷新缓存

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "source_id": "ds_001",
        "databases": [
          {
            "name": "business_db",
            "tables": [
              {
                "name": "users",
                "type": "TABLE",
                "row_count": 100000,
                "columns": [
                  {"name": "id", "type": "BIGINT", "nullable": false},
                  {"name": "username", "type": "VARCHAR(64)", "nullable": false},
                  {"name": "email", "type": "VARCHAR(128)", "nullable": true}
                ]
              }
            ]
          }
        ],
        "collected_at": "2024-03-15T10:00:00Z"
      }
    }
```

---

## 第45页

#### 6.3 数据质量接口

##### 6.3.1 创建质量规则

```yaml
POST /api/v1/quality/rules

Request Body:
  {
    "rule_name": "用户手机号非空检查",
    "rule_type": "not_null",
    "dimension": "completeness",
    "target_entity": "db.schema.dim_user",
    "target_column": "phone",
    "severity": "error",
    "threshold": 100,
    "schedule_cron": "0 6 * * *",
    "enabled": true
  }

Response:
  Success (201):
    {
      "code": 0,
      "data": {
        "rule_id": "rule_001",
        "rule_name": "用户手机号非空检查",
        "status": "active",
        "created_at": "2024-03-15T10:00:00Z"
      }
    }
```

##### 6.3.2 执行质量检查

```yaml
POST /api/v1/quality/rules/{rule_id}/execute

Request Body:
  {
    "sample_size": 10000,      # 采样数量，0表示全量
    "async": true              # 是否异步执行
  }

Response (async=true):
  Success (202):
    {
      "code": 0,
      "data": {
        "execution_id": "exec_001",
        "status": "running",
        "message": "质量检查任务已提交"
      }
    }

Response (async=false):
  Success (200):
    {
      "code": 0,
      "data": {
        "execution_id": "exec_001",
        "rule_id": "rule_001",
        "passed": false,
        "total_count": 10000,
        "failed_count": 23,
        "pass_rate": 0.9977,
        "execution_time_ms": 1234,
        "error_samples": [
          {"row_id": 1001, "phone": null},
          {"row_id": 1523, "phone": null}
        ]
      }
    }
```

---

## 第46页

##### 6.3.3 获取质量报告

```yaml
GET /api/v1/quality/reports

Query Parameters:
  entity: string               # 数据实体
  dimension: string            # 质量维度
  start_date: date            # 开始日期
  end_date: date              # 结束日期

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "summary": {
          "overall_score": 94.5,
          "dimension_scores": {
            "completeness": 98.2,
            "accuracy": 95.1,
            "consistency": 92.3,
            "timeliness": 96.8,
            "uniqueness": 99.5,
            "validity": 93.1
          },
          "total_rules": 56,
          "passed_rules": 52,
          "failed_rules": 4
        },
        "trend": [
          {"date": "2024-03-10", "score": 93.2},
          {"date": "2024-03-11", "score": 93.8},
          {"date": "2024-03-12", "score": 94.1},
          {"date": "2024-03-13", "score": 94.3},
          {"date": "2024-03-14", "score": 94.5}
        ],
        "issues": [
          {
            "rule_id": "rule_003",
            "rule_name": "订单金额准确性",
            "severity": "warning",
            "failed_count": 15,
            "last_check_time": "2024-03-15T06:00:00Z"
          }
        ]
      }
    }
```

---

## 第47页

#### 6.4 数据血缘接口

##### 6.4.1 查询上游血缘

```yaml
GET /api/v1/lineage/upstream

Query Parameters:
  qualified_name: string (required)  # 实体限定名
  depth: integer (default: 3)        # 查询深度
  node_types: string                 # 节点类型过滤

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "root": {
          "node_id": "node_001",
          "qualified_name": "db.schema.dws_order_1d",
          "name": "dws_order_1d",
          "node_type": "table"
        },
        "upstream": [
          {
            "node_id": "node_002",
            "qualified_name": "db.schema.dwd_order",
            "name": "dwd_order",
            "node_type": "table",
            "depth": 1,
            "edge_type": "derives_from"
          },
          {
            "node_id": "node_003",
            "qualified_name": "db.schema.ods_order",
            "name": "ods_order",
            "node_type": "table",
            "depth": 2,
            "edge_type": "derives_from"
          }
        ],
        "edges": [
          {
            "source": "node_001",
            "target": "node_002",
            "edge_type": "derives_from",
            "transformation": "SELECT ... GROUP BY ..."
          }
        ]
      }
    }
```

##### 6.4.2 影响分析

```yaml
GET /api/v1/lineage/impact-analysis

Query Parameters:
  qualified_name: string (required)
  include_indirect: boolean (default: true)

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "source": "db.schema.ods_order",
        "total_impacted": 12,
        "direct_impacted": 3,
        "indirect_impacted": 9,
        "impact_by_type": {
          "table": 8,
          "api": 3,
          "report": 1
        },
        "critical_paths": [
          ["ods_order", "dwd_order", "dws_order_1d", "report_daily"]
        ]
      }
    }
```

---

## 第48页

#### 6.5 数据服务接口

##### 6.5.1 创建数据API

```yaml
POST /api/v1/data-apis

Request Body:
  {
    "api_name": "订单列表查询",
    "api_path": "/orders",
    "api_method": "GET",
    "description": "查询订单列表",
    "parameters": [
      {
        "name": "user_id",
        "type": "string",
        "required": false,
        "description": "用户ID"
      },
      {
        "name": "status",
        "type": "string",
        "required": false,
        "enum": ["pending", "paid", "completed"]
      }
    ],
    "query_template": "SELECT * FROM orders WHERE 1=1 {% if user_id %}AND user_id = :user_id{% endif %}",
    "rate_limit": 100,
    "cache_ttl": 60
  }

Response:
  Success (201):
    {
      "code": 0,
      "data": {
        "api_id": "api_001",
        "api_name": "订单列表查询",
        "api_path": "/api/v1/data/orders",
        "status": "draft",
        "created_at": "2024-03-15T10:00:00Z"
      }
    }
```

##### 6.5.2 发布API

```yaml
POST /api/v1/data-apis/{api_id}/publish

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "api_id": "api_001",
        "status": "published",
        "published_at": "2024-03-15T10:30:00Z",
        "endpoint": "https://api.example.com/api/v1/data/orders"
      }
    }
```

---

## 第49页

##### 6.5.3 获取API统计

```yaml
GET /api/v1/data-apis/{api_id}/statistics

Query Parameters:
  start_time: datetime
  end_time: datetime
  granularity: string (hour/day/week)

Response:
  Success (200):
    {
      "code": 0,
      "data": {
        "api_id": "api_001",
        "summary": {
          "total_calls": 125680,
          "success_calls": 124532,
          "error_calls": 1148,
          "success_rate": 0.9909,
          "avg_response_time_ms": 45.2,
          "p95_response_time_ms": 120,
          "p99_response_time_ms": 250
        },
        "time_series": [
          {
            "time": "2024-03-15T00:00:00Z",
            "calls": 5230,
            "success_rate": 0.992,
            "avg_response_time_ms": 42.1
          },
          {
            "time": "2024-03-15T01:00:00Z",
            "calls": 4856,
            "success_rate": 0.995,
            "avg_response_time_ms": 38.5
          }
        ],
        "error_distribution": {
          "40001": 523,
          "40101": 312,
          "50001": 213,
          "50401": 100
        },
        "top_clients": [
          {"client_id": "client_001", "calls": 35620},
          {"client_id": "client_002", "calls": 28450}
        ]
      }
    }
```

---

## 第50页

### 7. 安全设计

#### 7.1 认证授权

##### 7.1.1 认证流程

```
┌─────────────────────────────────────────────────────────────┐
│                      JWT认证流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  登录流程：                                                  │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐             │
│  │客户端│───▶│认证   │───▶│验证   │───▶│生成   │             │
│  │      │    │请求   │    │凭据   │    │Token │             │
│  └──────┘    └──────┘    └──────┘    └───┬──┘             │
│                                          │                 │
│                                          ▼                 │
│  ┌──────┐    ┌──────┐                ┌──────┐             │
│  │存储   │◀───│返回   │◀───────────────│JWT    │             │
│  │Token │    │Token │                │Token │             │
│  └──────┘    └──────┘                └──────┘             │
│                                                             │
│  请求流程：                                                  │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐             │
│  │携带   │───▶│验证   │───▶│解析   │───▶│权限   │             │
│  │Token │    │Token │    │用户   │    │检查   │             │
│  └──────┘    └──────┘    └──────┘    └───┬──┘             │
│                                          │                 │
│                                          ▼                 │
│                                      ┌──────┐             │
│                                      │处理   │             │
│                                      │请求   │             │
│                                      └──────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##### 7.1.2 Token结构

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_001",
    "username": "zhangsan",
    "roles": ["data_analyst", "api_developer"],
    "permissions": ["read:table", "write:api"],
    "iat": 1710489600,
    "exp": 1710576000,
    "jti": "token_unique_id"
  },
  "signature": "..."
}
```

---

## 第51页

#### 7.2 数据加密

##### 7.2.1 加密策略

| 加密场景 | 加密方式 | 说明 |
|---------|---------|------|
| 传输加密 | TLS 1.3 | 所有API通信启用HTTPS |
| 存储加密 | AES-256 | 敏感配置信息加密存储 |
| 密码加密 | bcrypt | 用户密码哈希存储 |
| 令牌签名 | HMAC-SHA256 | JWT令牌签名 |

##### 7.2.2 敏感信息保护

```
┌─────────────────────────────────────────────────────────────┐
│                   敏感信息保护策略                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  配置信息加密：                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ - 数据源密码：AES-256加密存储                         │   │
│  │ - API密钥：加密存储，脱敏显示                         │   │
│  │ - 连接字符串：敏感部分加密                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  日志脱敏：                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ - SQL中的敏感参数值脱敏                              │   │
│  │ - 请求参数中的密码脱敏                               │   │
│  │ - 响应中的敏感字段脱敏                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  密钥管理：                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ - 主密钥存储在密钥管理服务(KMS)                       │   │
│  │ - 数据密钥由主密钥加密保护                           │   │
│  │ - 定期轮换密钥                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 第52页

#### 7.3 安全审计

##### 7.3.1 审计范围

| 审计类型 | 审计内容 | 保留期限 |
|---------|---------|---------|
| 登录审计 | 登录成功/失败、登出 | 180天 |
| 操作审计 | 增删改操作 | 365天 |
| 数据访问审计 | 查询、导出、API调用 | 90天 |
| 权限变更审计 | 角色分配、权限修改 | 永久 |
| 系统配置审计 | 系统参数变更 | 永久 |

##### 7.3.2 审计告警

```yaml
audit_alerts:
  # 异常登录告警
  - name: "异常登录检测"
    condition: |
      login_failed_count > 5 within 10 minutes
      OR login_from_new_location
      OR login_at_unusual_time
    severity: "high"
    actions:
      - notify_admin
      - lock_account
  
  # 敏感数据访问告警
  - name: "敏感数据大量导出"
    condition: |
      action = 'export'
      AND table IN (sensitive_tables)
      AND row_count > 10000
    severity: "medium"
    actions:
      - notify_data_owner
      - log_detail
  
  # 权限变更告警
  - name: "高权限角色分配"
    condition: |
      action = 'grant_role'
      AND role IN ('admin', 'data_admin')
    severity: "high"
    actions:
      - notify_security_team
      - require_approval
```

---

## 第53页

### 8. 部署方案

#### 8.1 部署架构

##### 8.1.1 生产环境部署架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        生产环境部署架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                           ┌─────────┐                               │
│                           │  CDN    │                               │
│                           └────┬────┘                               │
│                                │                                    │
│                           ┌────▼────┐                               │
│                           │  WAF    │                               │
│                           └────┬────┘                               │
│                                │                                    │
│                           ┌────▼────┐                               │
│                           │   LB    │                               │
│                           │ (SLB)   │                               │
│                           └────┬────┘                               │
│                                │                                    │
│         ┌──────────────────────┼──────────────────────┐            │
│         │                      │                      │            │
│    ┌────▼────┐           ┌────▼────┐           ┌────▼────┐        │
│    │  Web    │           │  Web    │           │  Web    │        │
│    │ Node 1  │           │ Node 2  │           │ Node 3  │        │
│    └────┬────┘           └────┬────┘           └────┬────┘        │
│         │                      │                      │            │
│         └──────────────────────┼──────────────────────┘            │
│                                │                                    │
│    ┌───────────────────────────┼───────────────────────────┐       │
│    │                           │                           │       │
│    │    ┌──────────────────────┼──────────────────────┐   │       │
│    │    │                      │                      │   │       │
│    ▼    ▼                      ▼                      ▼   ▼       │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│ │ PG主    │  │ PG从    │  │ Redis   │  │ Kafka   │  │ ES      │ │
│ │         │  │         │  │ Cluster │  │ Cluster │  │ Cluster │ │
│ └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 第54页

##### 8.1.2 容器化部署

```yaml
# docker-compose.yml (生产配置)
version: '3.8'

services:
  web:
    image: datacore/web:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
      restart_policy:
        condition: on-failure
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BROKERS=${KAFKA_BROKERS}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    image: datacore/worker:${VERSION}
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '4'
          memory: 8G
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BROKERS=${KAFKA_BROKERS}

  scheduler:
    image: datacore/scheduler:${VERSION}
    deploy:
      replicas: 1
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}

  postgres:
    image: postgres:15
    deploy:
      placement:
        constraints:
          - node.labels.db == true
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=datacore
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

volumes:
  pg_data:
```

---

## 第55页

#### 8.2 高可用设计

##### 8.2.1 应用层高可用

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层高可用架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      ┌──────────────┐                       │
│                      │   负载均衡   │                       │
│                      │   (主备)     │                       │
│                      └──────┬───────┘                       │
│                             │                               │
│           ┌─────────────────┼─────────────────┐            │
│           │                 │                 │            │
│      ┌────▼────┐       ┌────▼────┐       ┌────▼────┐      │
│      │ App-1   │       │ App-2   │       │ App-3   │      │
│      │(Active) │       │(Active) │       │(Active) │      │
│      └─────────┘       └─────────┘       └─────────┘      │
│                                                             │
│  设计要点：                                                  │
│  - 无状态设计：会话信息存储在Redis                           │
│  - 健康检查：定期探测应用健康状态                            │
│  - 优雅停机：支持平滑发布和重启                              │
│  - 自动扩缩：根据负载自动调整实例数                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##### 8.2.2 数据层高可用

| 组件 | 高可用方案 | RPO | RTO |
|------|-----------|-----|-----|
| PostgreSQL | 主从复制+自动故障转移 | 0 | <30s |
| Redis | Sentinel集群 | <1s | <10s |
| Kafka | 多副本+ISR机制 | 0 | <10s |
| Elasticsearch | 多节点分片副本 | 0 | <60s |

---

## 第56页

#### 8.3 监控告警

##### 8.3.1 监控指标

```yaml
monitoring_metrics:
  # 系统指标
  system:
    - name: cpu_usage
      description: CPU使用率
      threshold: 80%
      
    - name: memory_usage
      description: 内存使用率
      threshold: 85%
      
    - name: disk_usage
      description: 磁盘使用率
      threshold: 80%
  
  # 应用指标
  application:
    - name: request_rate
      description: 请求QPS
      
    - name: response_time_p95
      description: 95分位响应时间
      threshold: 500ms
      
    - name: error_rate
      description: 错误率
      threshold: 1%
  
  # 业务指标
  business:
    - name: collection_task_success_rate
      description: 采集任务成功率
      threshold: 95%
      
    - name: quality_check_pass_rate
      description: 质量检查通过率
      threshold: 90%
      
    - name: api_availability
      description: API可用性
      threshold: 99.9%
```

##### 8.3.2 告警规则

| 告警级别 | 响应时间 | 通知方式 |
|---------|---------|---------|
| P0-紧急 | 5分钟 | 电话+短信+邮件 |
| P1-严重 | 15分钟 | 短信+邮件 |
| P2-警告 | 30分钟 | 邮件+钉钉 |
| P3-提示 | 2小时 | 邮件 |

---

## 第57页

### 9. 运维手册

#### 9.1 日常运维

##### 9.1.1 健康检查

```bash
#!/bin/bash
# health_check.sh - 系统健康检查脚本

echo "=== DataCore健康检查 ==="
echo "检查时间: $(date)"

# 检查Web服务
echo -n "Web服务: "
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "正常"
else
    echo "异常"
fi

# 检查数据库
echo -n "数据库: "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "正常"
else
    echo "异常"
fi

# 检查Redis
echo -n "Redis: "
if redis-cli ping > /dev/null 2>&1; then
    echo "正常"
else
    echo "异常"
fi

# 检查Kafka
echo -n "Kafka: "
if kafka-broker-api-versions.sh --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "正常"
else
    echo "异常"
fi

# 检查磁盘空间
echo "磁盘使用:"
df -h | grep -E '^/dev'

# 检查内存使用
echo "内存使用:"
free -h
```

---

## 第58页

##### 9.1.2 日志管理

```yaml
# 日志配置
logging:
  # 日志级别
  level: INFO
  
  # 日志格式
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # 日志文件
  handlers:
    # 应用日志
    - type: file
      filename: /var/log/datacore/app.log
      max_size: 100MB
      backup_count: 30
      
    # 访问日志
    - type: file
      filename: /var/log/datacore/access.log
      max_size: 200MB
      backup_count: 7
      
    # 错误日志
    - type: file
      filename: /var/log/datacore/error.log
      level: ERROR
      max_size: 50MB
      backup_count: 30

# 日志清理策略
cleanup:
  # 应用日志保留30天
  app_logs: 30d
  # 访问日志保留7天
  access_logs: 7d
  # 审计日志保留1年
  audit_logs: 365d
```

##### 9.1.3 备份策略

| 备份类型 | 备份频率 | 保留周期 | 存储位置 |
|---------|---------|---------|---------|
| 全量备份 | 每天 | 30天 | OSS |
| 增量备份 | 每小时 | 7天 | 本地+OSS |
| 配置备份 | 实时 | 永久 | Git |
| 审计日志备份 | 每天 | 3年 | OSS冷存储 |

---

## 第59页

#### 9.2 故障处理

##### 9.2.1 常见故障处理

| 故障类型 | 现象 | 处理步骤 |
|---------|------|---------|
| 数据库连接满 | 请求超时 | 1.检查连接数 2.释放空闲连接 3.调整连接池 |
| 内存溢出 | OOM重启 | 1.查看heapdump 2.定位泄漏 3.优化代码 |
| 磁盘满 | 写入失败 | 1.清理日志 2.清理临时文件 3.扩容 |
| 采集任务卡死 | 任务无进度 | 1.检查数据源 2.检查网络 3.重启任务 |

##### 9.2.2 故障升级流程

```
┌─────────────────────────────────────────────────────────────┐
│                      故障升级流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│  │ 故障发现 │────▶│ 初步定位 │────▶│ 紧急处理 │           │
│  └──────────┘     └──────────┘     └──────────┘           │
│       │                                  │                 │
│       │ <5分钟                           │ 未解决          │
│       │                                  ▼                 │
│       │               ┌──────────────────────────────┐    │
│       │               │         升级处理             │    │
│       │               │  L1: 值班工程师 (15分钟)     │    │
│       │               │  L2: 技术负责人 (30分钟)     │    │
│       │               │  L3: 架构师/CTO (60分钟)     │    │
│       │               └──────────────────────────────┘    │
│       │                                  │                 │
│       │                                  ▼                 │
│       │                           ┌──────────┐            │
│       └──────────────────────────▶│ 故障恢复 │            │
│                                   └──────────┘            │
│                                        │                  │
│                                        ▼                  │
│                                   ┌──────────┐            │
│                                   │ 复盘改进 │            │
│                                   └──────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 第60页

### 10. 附录

#### 10.1 术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| 数据中台 | Data Middle Platform | 企业级数据服务共享平台 |
| 元数据 | Metadata | 描述数据的数据 |
| 数据血缘 | Data Lineage | 数据的来源和流转关系 |
| ETL | Extract-Transform-Load | 数据抽取、转换、加载 |
| CDC | Change Data Capture | 变更数据捕获 |
| RBAC | Role-Based Access Control | 基于角色的访问控制 |
| API网关 | API Gateway | API统一入口和管理平台 |
| 数据脱敏 | Data Masking | 敏感数据保护处理 |

#### 10.2 参考文档

1. FastAPI官方文档: https://fastapi.tiangolo.com/
2. Apache Kafka文档: https://kafka.apache.org/documentation/
3. Redis官方文档: https://redis.io/documentation
4. PostgreSQL官方文档: https://www.postgresql.org/docs/
5. Elasticsearch官方文档: https://www.elastic.co/guide/

#### 10.3 版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2024-03-15 | 初始版本 | 技术部 |

---

**文档结束**

---

北京灵犀科技有限公司 - datacore数据中台系统 V1.0 设计说明书
第31-60页 / 共60页

