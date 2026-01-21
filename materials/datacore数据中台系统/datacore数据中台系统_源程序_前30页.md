# datacore数据中台系统 V1.0 源程序代码

## 第1页

```python
# -*- coding: utf-8 -*-
"""
datacore数据中台系统 V1.0
Copyright (c) 2024 南京初鑫信息科技有限公司
All Rights Reserved.

文件: app/__init__.py
描述: 应用程序初始化模块
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from redis import Redis
from celery import Celery

from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
celery = Celery(__name__)


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称
        
    Returns:
        Flask应用实例
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    
    # 初始化Redis
    app.redis = Redis.from_url(app.config['REDIS_URL'])
```

## 第2页

```python
    # 初始化Celery
    celery.conf.update(app.config)
    
    # 注册蓝图
    from app.api import api_bp
    from app.auth import auth_bp
    from app.integration import integration_bp
    from app.model import model_bp
    from app.service import service_bp
    from app.asset import asset_bp
    from app.monitor import monitor_bp
    
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(integration_bp, url_prefix='/integration')
    app.register_blueprint(model_bp, url_prefix='/model')
    app.register_blueprint(service_bp, url_prefix='/service')
    app.register_blueprint(asset_bp, url_prefix='/asset')
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 配置日志
    setup_logging(app)
    
    return app


def register_error_handlers(app):
    """注册全局错误处理器"""
    from app.errors import (
        handle_400_error, handle_401_error,
        handle_403_error, handle_404_error,
        handle_500_error
    )
    
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(401, handle_401_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)


def setup_logging(app):
    """配置应用日志"""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(level=getattr(logging, log_level), format=log_format)
```

## 第3页

```python
# 文件: app/models/datasource.py
"""
数据源模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class SourceType(Enum):
    """数据源类型"""
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    ORACLE = 'oracle'
    SQLSERVER = 'sqlserver'
    HIVE = 'hive'
    SPARK = 'spark'
    KAFKA = 'kafka'
    ELASTICSEARCH = 'elasticsearch'
    MONGODB = 'mongodb'
    REDIS = 'redis'
    HTTP = 'http'
    FILE = 'file'


class SourceStatus(Enum):
    """数据源状态"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ERROR = 'error'


class DataSource(db.Model):
    """数据源模型"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.Enum(SourceType), nullable=False)
    status = db.Column(db.Enum(SourceStatus), default=SourceStatus.INACTIVE)
    
    # 连接配置
    connection_config = db.Column(db.JSON, default=dict)
    
    # 元数据
    schema_info = db.Column(db.JSON, default=dict)
    last_sync_at = db.Column(db.DateTime)
    
    # 所属域
    domain_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'))
    
    # 关联
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
```

## 第4页

```python
    # 统计
    table_count = db.Column(db.Integer, default=0)
    sync_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    sync_tasks = db.relationship('SyncTask', backref='source', lazy='dynamic')
    tables = db.relationship('SourceTable', backref='source', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataSource {self.name}>'
    
    def test_connection(self):
        """测试连接"""
        from app.services.connector import ConnectorFactory
        connector = ConnectorFactory.create(self)
        return connector.test()
    
    def sync_metadata(self):
        """同步元数据"""
        from app.services.connector import ConnectorFactory
        connector = ConnectorFactory.create(self)
        self.schema_info = connector.get_schema()
        self.last_sync_at = datetime.utcnow()
        self.sync_count += 1
        db.session.commit()
        return self.schema_info
    
    def to_dict(self, include_config=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'source_type': self.source_type.value,
            'status': self.status.value,
            'domain_id': self.domain_id,
            'table_count': self.table_count,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'created_at': self.created_at.isoformat()
        }
        if include_config:
            config = self.connection_config.copy()
            if 'password' in config:
                config['password'] = '******'
            data['connection_config'] = config
        return data
```

## 第5页

```python
class SourceTable(db.Model):
    """数据源表模型"""
    __tablename__ = 'source_tables'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = db.Column(db.String(36), db.ForeignKey('data_sources.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    comment = db.Column(db.String(512))
    
    # 表信息
    schema_name = db.Column(db.String(128))
    table_type = db.Column(db.String(32), default='table')  # table, view
    columns = db.Column(db.JSON, default=list)
    
    # 统计
    row_count = db.Column(db.BigInteger, default=0)
    size_bytes = db.Column(db.BigInteger, default=0)
    
    # 映射关系
    mapped_entity_id = db.Column(db.String(36), db.ForeignKey('data_entities.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'name': self.name,
            'comment': self.comment,
            'schema_name': self.schema_name,
            'table_type': self.table_type,
            'columns': self.columns,
            'row_count': self.row_count,
            'size_bytes': self.size_bytes
        }


class SyncTask(db.Model):
    """同步任务模型"""
    __tablename__ = 'sync_tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = db.Column(db.String(36), db.ForeignKey('data_sources.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    
    # 同步配置
    sync_type = db.Column(db.String(32), default='full')  # full, incremental
    sync_config = db.Column(db.JSON, default=dict)
    schedule_config = db.Column(db.JSON, default=dict)
    
    # 目标配置
    target_config = db.Column(db.JSON, default=dict)
    
    status = db.Column(db.String(32), default='inactive')
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
```

