# AIGC创作平台系统 V1.0 源程序代码

## 第1页

```python
# -*- coding: utf-8 -*-
"""
AIGC创作平台系统 V1.0
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
        config_name: 配置名称，默认从环境变量获取
        
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
```

## 第2页

```python
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'warning'
    
    # 初始化Redis连接
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    
    # 初始化Celery
    celery.conf.update(app.config)
    
    # 注册蓝图
    from app.api import api_bp
    from app.auth import auth_bp
    from app.content import content_bp
    from app.workflow import workflow_bp
    from app.asset import asset_bp
    from app.admin import admin_bp
    
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(content_bp, url_prefix='/content')
    app.register_blueprint(workflow_bp, url_prefix='/workflow')
    app.register_blueprint(asset_bp, url_prefix='/asset')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册请求钩子
    register_request_hooks(app)
    
    # 配置日志
    setup_logging(app)
    
    return app


def register_error_handlers(app):
    """注册全局错误处理器"""
    from app.errors import (
        handle_400_error,
        handle_401_error,
        handle_403_error,
        handle_404_error,
        handle_500_error
    )
    
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(401, handle_401_error)
```

## 第3页

```python
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)


def register_request_hooks(app):
    """注册请求钩子"""
    from flask import g, request
    from app.models import User
    import time
    
    @app.before_request
    def before_request():
        g.request_start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'request_start_time'):
            elapsed = time.time() - g.request_start_time
            response.headers['X-Response-Time'] = f'{elapsed:.3f}s'
        response.headers['X-Request-ID'] = g.get('request_id', '')
        return response


def setup_logging(app):
    """配置应用日志"""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )
    
    # 文件日志处理器
    if app.config.get('LOG_FILE'):
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)


# 文件: app/models/user.py
"""
用户模型模块
"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
```

## 第4页

```python
from app import db, login_manager


class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    permissions = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def has_permission(self, permission):
        """检查角色是否具有指定权限"""
        return self.permissions.get(permission, False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    nickname = db.Column(db.String(64))
    avatar_url = db.Column(db.String(512))
    phone = db.Column(db.String(20))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
```

## 第5页

```python
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    contents = db.relationship('Content', backref='creator', lazy='dynamic')
    workflows = db.relationship('Workflow', backref='owner', lazy='dynamic')
    assets = db.relationship('Asset', backref='uploader', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def password(self):
        raise AttributeError('密码不可读取')
    
    @password.setter
    def password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def can(self, permission):
        """检查用户是否具有指定权限"""
        return self.role is not None and self.role.has_permission(permission)
    
    def generate_token(self, expiration=3600):
        """生成JWT令牌"""
        from app.utils.auth import generate_jwt_token
        return generate_jwt_token(self.id, expiration)
    
    @staticmethod
    def verify_token(token):
        """验证JWT令牌"""
        from app.utils.auth import verify_jwt_token
        data = verify_jwt_token(token)
        if data:
            return User.query.get(data.get('user_id'))
        return None
    
    def to_dict(self, include_email=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar_url': self.avatar_url,
```

## 第6页

```python
            'role': self.role.name if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
            data['phone'] = self.phone
        return data


@login_manager.user_loader
def load_user(user_id):
    """用户加载回调"""
    return User.query.get(user_id)


class Department(db.Model):
    """部门模型"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(32), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    manager_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    description = db.Column(db.String(256))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    children = db.relationship('Department', backref=db.backref('parent', remote_side=[id]))
    users = db.relationship('User', backref='department', foreign_keys='User.department_id')
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def get_ancestors(self):
        """获取所有祖先部门"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """获取所有后代部门"""
        descendants = []
```

## 第7页

```python
        def collect_descendants(dept):
            for child in dept.children:
                descendants.append(child)
                collect_descendants(child)
        collect_descendants(self)
        return descendants
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active
        }
        if include_children:
            data['children'] = [c.to_dict(include_children=True) for c in self.children]
        return data


# 文件: app/models/content.py
"""
内容模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    MIXED = 'mixed'


class ContentStatus(Enum):
    """内容状态枚举"""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
```