## 第6页

```python
    # 统计
    run_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 运行记录
    runs = db.relationship('SyncRun', backref='task', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'name': self.name,
            'sync_type': self.sync_type,
            'status': self.status,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None
        }


# 文件: app/models/domain.py
"""
主题域模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class DomainType(Enum):
    """主题域类型"""
    ODS = 'ods'      # 操作数据层
    DWD = 'dwd'      # 明细数据层
    DWS = 'dws'      # 汇总数据层
    ADS = 'ads'      # 应用数据层
    DIM = 'dim'      # 维度层


class DataDomain(db.Model):
    """数据域模型"""
    __tablename__ = 'data_domains'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    domain_type = db.Column(db.Enum(DomainType), nullable=False)
    
    # 层级关系
    parent_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'))
    level = db.Column(db.Integer, default=1)
    path = db.Column(db.String(512))  # 路径: /root/parent/current
```

## 第7页

```python
    # 负责人
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # 排序
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    children = db.relationship('DataDomain', backref=db.backref('parent', remote_side=[id]))
    entities = db.relationship('DataEntity', backref='domain', lazy='dynamic')
    sources = db.relationship('DataSource', backref='domain', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataDomain {self.name}>'
    
    def get_ancestors(self):
        """获取所有祖先域"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """获取所有后代域"""
        descendants = []
        
        def collect(domain):
            for child in domain.children:
                descendants.append(child)
                collect(child)
        
        collect(self)
        return descendants
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'domain_type': self.domain_type.value,
            'parent_id': self.parent_id,
            'level': self.level,
            'path': self.path,
            'is_active': self.is_active
        }
        if include_children:
            data['children'] = [c.to_dict(True) for c in self.children]
        return data
```

## 第8页

```python
class DataEntity(db.Model):
    """数据实体模型"""
    __tablename__ = 'data_entities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    name_en = db.Column(db.String(128))
    description = db.Column(db.Text)
    
    # 所属域
    domain_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'), nullable=False)
    
    # 实体类型
    entity_type = db.Column(db.String(32), default='table')  # table, dimension, fact
    
    # 物理信息
    physical_table = db.Column(db.String(256))
    physical_schema = db.Column(db.String(128))
    
    # 负责人
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # 生命周期
    lifecycle_days = db.Column(db.Integer, default=-1)  # -1表示永久保留
    
    # 状态
    status = db.Column(db.String(32), default='draft')  # draft, active, deprecated
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    fields = db.relationship('EntityField', backref='entity', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataEntity {self.name}>'
    
    def to_dict(self, include_fields=False):
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'name_en': self.name_en,
            'description': self.description,
            'domain_id': self.domain_id,
            'entity_type': self.entity_type,
            'physical_table': self.physical_table,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
        if include_fields:
            data['fields'] = [f.to_dict() for f in self.fields]
        return data
```

## 第9页

```python
class EntityField(db.Model):
    """实体字段模型"""
    __tablename__ = 'entity_fields'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = db.Column(db.String(36), db.ForeignKey('data_entities.id'), nullable=False)
    
    name = db.Column(db.String(128), nullable=False)
    name_en = db.Column(db.String(128))
    description = db.Column(db.Text)
    
    # 字段类型
    data_type = db.Column(db.String(64), nullable=False)
    length = db.Column(db.Integer)
    precision = db.Column(db.Integer)
    scale = db.Column(db.Integer)
    
    # 约束
    is_primary = db.Column(db.Boolean, default=False)
    is_nullable = db.Column(db.Boolean, default=True)
    is_partition = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(256))
    
    # 关联标准
    standard_id = db.Column(db.String(36), db.ForeignKey('data_standards.id'))
    
    # 排序
    sort_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'name': self.name,
            'name_en': self.name_en,
            'description': self.description,
            'data_type': self.data_type,
            'length': self.length,
            'is_primary': self.is_primary,
            'is_nullable': self.is_nullable,
            'default_value': self.default_value,
            'standard_id': self.standard_id,
            'sort_order': self.sort_order
        }
```

## 第10页