## 第8页

```python
class Content(db.Model):
    """内容模型"""
    __tablename__ = 'contents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(256), nullable=False)
    content_type = db.Column(db.Enum(ContentType), default=ContentType.TEXT)
    status = db.Column(db.Enum(ContentStatus), default=ContentStatus.DRAFT)
    body = db.Column(db.Text)
    summary = db.Column(db.String(512))
    cover_image = db.Column(db.String(512))
    tags = db.Column(db.JSON, default=list)
    metadata = db.Column(db.JSON, default=dict)
    
    # 创作相关
    prompt = db.Column(db.Text)
    model_name = db.Column(db.String(64))
    generation_params = db.Column(db.JSON, default=dict)
    
    # 关联关系
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'))
    
    # 审核相关
    reviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    review_comment = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)
    
    # 发布相关
    published_at = db.Column(db.DateTime)
    publish_channels = db.Column(db.JSON, default=list)
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    versions = db.relationship('ContentVersion', backref='content', lazy='dynamic')
    attachments = db.relationship('ContentAttachment', backref='content', lazy='dynamic')
    comments = db.relationship('ContentComment', backref='content', lazy='dynamic')
    
    def __repr__(self):
        return f'<Content {self.title}>'
```

## 第9页

```python
    def submit_for_review(self):
        """提交审核"""
        if self.status != ContentStatus.DRAFT:
            raise ValueError('只有草稿状态可以提交审核')
        self.status = ContentStatus.PENDING
        db.session.commit()
    
    def approve(self, reviewer_id, comment=None):
        """审核通过"""
        if self.status != ContentStatus.PENDING:
            raise ValueError('只有待审核状态可以审批')
        self.status = ContentStatus.APPROVED
        self.reviewer_id = reviewer_id
        self.review_comment = comment
        self.reviewed_at = datetime.utcnow()
        db.session.commit()
    
    def reject(self, reviewer_id, comment):
        """审核驳回"""
        if self.status != ContentStatus.PENDING:
            raise ValueError('只有待审核状态可以驳回')
        self.status = ContentStatus.REJECTED
        self.reviewer_id = reviewer_id
        self.review_comment = comment
        self.reviewed_at = datetime.utcnow()
        db.session.commit()
    
    def publish(self, channels=None):
        """发布内容"""
        if self.status != ContentStatus.APPROVED:
            raise ValueError('只有审核通过的内容可以发布')
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        if channels:
            self.publish_channels = channels
        db.session.commit()
    
    def archive(self):
        """归档内容"""
        self.status = ContentStatus.ARCHIVED
        db.session.commit()
    
    def create_version(self, comment=None):
        """创建版本快照"""
        version = ContentVersion(
            content_id=self.id,
            version_number=self.versions.count() + 1,
            title=self.title,
            body=self.body,
            metadata=self.metadata,
            comment=comment
        )
        db.session.add(version)
        db.session.commit()
        return version
```

## 第10页

```python
    def to_dict(self, include_body=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type.value,
            'status': self.status.value,
            'summary': self.summary,
            'cover_image': self.cover_image,
            'tags': self.tags,
            'creator': self.creator.to_dict() if self.creator else None,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_body:
            data['body'] = self.body
            data['prompt'] = self.prompt
            data['model_name'] = self.model_name
        return data


class ContentVersion(db.Model):
    """内容版本模型"""
    __tablename__ = 'content_versions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = db.Column(db.String(36), db.ForeignKey('contents.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256))
    body = db.Column(db.Text)
    metadata = db.Column(db.JSON, default=dict)
    comment = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'version_number': self.version_number,
            'title': self.title,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }


class ContentAttachment(db.Model):
    """内容附件模型"""
    __tablename__ = 'content_attachments'
```

## 第11页

```python
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = db.Column(db.String(36), db.ForeignKey('contents.id'), nullable=False)
    file_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(64))
    mime_type = db.Column(db.String(128))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type
        }


# 文件: app/models/workflow.py
"""
工作流模型模块
"""
import uuid
from datetime import datetime
from enum import Enum

from app import db


class WorkflowStatus(Enum):
    """工作流状态"""
    DRAFT = 'draft'
    ACTIVE = 'active'
    PAUSED = 'paused'
    ARCHIVED = 'archived'


class TaskStatus(Enum):
    """任务状态"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
```

## 第12页

```python
class Workflow(db.Model):
    """工作流模型"""
    __tablename__ = 'workflows'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    
    # 工作流定义
    definition = db.Column(db.JSON, default=dict)
    variables = db.Column(db.JSON, default=dict)
    
    # 模板相关
    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.String(36), db.ForeignKey('workflows.id'))
    
    # 关联
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # 统计
    run_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tasks = db.relationship('WorkflowTask', backref='workflow', lazy='dynamic')
    executions = db.relationship('WorkflowExecution', backref='workflow', lazy='dynamic')
    
    def __repr__(self):
        return f'<Workflow {self.name}>'
    
    def activate(self):
        """激活工作流"""
        if not self.definition:
            raise ValueError('工作流定义不能为空')
        self.status = WorkflowStatus.ACTIVE
        db.session.commit()
    
    def pause(self):
        """暂停工作流"""
        self.status = WorkflowStatus.PAUSED
        db.session.commit()
    
    def archive(self):
        """归档工作流"""
        self.status = WorkflowStatus.ARCHIVED
        db.session.commit()
```

## 第13页

```python
    def execute(self, params=None):
        """执行工作流"""
        if self.status != WorkflowStatus.ACTIVE:
            raise ValueError('只有激活状态的工作流可以执行')
        
        execution = WorkflowExecution(
            workflow_id=self.id,
            params=params or {},
            status=TaskStatus.PENDING
        )
        db.session.add(execution)
        db.session.commit()
        
        # 触发异步执行
        from app.tasks.workflow import execute_workflow
        execute_workflow.delay(execution.id)
        
        return execution
    
    def to_dict(self, include_definition=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'is_template': self.is_template,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'owner': self.owner.to_dict() if self.owner else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_definition:
            data['definition'] = self.definition
            data['variables'] = self.variables
        return data


class WorkflowTask(db.Model):
    """工作流任务节点模型"""
    __tablename__ = 'workflow_tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    task_type = db.Column(db.String(64), nullable=False)
    config = db.Column(db.JSON, default=dict)
    position = db.Column(db.JSON, default=dict)  # 画布位置
    sort_order = db.Column(db.Integer, default=0)
    
    # 输入输出定义
    inputs = db.Column(db.JSON, default=list)
    outputs = db.Column(db.JSON, default=list)
```

## 第14页

```python
    # 条件与分支
    condition = db.Column(db.Text)
    next_tasks = db.Column(db.JSON, default=list)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'task_type': self.task_type,
            'config': self.config,
            'position': self.position,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'condition': self.condition,
            'next_tasks': self.next_tasks
        }


class WorkflowExecution(db.Model):
    """工作流执行记录模型"""
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    params = db.Column(db.JSON, default=dict)
    result = db.Column(db.JSON, default=dict)
    error_message = db.Column(db.Text)
    
    # 执行信息
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    
    # 触发者
    triggered_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    trigger_type = db.Column(db.String(32), default='manual')  # manual, schedule, api
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 任务执行记录
    task_executions = db.relationship('TaskExecution', backref='workflow_execution', lazy='dynamic')
    
    def start(self):
        """开始执行"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        db.session.commit()
```

## 第15页