```python
# 文件: app/models/standard.py
"""
数据标准模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class StandardType(Enum):
    """标准类型"""
    NAMING = 'naming'          # 命名标准
    DATA_TYPE = 'data_type'    # 数据类型标准
    CODE = 'code'              # 代码标准
    QUALITY = 'quality'        # 质量标准


class DataStandard(db.Model):
    """数据标准模型"""
    __tablename__ = 'data_standards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    standard_type = db.Column(db.Enum(StandardType), nullable=False)
    
    # 标准内容
    content = db.Column(db.JSON, default=dict)
    
    # 分类
    category_id = db.Column(db.String(36), db.ForeignKey('standard_categories.id'))
    
    # 版本
    version = db.Column(db.String(32), default='1.0')
    
    # 状态
    status = db.Column(db.String(32), default='draft')  # draft, active, deprecated
    
    # 负责人
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataStandard {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'standard_type': self.standard_type.value,
            'content': self.content,
            'version': self.version,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
```

## 第11页

```python
class StandardCategory(db.Model):
    """标准分类模型"""
    __tablename__ = 'standard_categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(32), unique=True)
    parent_id = db.Column(db.String(36), db.ForeignKey('standard_categories.id'))
    description = db.Column(db.String(256))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    children = db.relationship('StandardCategory', backref=db.backref('parent', remote_side=[id]))
    standards = db.relationship('DataStandard', backref='category', lazy='dynamic')
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'description': self.description,
            'sort_order': self.sort_order
        }
        if include_children:
            data['children'] = [c.to_dict(True) for c in self.children]
        return data


# 文件: app/models/service.py
"""
数据服务模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class ServiceType(Enum):
    """服务类型"""
    API = 'api'            # API服务
    QUERY = 'query'        # 查询服务
    SUBSCRIBE = 'subscribe' # 订阅服务
    FILE = 'file'          # 文件服务


class ServiceStatus(Enum):
    """服务状态"""
    DRAFT = 'draft'
    ACTIVE = 'active'
    OFFLINE = 'offline'
    DEPRECATED = 'deprecated'
```

## 第12页

```python
class DataService(db.Model):
    """数据服务模型"""
    __tablename__ = 'data_services'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    status = db.Column(db.Enum(ServiceStatus), default=ServiceStatus.DRAFT)
    
    # API配置
    api_path = db.Column(db.String(256))
    api_method = db.Column(db.String(16), default='GET')
    
    # 服务配置
    config = db.Column(db.JSON, default=dict)
    
    # 请求/响应定义
    request_schema = db.Column(db.JSON, default=dict)
    response_schema = db.Column(db.JSON, default=dict)
    
    # 数据来源
    source_type = db.Column(db.String(32))  # entity, sql, function
    source_config = db.Column(db.JSON, default=dict)
    
    # 访问控制
    auth_required = db.Column(db.Boolean, default=True)
    rate_limit = db.Column(db.Integer, default=1000)  # 每分钟请求数
    
    # 关联
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    domain_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'))
    
    # 版本
    version = db.Column(db.String(32), default='1.0')
    
    # 统计
    call_count = db.Column(db.BigInteger, default=0)
    success_count = db.Column(db.BigInteger, default=0)
    avg_response_time = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # 关联关系
    subscriptions = db.relationship('ServiceSubscription', backref='service', lazy='dynamic')
    call_logs = db.relationship('ServiceCallLog', backref='service', lazy='dynamic')
```

## 第13页

```python
    def __repr__(self):
        return f'<DataService {self.name}>'
    
    def publish(self):
        """发布服务"""
        if self.status == ServiceStatus.DRAFT:
            self.status = ServiceStatus.ACTIVE
            self.published_at = datetime.utcnow()
            db.session.commit()
    
    def offline(self):
        """下线服务"""
        self.status = ServiceStatus.OFFLINE
        db.session.commit()
    
    def deprecate(self):
        """废弃服务"""
        self.status = ServiceStatus.DEPRECATED
        db.session.commit()
    
    def to_dict(self, include_schema=False):
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'service_type': self.service_type.value,
            'status': self.status.value,
            'api_path': self.api_path,
            'api_method': self.api_method,
            'auth_required': self.auth_required,
            'rate_limit': self.rate_limit,
            'version': self.version,
            'call_count': self.call_count,
            'avg_response_time': self.avg_response_time,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        if include_schema:
            data['request_schema'] = self.request_schema
            data['response_schema'] = self.response_schema
            data['config'] = self.config
        return data


class ServiceSubscription(db.Model):
    """服务订阅模型"""
    __tablename__ = 'service_subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = db.Column(db.String(36), db.ForeignKey('data_services.id'), nullable=False)
    subscriber_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # 订阅配置
    app_key = db.Column(db.String(64), unique=True, nullable=False)
    app_secret = db.Column(db.String(128), nullable=False)
```

## 第14页

```python
    # 配额
    daily_quota = db.Column(db.Integer, default=10000)
    used_quota = db.Column(db.Integer, default=0)
    
    # 状态
    status = db.Column(db.String(32), default='pending')  # pending, approved, rejected
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # 有效期
    expires_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'subscriber_id': self.subscriber_id,
            'app_key': self.app_key,
            'daily_quota': self.daily_quota,
            'used_quota': self.used_quota,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class ServiceCallLog(db.Model):
    """服务调用日志模型"""
    __tablename__ = 'service_call_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = db.Column(db.String(36), db.ForeignKey('data_services.id'), nullable=False)
    subscription_id = db.Column(db.String(36), db.ForeignKey('service_subscriptions.id'))
    
    # 请求信息
    request_method = db.Column(db.String(16))
    request_path = db.Column(db.String(512))
    request_params = db.Column(db.JSON, default=dict)
    request_body = db.Column(db.Text)
    
    # 响应信息
    response_code = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    
    # 性能指标
    response_time_ms = db.Column(db.Integer)
    
    # 客户端信息
    client_ip = db.Column(db.String(64))
    user_agent = db.Column(db.String(512))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 第15页

```python
# 文件: app/models/indicator.py
"""
指标模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class IndicatorType(Enum):
    """指标类型"""
    ATOMIC = 'atomic'          # 原子指标
    DERIVED = 'derived'        # 派生指标
    COMPOSITE = 'composite'    # 复合指标


class AggregationType(Enum):
    """聚合类型"""
    SUM = 'sum'
    COUNT = 'count'
    AVG = 'avg'
    MAX = 'max'
    MIN = 'min'
    DISTINCT_COUNT = 'distinct_count'


class Indicator(db.Model):
    """指标模型"""
    __tablename__ = 'indicators'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    name_en = db.Column(db.String(128))
    description = db.Column(db.Text)
    
    # 指标类型
    indicator_type = db.Column(db.Enum(IndicatorType), nullable=False)
    
    # 所属域
    domain_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'))
    
    # 业务定义
    business_definition = db.Column(db.Text)
    calculation_formula = db.Column(db.Text)
    
    # 技术实现
    aggregation_type = db.Column(db.Enum(AggregationType))
    source_field = db.Column(db.String(256))
    filter_condition = db.Column(db.Text)
    
    # 关联实体
    entity_id = db.Column(db.String(36), db.ForeignKey('data_entities.id'))
    
    # 数据类型
    data_type = db.Column(db.String(32), default='decimal')
    unit = db.Column(db.String(32))  # 单位
    precision = db.Column(db.Integer, default=2)
```

## 第16页

```python
    # 状态
    status = db.Column(db.String(32), default='draft')  # draft, active, deprecated
    
    # 负责人
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # 版本
    version = db.Column(db.String(32), default='1.0')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    dimensions = db.relationship('IndicatorDimension', backref='indicator', lazy='dynamic')
    
    def __repr__(self):
        return f'<Indicator {self.name}>'
    
    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'name_en': self.name_en,
            'description': self.description,
            'indicator_type': self.indicator_type.value,
            'domain_id': self.domain_id,
            'business_definition': self.business_definition,
            'data_type': self.data_type,
            'unit': self.unit,
            'status': self.status,
            'version': self.version,
            'created_at': self.created_at.isoformat()
        }
        if include_details:
            data['calculation_formula'] = self.calculation_formula
            data['aggregation_type'] = self.aggregation_type.value if self.aggregation_type else None
            data['source_field'] = self.source_field
            data['dimensions'] = [d.to_dict() for d in self.dimensions]
        return data


class IndicatorDimension(db.Model):
    """指标维度关联模型"""
    __tablename__ = 'indicator_dimensions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    indicator_id = db.Column(db.String(36), db.ForeignKey('indicators.id'), nullable=False)
    dimension_id = db.Column(db.String(36), db.ForeignKey('dimensions.id'), nullable=False)
    is_required = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'indicator_id': self.indicator_id,
            'dimension_id': self.dimension_id,
            'is_required': self.is_required
        }
```

## 第17页

```python
class Dimension(db.Model):
    """维度模型"""
    __tablename__ = 'dimensions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    name_en = db.Column(db.String(128))
    description = db.Column(db.Text)
    
    # 维度类型
    dimension_type = db.Column(db.String(32), default='normal')  # normal, time, hierarchy
    
    # 关联实体
    entity_id = db.Column(db.String(36), db.ForeignKey('data_entities.id'))
    
    # 层级配置（层级维度）
    hierarchy_config = db.Column(db.JSON, default=dict)
    
    # 时间粒度（时间维度）
    time_granularity = db.Column(db.String(32))  # year, quarter, month, week, day
    
    # 所属域
    domain_id = db.Column(db.String(36), db.ForeignKey('data_domains.id'))
    
    # 状态
    status = db.Column(db.String(32), default='draft')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Dimension {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'name_en': self.name_en,
            'description': self.description,
            'dimension_type': self.dimension_type,
            'entity_id': self.entity_id,
            'time_granularity': self.time_granularity,
            'domain_id': self.domain_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
```

## 第18页

```python
# 文件: app/services/connector.py
"""
数据源连接器服务模块
"""
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

import pymysql
import psycopg2

from app.models.datasource import DataSource, SourceType


logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """连接器基类"""
    
    @abstractmethod
    def connect(self):
        """建立连接"""
        pass
    
    @abstractmethod
    def test(self) -> bool:
        """测试连接"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """获取元数据"""
        pass
    
    @abstractmethod
    def execute(self, sql: str, params: tuple = None) -> List[Dict]:
        """执行查询"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭连接"""
        pass