```python
    def complete(self, result=None):
        """完成执行"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.result = result or {}
        
        # 更新工作流统计
        self.workflow.run_count += 1
        self.workflow.success_count += 1
        db.session.commit()
    
    def fail(self, error_message):
        """执行失败"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.error_message = error_message
        
        # 更新工作流统计
        self.workflow.run_count += 1
        db.session.commit()
    
    def cancel(self):
        """取消执行"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'status': self.status.value,
            'params': self.params,
            'result': self.result,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'trigger_type': self.trigger_type,
            'created_at': self.created_at.isoformat()
        }


class TaskExecution(db.Model):
    """任务执行记录模型"""
    __tablename__ = 'task_executions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

## 第16页

```python
    execution_id = db.Column(db.String(36), db.ForeignKey('workflow_executions.id'), nullable=False)
    task_id = db.Column(db.String(36), db.ForeignKey('workflow_tasks.id'), nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    inputs = db.Column(db.JSON, default=dict)
    outputs = db.Column(db.JSON, default=dict)
    error_message = db.Column(db.Text)
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    retry_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status.value,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'retry_count': self.retry_count
        }


# 文件: app/models/asset.py
"""
资产模型模块
"""
import uuid
import hashlib
from datetime import datetime
from enum import Enum

from app import db


class AssetType(Enum):
    """资产类型"""
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    TEMPLATE = 'template'
    MODEL = 'model'
    OTHER = 'other'
```

## 第17页

```python
class AssetStatus(Enum):
    """资产状态"""
    UPLOADING = 'uploading'
    PROCESSING = 'processing'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    DELETED = 'deleted'


class Asset(db.Model):
    """资产模型"""
    __tablename__ = 'assets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    asset_type = db.Column(db.Enum(AssetType), default=AssetType.OTHER)
    status = db.Column(db.Enum(AssetStatus), default=AssetStatus.UPLOADING)
    
    # 文件信息
    file_path = db.Column(db.String(512), nullable=False)
    file_name = db.Column(db.String(256))
    file_size = db.Column(db.BigInteger)
    mime_type = db.Column(db.String(128))
    file_hash = db.Column(db.String(64), index=True)
    
    # 媒体元数据
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration = db.Column(db.Float)  # 视频/音频时长（秒）
    
    # 缩略图
    thumbnail_path = db.Column(db.String(512))
    preview_path = db.Column(db.String(512))
    
    # 标签与分类
    tags = db.Column(db.JSON, default=list)
    category_id = db.Column(db.Integer, db.ForeignKey('asset_categories.id'))
    
    # 使用统计
    use_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    
    # 版权信息
    copyright_info = db.Column(db.JSON, default=dict)
    license_type = db.Column(db.String(64))
    
    # 关联
    uploader_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 第18页

```python
    def __repr__(self):
        return f'<Asset {self.name}>'
    
    @staticmethod
    def calculate_hash(file_path):
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def increment_use_count(self):
        """增加使用计数"""
        self.use_count += 1
        db.session.commit()
    
    def archive(self):
        """归档资产"""
        self.status = AssetStatus.ARCHIVED
        db.session.commit()
    
    def soft_delete(self):
        """软删除资产"""
        self.status = AssetStatus.DELETED
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'asset_type': self.asset_type.value,
            'status': self.status.value,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumbnail_path': self.thumbnail_path,
            'tags': self.tags,
            'use_count': self.use_count,
            'uploader': self.uploader.to_dict() if self.uploader else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AssetCategory(db.Model):
    """资产分类模型"""
    __tablename__ = 'asset_categories'
```

## 第19页

```python
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(32), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('asset_categories.id'))
    description = db.Column(db.String(256))
    icon = db.Column(db.String(64))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    children = db.relationship('AssetCategory', backref=db.backref('parent', remote_side=[id]))
    assets = db.relationship('Asset', backref='category', lazy='dynamic')
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'description': self.description,
            'icon': self.icon,
            'sort_order': self.sort_order
        }
        if include_children:
            data['children'] = [c.to_dict(include_children=True) for c in self.children]
        return data


# 文件: app/services/content_service.py
"""
内容服务模块
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from app import db
from app.models.content import Content, ContentType, ContentStatus, ContentVersion
from app.models.user import User
from app.services.ai_service import AIService
from app.utils.pagination import Pagination


class ContentService:
    """内容服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
```