class MySQLConnector(BaseConnector):
    """MySQL连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self):
        self.connection = pymysql.connect(
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 3306),
            user=self.config.get('user'),
            password=self.config.get('password'),
            database=self.config.get('database'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return self.connection
```

## 第19页

```python
    def test(self) -> bool:
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1')
            conn.close()
            return True
        except Exception as e:
            logger.error(f'MySQL连接测试失败: {str(e)}')
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        schema = {'tables': []}
        conn = self.connect()
        
        try:
            with conn.cursor() as cursor:
                # 获取表列表
                cursor.execute("""
                    SELECT TABLE_NAME, TABLE_COMMENT, TABLE_ROWS
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
                """, (self.config.get('database'),))
                tables = cursor.fetchall()
                
                for table in tables:
                    table_info = {
                        'name': table['TABLE_NAME'],
                        'comment': table['TABLE_COMMENT'],
                        'rows': table['TABLE_ROWS'],
                        'columns': []
                    }
                    
                    # 获取列信息
                    cursor.execute("""
                        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT,
                               IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT,
                               CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY ORDINAL_POSITION
                    """, (self.config.get('database'), table['TABLE_NAME']))
                    columns = cursor.fetchall()
                    
                    for col in columns:
                        table_info['columns'].append({
                            'name': col['COLUMN_NAME'],
                            'type': col['DATA_TYPE'],
                            'comment': col['COLUMN_COMMENT'],
                            'nullable': col['IS_NULLABLE'] == 'YES',
                            'is_primary': col['COLUMN_KEY'] == 'PRI',
                            'default': col['COLUMN_DEFAULT'],
                            'length': col['CHARACTER_MAXIMUM_LENGTH'],
                            'precision': col['NUMERIC_PRECISION']
                        })
                    
                    schema['tables'].append(table_info)
        finally:
            conn.close()
        
        return schema
```

## 第20页

```python
    def execute(self, sql: str, params: tuple = None) -> List[Dict]:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()
    
    def close(self):
        if self.connection:
            self.connection.close()


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self):
        self.connection = psycopg2.connect(
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 5432),
            user=self.config.get('user'),
            password=self.config.get('password'),
            database=self.config.get('database')
        )
        return self.connection
    
    def test(self) -> bool:
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f'PostgreSQL连接测试失败: {str(e)}')
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        schema = {'tables': []}
        conn = self.connect()
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                table_info = {'name': table_name, 'columns': []}
                # ... 获取列信息
                schema['tables'].append(table_info)
            
            cursor.close()
        finally:
            conn.close()
        
        return schema
```

## 第21页

```python
    def execute(self, sql: str, params: tuple = None) -> List[Dict]:
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()
    
    def close(self):
        if self.connection:
            self.connection.close()


class ConnectorFactory:
    """连接器工厂"""
    
    CONNECTOR_MAP = {
        SourceType.MYSQL: MySQLConnector,
        SourceType.POSTGRESQL: PostgreSQLConnector,
    }
    
    @classmethod
    def create(cls, source: DataSource) -> BaseConnector:
        """创建连接器实例"""
        connector_class = cls.CONNECTOR_MAP.get(source.source_type)
        if not connector_class:
            raise ValueError(f'不支持的数据源类型: {source.source_type}')
        return connector_class(source.connection_config)


# 文件: app/services/domain_service.py
"""
主题域服务模块
"""
from typing import List, Optional, Dict, Any

from app import db
from app.models.domain import DataDomain, DataEntity, EntityField, DomainType
from app.utils.pagination import Pagination


class DomainService:
    """主题域服务类"""
    
    def create_domain(
        self,
        name: str,
        code: str,
        domain_type: DomainType,
        description: str = None,
        parent_id: str = None,
        owner_id: str = None
    ) -> DataDomain:
        """创建主题域"""
        # 计算层级
        level = 1
        path = f'/{code}'
        
        if parent_id:
            parent = DataDomain.query.get(parent_id)
            if parent:
                level = parent.level + 1
                path = f'{parent.path}/{code}'
```

## 第22页

```python
        domain = DataDomain(
            name=name,
            code=code,
            domain_type=domain_type,
            description=description,
            parent_id=parent_id,
            owner_id=owner_id,
            level=level,
            path=path
        )
        db.session.add(domain)
        db.session.commit()
        return domain
    
    def get_domain_tree(self) -> List[Dict]:
        """获取域树结构"""
        roots = DataDomain.query.filter(
            DataDomain.parent_id.is_(None),
            DataDomain.is_active == True
        ).order_by(DataDomain.sort_order).all()
        
        return [d.to_dict(include_children=True) for d in roots]
    
    def create_entity(
        self,
        name: str,
        code: str,
        domain_id: str,
        entity_type: str = 'table',
        description: str = None,
        name_en: str = None,
        owner_id: str = None
    ) -> DataEntity:
        """创建数据实体"""
        entity = DataEntity(
            name=name,
            code=code,
            domain_id=domain_id,
            entity_type=entity_type,
            description=description,
            name_en=name_en,
            owner_id=owner_id
        )
        db.session.add(entity)
        db.session.commit()
        return entity
    
    def add_entity_field(
        self,
        entity_id: str,
        name: str,
        data_type: str,
        description: str = None,
        name_en: str = None,
        is_primary: bool = False,
        is_nullable: bool = True,
        length: int = None
    ) -> EntityField:
        """添加实体字段"""
        # 获取排序序号
        max_order = db.session.query(db.func.max(EntityField.sort_order)).filter_by(
            entity_id=entity_id
        ).scalar() or 0
```

## 第23页

```python
        field = EntityField(
            entity_id=entity_id,
            name=name,
            data_type=data_type,
            description=description,
            name_en=name_en,
            is_primary=is_primary,
            is_nullable=is_nullable,
            length=length,
            sort_order=max_order + 1
        )
        db.session.add(field)
        db.session.commit()
        return field
    
    def list_entities(
        self,
        domain_id: str = None,
        status: str = None,
        keyword: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """获取实体列表"""
        query = DataEntity.query
        
        if domain_id:
            query = query.filter(DataEntity.domain_id == domain_id)
        
        if status:
            query = query.filter(DataEntity.status == status)
        
        if keyword:
            query = query.filter(
                db.or_(
                    DataEntity.name.ilike(f'%{keyword}%'),
                    DataEntity.code.ilike(f'%{keyword}%')
                )
            )
        
        query = query.order_by(DataEntity.created_at.desc())
        
        return Pagination(query, page, per_page)


# 文件: app/services/service_service.py
"""
数据服务服务模块
"""
import secrets
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from app import db
from app.models.service import (
    DataService, ServiceSubscription, ServiceCallLog,
    ServiceType, ServiceStatus
)
from app.utils.pagination import Pagination
```

## 第24页

```python
class DataServiceService:
    """数据服务服务类"""
    
    def create_service(
        self,
        name: str,
        code: str,
        service_type: ServiceType,
        owner_id: str,
        description: str = None,
        api_path: str = None,
        api_method: str = 'GET',
        domain_id: str = None
    ) -> DataService:
        """创建数据服务"""
        service = DataService(
            name=name,
            code=code,
            service_type=service_type,
            owner_id=owner_id,
            description=description,
            api_path=api_path or f'/api/data/{code}',
            api_method=api_method,
            domain_id=domain_id
        )
        db.session.add(service)
        db.session.commit()
        return service
    
    def update_service_schema(
        self,
        service_id: str,
        request_schema: Dict = None,
        response_schema: Dict = None,
        source_config: Dict = None
    ) -> DataService:
        """更新服务Schema"""
        service = DataService.query.get_or_404(service_id)
        
        if request_schema:
            service.request_schema = request_schema
        if response_schema:
            service.response_schema = response_schema
        if source_config:
            service.source_config = source_config
        
        db.session.commit()
        return service
    
    def publish_service(self, service_id: str) -> DataService:
        """发布服务"""
        service = DataService.query.get_or_404(service_id)
        service.publish()
        return service
    
    def offline_service(self, service_id: str) -> DataService:
        """下线服务"""
        service = DataService.query.get_or_404(service_id)
        service.offline()
        return service
```

## 第25页

```python
    def subscribe_service(
        self,
        service_id: str,
        subscriber_id: str,
        daily_quota: int = 10000
    ) -> ServiceSubscription:
        """订阅服务"""
        # 生成AppKey和AppSecret
        app_key = f'ak_{secrets.token_hex(16)}'
        app_secret = secrets.token_hex(32)
        
        subscription = ServiceSubscription(
            service_id=service_id,
            subscriber_id=subscriber_id,
            app_key=app_key,
            app_secret=hashlib.sha256(app_secret.encode()).hexdigest(),
            daily_quota=daily_quota,
            status='pending'
        )
        db.session.add(subscription)
        db.session.commit()
        
        # 返回时需要明文secret（仅此一次）
        subscription._plain_secret = app_secret
        return subscription
    
    def approve_subscription(
        self,
        subscription_id: str,
        approver_id: str
    ) -> ServiceSubscription:
        """审批订阅"""
        subscription = ServiceSubscription.query.get_or_404(subscription_id)
        subscription.status = 'approved'
        subscription.approved_at = datetime.utcnow()
        subscription.approved_by = approver_id
        db.session.commit()
        return subscription
    
    def call_service(
        self,
        service: DataService,
        subscription: ServiceSubscription,
        params: Dict[str, Any],
        client_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """调用服务"""
        start_time = datetime.utcnow()
        
        try:
            # 检查配额
            if subscription.used_quota >= subscription.daily_quota:
                raise ValueError('已超出每日调用配额')
            
            # 执行服务逻辑
            result = self._execute_service(service, params)
            
            # 记录调用日志
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._log_call(service, subscription, params, result, 200, response_time, client_info)
```

## 第26页

```python
            # 更新统计
            service.call_count += 1
            service.success_count += 1
            subscription.used_quota += 1
            
            # 更新平均响应时间
            total_time = service.avg_response_time * (service.call_count - 1) + response_time
            service.avg_response_time = total_time / service.call_count
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._log_call(service, subscription, params, {'error': str(e)}, 500, response_time, client_info)
            service.call_count += 1
            db.session.commit()
            raise
    
    def _execute_service(self, service: DataService, params: Dict) -> Dict[str, Any]:
        """执行服务逻辑"""
        source_type = service.source_type
        source_config = service.source_config
        
        if source_type == 'sql':
            return self._execute_sql_service(source_config, params)
        elif source_type == 'entity':
            return self._execute_entity_service(source_config, params)
        else:
            raise ValueError(f'不支持的数据源类型: {source_type}')
    
    def _execute_sql_service(self, config: Dict, params: Dict) -> Dict[str, Any]:
        """执行SQL服务"""
        from app.models.datasource import DataSource
        from app.services.connector import ConnectorFactory
        
        source_id = config.get('source_id')
        sql_template = config.get('sql')
        
        # 参数替换
        sql = sql_template
        for key, value in params.items():
            sql = sql.replace(f'{{{key}}}', str(value))
        
        source = DataSource.query.get(source_id)
        connector = ConnectorFactory.create(source)
        
        data = connector.execute(sql)
        
        return {'data': data, 'count': len(data)}
```

## 第27页

```python
    def _execute_entity_service(self, config: Dict, params: Dict) -> Dict[str, Any]:
        """执行实体服务"""
        from app.models.domain import DataEntity
        from app.models.datasource import DataSource
        from app.services.connector import ConnectorFactory
        
        entity_id = config.get('entity_id')
        fields = config.get('fields', ['*'])
        
        entity = DataEntity.query.get(entity_id)
        if not entity or not entity.physical_table:
            raise ValueError('实体未配置物理表')
        
        # 构建查询SQL
        field_list = ', '.join(fields) if fields != ['*'] else '*'
        sql = f'SELECT {field_list} FROM {entity.physical_table}'
        
        # 添加条件
        conditions = []
        for key, value in params.items():
            conditions.append(f"{key} = '{value}'")
        
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        
        # 获取数据源并执行
        source = entity.domain.sources.first()
        if not source:
            raise ValueError('未找到关联数据源')
        
        connector = ConnectorFactory.create(source)
        data = connector.execute(sql)
        
        return {'data': data, 'count': len(data)}
    
    def _log_call(
        self,
        service: DataService,
        subscription: ServiceSubscription,
        params: Dict,
        result: Dict,
        response_code: int,
        response_time: int,
        client_info: Dict
    ):
        """记录调用日志"""
        log = ServiceCallLog(
            service_id=service.id,
            subscription_id=subscription.id,
            request_method=service.api_method,
            request_path=service.api_path,
            request_params=params,
            response_code=response_code,
            response_body=str(result)[:1000],  # 截断
            response_time_ms=response_time,
            client_ip=client_info.get('ip'),
            user_agent=client_info.get('user_agent')
        )
        db.session.add(log)
```

## 第28页

```python
# 文件: app/services/indicator_service.py
"""
指标服务模块
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from app import db
from app.models.indicator import (
    Indicator, IndicatorDimension, Dimension,
    IndicatorType, AggregationType
)
from app.utils.pagination import Pagination