## 第20页

```python
    def create_content(
        self,
        title: str,
        creator_id: str,
        content_type: ContentType = ContentType.TEXT,
        body: str = None,
        summary: str = None,
        tags: List[str] = None,
        project_id: str = None,
        **kwargs
    ) -> Content:
        """
        创建内容
        
        Args:
            title: 标题
            creator_id: 创建者ID
            content_type: 内容类型
            body: 内容正文
            summary: 摘要
            tags: 标签列表
            project_id: 项目ID
            
        Returns:
            创建的内容对象
        """
        content = Content(
            title=title,
            creator_id=creator_id,
            content_type=content_type,
            body=body,
            summary=summary,
            tags=tags or [],
            project_id=project_id,
            **kwargs
        )
        db.session.add(content)
        db.session.commit()
        return content
    
    def update_content(
        self,
        content_id: str,
        **kwargs
    ) -> Content:
        """
        更新内容
        
        Args:
            content_id: 内容ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的内容对象
        """
        content = Content.query.get_or_404(content_id)
```

## 第21页

```python
        # 创建版本快照
        if kwargs.get('body') and kwargs['body'] != content.body:
            content.create_version(comment='自动保存版本')
        
        for key, value in kwargs.items():
            if hasattr(content, key):
                setattr(content, key, value)
        
        db.session.commit()
        return content
    
    def delete_content(self, content_id: str, soft_delete: bool = True) -> bool:
        """
        删除内容
        
        Args:
            content_id: 内容ID
            soft_delete: 是否软删除
            
        Returns:
            是否删除成功
        """
        content = Content.query.get_or_404(content_id)
        
        if soft_delete:
            content.archive()
        else:
            db.session.delete(content)
            db.session.commit()
        
        return True
    
    def get_content(self, content_id: str) -> Optional[Content]:
        """获取单个内容"""
        return Content.query.get(content_id)
    
    def list_contents(
        self,
        creator_id: str = None,
        content_type: ContentType = None,
        status: ContentStatus = None,
        project_id: str = None,
        tags: List[str] = None,
        keyword: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """
        获取内容列表
        
        Args:
            creator_id: 创建者ID
            content_type: 内容类型
            status: 状态
            project_id: 项目ID
```

## 第22页

```python
            tags: 标签筛选
            keyword: 关键词搜索
            page: 页码
            per_page: 每页数量
            
        Returns:
            分页结果
        """
        query = Content.query
        
        if creator_id:
            query = query.filter(Content.creator_id == creator_id)
        
        if content_type:
            query = query.filter(Content.content_type == content_type)
        
        if status:
            query = query.filter(Content.status == status)
        
        if project_id:
            query = query.filter(Content.project_id == project_id)
        
        if tags:
            for tag in tags:
                query = query.filter(Content.tags.contains([tag]))
        
        if keyword:
            query = query.filter(
                db.or_(
                    Content.title.ilike(f'%{keyword}%'),
                    Content.body.ilike(f'%{keyword}%')
                )
            )
        
        query = query.order_by(Content.created_at.desc())
        
        return Pagination(query, page, per_page)
    
    async def generate_content(
        self,
        prompt: str,
        content_type: ContentType,
        model_name: str = 'gpt-4',
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        使用AI生成内容
        
        Args:
            prompt: 提示词
            content_type: 内容类型
            model_name: 模型名称
            params: 生成参数
            
        Returns:
            生成结果
        """
```

## 第23页

```python
        params = params or {}
        
        if content_type == ContentType.TEXT:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                model=model_name,
                **params
            )
        elif content_type == ContentType.IMAGE:
            result = await self.ai_service.generate_image(
                prompt=prompt,
                model=model_name,
                **params
            )
        else:
            raise ValueError(f'不支持的内容类型: {content_type}')
        
        return result
    
    def submit_for_review(self, content_id: str) -> Content:
        """提交内容审核"""
        content = Content.query.get_or_404(content_id)
        content.submit_for_review()
        return content
    
    def review_content(
        self,
        content_id: str,
        reviewer_id: str,
        approved: bool,
        comment: str = None
    ) -> Content:
        """
        审核内容
        
        Args:
            content_id: 内容ID
            reviewer_id: 审核人ID
            approved: 是否通过
            comment: 审核意见
            
        Returns:
            审核后的内容对象
        """
        content = Content.query.get_or_404(content_id)
        
        if approved:
            content.approve(reviewer_id, comment)
        else:
            if not comment:
                raise ValueError('驳回时必须填写审核意见')
            content.reject(reviewer_id, comment)
        
        return content
```

## 第24页

```python
    def publish_content(
        self,
        content_id: str,
        channels: List[str] = None
    ) -> Content:
        """
        发布内容
        
        Args:
            content_id: 内容ID
            channels: 发布渠道列表
            
        Returns:
            发布后的内容对象
        """
        content = Content.query.get_or_404(content_id)
        content.publish(channels)
        return content
    
    def get_content_stats(self, content_id: str) -> Dict[str, Any]:
        """获取内容统计信息"""
        content = Content.query.get_or_404(content_id)
        return {
            'view_count': content.view_count,
            'like_count': content.like_count,
            'share_count': content.share_count,
            'version_count': content.versions.count(),
            'attachment_count': content.attachments.count()
        }


# 文件: app/services/ai_service.py
"""
AI服务模块
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

import httpx
from openai import AsyncOpenAI

from app.config import settings


logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """AI提供商基类"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成文本"""
        pass
```

## 第25页

```python
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成图像"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI提供商"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_text(
        self,
        prompt: str,
        model: str = 'gpt-4',
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            生成结果
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'model': model
            }
        except Exception as e:
            logger.error(f'OpenAI文本生成失败: {str(e)}')
            return {'success': False, 'error': str(e)}
```

## 第26页

```python
    async def generate_image(
        self,
        prompt: str,
        model: str = 'dall-e-3',
        size: str = '1024x1024',
        quality: str = 'standard',
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 提示词
            model: 模型名称
            size: 图像尺寸
            quality: 图像质量
            n: 生成数量
            
        Returns:
            生成结果
        """
        try:
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                **kwargs
            )
            
            images = [
                {
                    'url': img.url,
                    'revised_prompt': img.revised_prompt
                }
                for img in response.data
            ]
            
            return {
                'success': True,
                'images': images,
                'model': model
            }
        except Exception as e:
            logger.error(f'OpenAI图像生成失败: {str(e)}')
            return {'success': False, 'error': str(e)}


class AIService:
    """AI服务统一接口"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
        }
        self.default_provider = 'openai'
```

## 第27页

```python
    def get_provider(self, provider_name: str = None) -> BaseAIProvider:
        """获取AI提供商"""
        name = provider_name or self.default_provider
        if name not in self.providers:
            raise ValueError(f'不支持的AI提供商: {name}')
        return self.providers[name]
    
    async def generate_text(
        self,
        prompt: str,
        provider: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成文本"""
        ai_provider = self.get_provider(provider)
        return await ai_provider.generate_text(prompt, **kwargs)
    
    async def generate_image(
        self,
        prompt: str,
        provider: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成图像"""
        ai_provider = self.get_provider(provider)
        return await ai_provider.generate_image(prompt, **kwargs)
    
    async def batch_generate(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量生成
        
        Args:
            tasks: 任务列表，每个任务包含type、prompt等参数
            max_concurrent: 最大并发数
            
        Returns:
            生成结果列表
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
                else:
                    return {'success': False, 'error': f'未知任务类型: {task_type}'}
```