class IndicatorService:
    """指标服务类"""
    
    def create_indicator(
        self,
        name: str,
        code: str,
        indicator_type: IndicatorType,
        owner_id: str,
        description: str = None,
        name_en: str = None,
        domain_id: str = None,
        business_definition: str = None,
        calculation_formula: str = None,
        aggregation_type: AggregationType = None,
        source_field: str = None,
        entity_id: str = None,
        data_type: str = 'decimal',
        unit: str = None
    ) -> Indicator:
        """创建指标"""
        indicator = Indicator(
            name=name,
            code=code,
            indicator_type=indicator_type,
            owner_id=owner_id,
            description=description,
            name_en=name_en,
            domain_id=domain_id,
            business_definition=business_definition,
            calculation_formula=calculation_formula,
            aggregation_type=aggregation_type,
            source_field=source_field,
            entity_id=entity_id,
            data_type=data_type,
            unit=unit
        )
        db.session.add(indicator)
        db.session.commit()
        return indicator
    
    def add_dimension(
        self,
        indicator_id: str,
        dimension_id: str,
        is_required: bool = False
    ) -> IndicatorDimension:
        """添加指标维度"""
        relation = IndicatorDimension(
            indicator_id=indicator_id,
            dimension_id=dimension_id,
            is_required=is_required
        )
        db.session.add(relation)
        db.session.commit()
        return relation