## 第28页

```python
        results = await asyncio.gather(
            *[process_task(task) for task in tasks],
            return_exceptions=True
        )
        
        return [
            r if not isinstance(r, Exception) else {'success': False, 'error': str(r)}
            for r in results
        ]


# 文件: app/services/workflow_service.py
"""
工作流服务模块
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app import db
from app.models.workflow import (
    Workflow, WorkflowTask, WorkflowExecution,
    TaskExecution, WorkflowStatus, TaskStatus
)
from app.utils.pagination import Pagination


logger = logging.getLogger(__name__)


class WorkflowService:
    """工作流服务类"""
    
    def create_workflow(
        self,
        name: str,
        owner_id: str,
        description: str = None,
        definition: Dict[str, Any] = None,
        variables: Dict[str, Any] = None,
        is_template: bool = False,
        project_id: str = None
    ) -> Workflow:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            owner_id: 所有者ID
            description: 描述
            definition: 工作流定义
            variables: 变量定义
            is_template: 是否为模板
            project_id: 项目ID
            
        Returns:
            创建的工作流对象
        """
```

## 第29页

```python
        workflow = Workflow(
            name=name,
            owner_id=owner_id,
            description=description,
            definition=definition or {},
            variables=variables or {},
            is_template=is_template,
            project_id=project_id
        )
        db.session.add(workflow)
        db.session.commit()
        return workflow
    
    def update_workflow(
        self,
        workflow_id: str,
        **kwargs
    ) -> Workflow:
        """更新工作流"""
        workflow = Workflow.query.get_or_404(workflow_id)
        
        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        db.session.commit()
        return workflow
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """删除工作流"""
        workflow = Workflow.query.get_or_404(workflow_id)
        workflow.archive()
        return True
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取单个工作流"""
        return Workflow.query.get(workflow_id)
    
    def list_workflows(
        self,
        owner_id: str = None,
        status: WorkflowStatus = None,
        is_template: bool = None,
        project_id: str = None,
        keyword: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """获取工作流列表"""
        query = Workflow.query
        
        if owner_id:
            query = query.filter(Workflow.owner_id == owner_id)
        
        if status:
            query = query.filter(Workflow.status == status)
```

## 第30页

```python
        if is_template is not None:
            query = query.filter(Workflow.is_template == is_template)
        
        if project_id:
            query = query.filter(Workflow.project_id == project_id)
        
        if keyword:
            query = query.filter(
                db.or_(
                    Workflow.name.ilike(f'%{keyword}%'),
                    Workflow.description.ilike(f'%{keyword}%')
                )
            )
        
        query = query.order_by(Workflow.created_at.desc())
        
        return Pagination(query, page, per_page)
    
    def add_task(
        self,
        workflow_id: str,
        name: str,
        task_type: str,
        config: Dict[str, Any] = None,
        position: Dict[str, Any] = None,
        inputs: List[Dict] = None,
        outputs: List[Dict] = None
    ) -> WorkflowTask:
        """添加工作流任务节点"""
        task = WorkflowTask(
            workflow_id=workflow_id,
            name=name,
            task_type=task_type,
            config=config or {},
            position=position or {},
            inputs=inputs or [],
            outputs=outputs or []
        )
        db.session.add(task)
        db.session.commit()
        return task
    
    def execute_workflow(
        self,
        workflow_id: str,
        params: Dict[str, Any] = None,
        triggered_by: str = None,
        trigger_type: str = 'manual'
    ) -> WorkflowExecution:
        """执行工作流"""
        workflow = Workflow.query.get_or_404(workflow_id)
        return workflow.execute(params)
```

---

**AIGC创作平台系统 V1.0 源程序 前30页 完**

*第1页 至 第30页*