```

## 第29页

```python
    def create_dimension(
        self,
        name: str,
        code: str,
        dimension_type: str = 'normal',
        description: str = None,
        name_en: str = None,
        entity_id: str = None,
        domain_id: str = None,
        time_granularity: str = None
    ) -> Dimension:
        """创建维度"""
        dimension = Dimension(
            name=name,
            code=code,
            dimension_type=dimension_type,
            description=description,
            name_en=name_en,
            entity_id=entity_id,
            domain_id=domain_id,
            time_granularity=time_granularity
        )
        db.session.add(dimension)
        db.session.commit()
        return dimension
    
    def list_indicators(
        self,
        domain_id: str = None,
        indicator_type: IndicatorType = None,
        status: str = None,
        keyword: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """获取指标列表"""
        query = Indicator.query
        
        if domain_id:
            query = query.filter(Indicator.domain_id == domain_id)
        
        if indicator_type:
            query = query.filter(Indicator.indicator_type == indicator_type)
        
        if status:
            query = query.filter(Indicator.status == status)
        
        if keyword:
            query = query.filter(
                db.or_(
                    Indicator.name.ilike(f'%{keyword}%'),
                    Indicator.code.ilike(f'%{keyword}%')
                )
            )
        
        query = query.order_by(Indicator.created_at.desc())
        
        return Pagination(query, page, per_page)
```

## 第30页

```python
    def calculate_indicator(
        self,
        indicator_id: str,
        dimension_values: Dict[str, Any] = None,
        time_range: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """计算指标值"""
        indicator = Indicator.query.get_or_404(indicator_id)
        
        if indicator.indicator_type == IndicatorType.ATOMIC:
            return self._calculate_atomic(indicator, dimension_values, time_range)
        elif indicator.indicator_type == IndicatorType.DERIVED:
            return self._calculate_derived(indicator, dimension_values, time_range)
        elif indicator.indicator_type == IndicatorType.COMPOSITE:
            return self._calculate_composite(indicator, dimension_values, time_range)
    
    def _calculate_atomic(
        self,
        indicator: Indicator,
        dimension_values: Dict,
        time_range: Dict
    ) -> Dict[str, Any]:
        """计算原子指标"""
        from app.services.connector import ConnectorFactory
        
        entity = indicator.entity
        if not entity:
            raise ValueError('指标未关联实体')
        
        source = entity.domain.sources.first()
        if not source:
            raise ValueError('未找到数据源')
        
        # 构建聚合SQL
        agg_func = indicator.aggregation_type.value.upper()
        field = indicator.source_field
        table = entity.physical_table
        
        sql = f'SELECT {agg_func}({field}) as value FROM {table}'
        
        # 添加维度条件
        conditions = []
        if dimension_values:
            for dim, value in dimension_values.items():
                conditions.append(f"{dim} = '{value}'")
        
        # 添加时间条件
        if time_range:
            if time_range.get('start'):
                conditions.append(f"created_at >= '{time_range['start']}'")
            if time_range.get('end'):
                conditions.append(f"created_at <= '{time_range['end']}'")
        
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        
        connector = ConnectorFactory.create(source)
        result = connector.execute(sql)
        
        return {
            'indicator_id': indicator.id,
            'indicator_name': indicator.name,
            'value': result[0]['value'] if result else 0,
            'unit': indicator.unit
        }
```

---

**datacore数据中台系统 V1.0 源程序 前30页 完**

*第1页 至 第30页*

