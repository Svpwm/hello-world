# AIGC创作平台系统 V1.0 源程序代码

## 第N-29页

```python
# -*- coding: utf-8 -*-
"""
AIGC创作平台系统 V1.0
Copyright (c) 2024 南京初鑫信息科技有限公司
All Rights Reserved.

文件: app/api/content.py
描述: 内容管理API接口
"""

from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user

from app.services.content_service import ContentService
from app.models.content import ContentType, ContentStatus
from app.utils.decorators import permission_required
from app.utils.validators import validate_json
from app.schemas.content import (
    ContentCreateSchema,
    ContentUpdateSchema,
    ContentQuerySchema
)


content_bp = Blueprint('content', __name__)
content_service = ContentService()


@content_bp.route('/contents', methods=['GET'])
@login_required
def list_contents():
    """
    获取内容列表
    
    Query Parameters:
        - page: 页码
        - per_page: 每页数量
        - content_type: 内容类型
        - status: 状态
        - keyword: 搜索关键词
    """
    schema = ContentQuerySchema()
    params = schema.load(request.args)
    
    pagination = content_service.list_contents(
        creator_id=params.get('creator_id'),
        content_type=params.get('content_type'),
        status=params.get('status'),
        keyword=params.get('keyword'),
        page=params.get('page', 1),
        per_page=params.get('per_page', 20)
    )
```

## 第N-28页

```python
    return jsonify({
        'success': True,
        'data': {
            'items': [item.to_dict(include_body=False) for item in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    })


@content_bp.route('/contents', methods=['POST'])
@login_required
@validate_json(ContentCreateSchema)
def create_content():
    """创建内容"""
    data = g.validated_data
    
    content = content_service.create_content(
        title=data['title'],
        creator_id=current_user.id,
        content_type=ContentType(data.get('content_type', 'text')),
        body=data.get('body'),
        summary=data.get('summary'),
        tags=data.get('tags', []),
        project_id=data.get('project_id')
    )
    
    return jsonify({
        'success': True,
        'data': content.to_dict()
    }), 201


@content_bp.route('/contents/<content_id>', methods=['GET'])
@login_required
def get_content(content_id):
    """获取内容详情"""
    content = content_service.get_content(content_id)
    
    if not content:
        return jsonify({
            'success': False,
            'error': '内容不存在'
        }), 404
    
    # 增加浏览计数
    content.view_count += 1
    
    return jsonify({
        'success': True,
        'data': content.to_dict()
    })
```

## 第N-27页

```python
@content_bp.route('/contents/<content_id>', methods=['PUT'])
@login_required
@validate_json(ContentUpdateSchema)
def update_content(content_id):
    """更新内容"""
    data = g.validated_data
    
    content = content_service.update_content(
        content_id=content_id,
        **data
    )
    
    return jsonify({
        'success': True,
        'data': content.to_dict()
    })


@content_bp.route('/contents/<content_id>', methods=['DELETE'])
@login_required
def delete_content(content_id):
    """删除内容"""
    content_service.delete_content(content_id)
    
    return jsonify({
        'success': True,
        'message': '内容已删除'
    })


@content_bp.route('/contents/<content_id>/submit', methods=['POST'])
@login_required
def submit_content(content_id):
    """提交内容审核"""
    content = content_service.submit_for_review(content_id)
    
    return jsonify({
        'success': True,
        'data': content.to_dict()
    })


@content_bp.route('/contents/<content_id>/review', methods=['POST'])
@login_required
@permission_required('content.review')
def review_content(content_id):
    """审核内容"""
    data = request.get_json()
    
    content = content_service.review_content(
        content_id=content_id,
        reviewer_id=current_user.id,
        approved=data.get('approved', False),
        comment=data.get('comment')
    )
```

## 第N-26页

```python
    return jsonify({
        'success': True,
        'data': content.to_dict()
    })


@content_bp.route('/contents/<content_id>/publish', methods=['POST'])
@login_required
@permission_required('content.publish')
def publish_content(content_id):
    """发布内容"""
    data = request.get_json() or {}
    
    content = content_service.publish_content(
        content_id=content_id,
        channels=data.get('channels')
    )
    
    return jsonify({
        'success': True,
        'data': content.to_dict()
    })


@content_bp.route('/contents/<content_id>/stats', methods=['GET'])
@login_required
def get_content_stats(content_id):
    """获取内容统计"""
    stats = content_service.get_content_stats(content_id)
    
    return jsonify({
        'success': True,
        'data': stats
    })


# 文件: app/api/generation.py
"""
AI生成API接口
"""

from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user

from app.services.ai_service import AIService
from app.services.content_service import ContentService
from app.models.content import ContentType
from app.utils.validators import validate_json
from app.schemas.generation import GenerationRequestSchema


generation_bp = Blueprint('generation', __name__)
ai_service = AIService()
content_service = ContentService()
```

## 第N-25页

```python
@generation_bp.route('/generate/text', methods=['POST'])
@login_required
async def generate_text():
    """
    生成文本内容
    
    Request Body:
        - prompt: 提示词
        - model: 模型名称（可选）
        - max_tokens: 最大token数（可选）
        - temperature: 温度参数（可选）
        - save_as_content: 是否保存为内容（可选）
    """
    data = request.get_json()
    
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({
            'success': False,
            'error': '提示词不能为空'
        }), 400
    
    result = await ai_service.generate_text(
        prompt=prompt,
        model=data.get('model', 'gpt-4'),
        max_tokens=data.get('max_tokens', 2048),
        temperature=data.get('temperature', 0.7)
    )
    
    if not result.get('success'):
        return jsonify({
            'success': False,
            'error': result.get('error', '生成失败')
        }), 500
    
    # 如果需要保存为内容
    if data.get('save_as_content'):
        content = content_service.create_content(
            title=data.get('title', '生成的文本内容'),
            creator_id=current_user.id,
            content_type=ContentType.TEXT,
            body=result['content'],
            prompt=prompt,
            model_name=data.get('model', 'gpt-4'),
            generation_params={
                'max_tokens': data.get('max_tokens', 2048),
                'temperature': data.get('temperature', 0.7)
            }
        )
        result['content_id'] = content.id
    
    return jsonify({
        'success': True,
        'data': result
    })
```

## 第N-24页

```python
@generation_bp.route('/generate/image', methods=['POST'])
@login_required
async def generate_image():
    """
    生成图像内容
    
    Request Body:
        - prompt: 提示词
        - model: 模型名称（可选）
        - size: 图像尺寸（可选）
        - quality: 图像质量（可选）
        - n: 生成数量（可选）
    """
    data = request.get_json()
    
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({
            'success': False,
            'error': '提示词不能为空'
        }), 400
    
    result = await ai_service.generate_image(
        prompt=prompt,
        model=data.get('model', 'dall-e-3'),
        size=data.get('size', '1024x1024'),
        quality=data.get('quality', 'standard'),
        n=data.get('n', 1)
    )
    
    if not result.get('success'):
        return jsonify({
            'success': False,
            'error': result.get('error', '生成失败')
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    })


@generation_bp.route('/generate/batch', methods=['POST'])
@login_required
async def batch_generate():
    """
    批量生成内容
    
    Request Body:
        - tasks: 任务列表
            - type: 任务类型（text/image）
            - prompt: 提示词
            - params: 生成参数（可选）
    """
    data = request.get_json()
    
    tasks = data.get('tasks', [])
    if not tasks:
        return jsonify({
            'success': False,
            'error': '任务列表不能为空'
        }), 400
```

## 第N-23页

```python
    results = await ai_service.batch_generate(
        tasks=tasks,
        max_concurrent=data.get('max_concurrent', 5)
    )
    
    return jsonify({
        'success': True,
        'data': {
            'results': results,
            'total': len(results),
            'success_count': sum(1 for r in results if r.get('success')),
            'fail_count': sum(1 for r in results if not r.get('success'))
        }
    })


# 文件: app/api/workflow.py
"""
工作流API接口
"""

from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user

from app.services.workflow_service import WorkflowService
from app.models.workflow import WorkflowStatus
from app.utils.validators import validate_json
from app.schemas.workflow import (
    WorkflowCreateSchema,
    WorkflowUpdateSchema
)


workflow_bp = Blueprint('workflow', __name__)
workflow_service = WorkflowService()


@workflow_bp.route('/workflows', methods=['GET'])
@login_required
def list_workflows():
    """获取工作流列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    is_template = request.args.get('is_template', type=bool)
    keyword = request.args.get('keyword')
    
    pagination = workflow_service.list_workflows(
        owner_id=request.args.get('owner_id') or current_user.id,
        status=WorkflowStatus(status) if status else None,
        is_template=is_template,
        keyword=keyword,
        page=page,
        per_page=per_page
    )
```

## 第N-22页

```python
    return jsonify({
        'success': True,
        'data': {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    })


@workflow_bp.route('/workflows', methods=['POST'])
@login_required
@validate_json(WorkflowCreateSchema)
def create_workflow():
    """创建工作流"""
    data = g.validated_data
    
    workflow = workflow_service.create_workflow(
        name=data['name'],
        owner_id=current_user.id,
        description=data.get('description'),
        definition=data.get('definition'),
        variables=data.get('variables'),
        is_template=data.get('is_template', False),
        project_id=data.get('project_id')
    )
    
    return jsonify({
        'success': True,
        'data': workflow.to_dict(include_definition=True)
    }), 201


@workflow_bp.route('/workflows/<workflow_id>', methods=['GET'])
@login_required
def get_workflow(workflow_id):
    """获取工作流详情"""
    workflow = workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        return jsonify({
            'success': False,
            'error': '工作流不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': workflow.to_dict(include_definition=True)
    })


@workflow_bp.route('/workflows/<workflow_id>', methods=['PUT'])
@login_required
@validate_json(WorkflowUpdateSchema)
def update_workflow(workflow_id):
    """更新工作流"""
    data = g.validated_data
```

## 第N-21页

```python
    workflow = workflow_service.update_workflow(
        workflow_id=workflow_id,
        **data
    )
    
    return jsonify({
        'success': True,
        'data': workflow.to_dict(include_definition=True)
    })


@workflow_bp.route('/workflows/<workflow_id>', methods=['DELETE'])
@login_required
def delete_workflow(workflow_id):
    """删除工作流"""
    workflow_service.delete_workflow(workflow_id)
    
    return jsonify({
        'success': True,
        'message': '工作流已删除'
    })


@workflow_bp.route('/workflows/<workflow_id>/activate', methods=['POST'])
@login_required
def activate_workflow(workflow_id):
    """激活工作流"""
    workflow = workflow_service.get_workflow(workflow_id)
    workflow.activate()
    
    return jsonify({
        'success': True,
        'data': workflow.to_dict()
    })


@workflow_bp.route('/workflows/<workflow_id>/execute', methods=['POST'])
@login_required
def execute_workflow(workflow_id):
    """执行工作流"""
    data = request.get_json() or {}
    
    execution = workflow_service.execute_workflow(
        workflow_id=workflow_id,
        params=data.get('params'),
        triggered_by=current_user.id,
        trigger_type='manual'
    )
    
    return jsonify({
        'success': True,
        'data': execution.to_dict()
    })
```

## 第N-20页

```python
@workflow_bp.route('/workflows/<workflow_id>/tasks', methods=['POST'])
@login_required
def add_workflow_task(workflow_id):
    """添加工作流任务节点"""
    data = request.get_json()
    
    task = workflow_service.add_task(
        workflow_id=workflow_id,
        name=data['name'],
        task_type=data['task_type'],
        config=data.get('config'),
        position=data.get('position'),
        inputs=data.get('inputs'),
        outputs=data.get('outputs')
    )
    
    return jsonify({
        'success': True,
        'data': task.to_dict()
    }), 201


# 文件: app/api/asset.py
"""
资产管理API接口
"""

import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.services.asset_service import AssetService
from app.models.asset import AssetType, AssetStatus
from app.utils.file_utils import allowed_file, get_file_type


asset_bp = Blueprint('asset', __name__)
asset_service = AssetService()


@asset_bp.route('/assets', methods=['GET'])
@login_required
def list_assets():
    """获取资产列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    asset_type = request.args.get('asset_type')
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword')
    tags = request.args.getlist('tags')
```

## 第N-19页

```python
    pagination = asset_service.list_assets(
        uploader_id=request.args.get('uploader_id'),
        asset_type=AssetType(asset_type) if asset_type else None,
        category_id=category_id,
        keyword=keyword,
        tags=tags,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    })


@asset_bp.route('/assets/upload', methods=['POST'])
@login_required
def upload_asset():
    """上传资产"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': '未找到上传文件'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': '文件名不能为空'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': '不支持的文件类型'
        }), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    file_type = get_file_type(filename)
    
    asset = asset_service.create_asset(
        file=file,
        filename=filename,
        uploader_id=current_user.id,
        name=request.form.get('name', filename),
        description=request.form.get('description'),
        asset_type=AssetType(file_type),
        category_id=request.form.get('category_id', type=int),
        tags=request.form.getlist('tags')
    )
```

## 第N-18页

```python
    return jsonify({
        'success': True,
        'data': asset.to_dict()
    }), 201


@asset_bp.route('/assets/<asset_id>', methods=['GET'])
@login_required
def get_asset(asset_id):
    """获取资产详情"""
    asset = asset_service.get_asset(asset_id)
    
    if not asset:
        return jsonify({
            'success': False,
            'error': '资产不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': asset.to_dict()
    })


@asset_bp.route('/assets/<asset_id>/download', methods=['GET'])
@login_required
def download_asset(asset_id):
    """下载资产"""
    asset = asset_service.get_asset(asset_id)
    
    if not asset:
        return jsonify({
            'success': False,
            'error': '资产不存在'
        }), 404
    
    # 增加下载计数
    asset.download_count += 1
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], asset.file_path)
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=asset.file_name
    )


@asset_bp.route('/assets/<asset_id>', methods=['PUT'])
@login_required
def update_asset(asset_id):
    """更新资产信息"""
    data = request.get_json()
    
    asset = asset_service.update_asset(
        asset_id=asset_id,
        **data
    )
```

## 第N-17页

```python
    return jsonify({
        'success': True,
        'data': asset.to_dict()
    })


@asset_bp.route('/assets/<asset_id>', methods=['DELETE'])
@login_required
def delete_asset(asset_id):
    """删除资产"""
    asset_service.delete_asset(asset_id)
    
    return jsonify({
        'success': True,
        'message': '资产已删除'
    })


# 文件: app/tasks/workflow.py
"""
工作流异步任务模块
"""

import logging
from datetime import datetime
from typing import Dict, Any

from celery import shared_task

from app import db, celery
from app.models.workflow import (
    Workflow, WorkflowTask, WorkflowExecution,
    TaskExecution, TaskStatus
)
from app.services.ai_service import AIService


logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def execute_workflow(self, execution_id: str):
    """
    执行工作流任务
    
    Args:
        execution_id: 执行记录ID
    """
    execution = WorkflowExecution.query.get(execution_id)
    if not execution:
        logger.error(f'执行记录不存在: {execution_id}')
        return
    
    execution.start()
    
    try:
        workflow = execution.workflow
        definition = workflow.definition
```

## 第N-16页

```python
        # 解析工作流定义
        tasks = definition.get('tasks', [])
        connections = definition.get('connections', [])
        
        # 构建任务执行顺序
        task_order = build_task_order(tasks, connections)
        
        # 初始化上下文
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
                raise Exception(f"任务 {task['name']} 执行失败: {task_result.get('error')}")
        
        # 完成执行
        execution.complete(result=context['results'])
        logger.info(f'工作流执行成功: {execution_id}')
        
    except Exception as e:
        logger.error(f'工作流执行失败: {execution_id}, 错误: {str(e)}')
        execution.fail(str(e))
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))


def build_task_order(tasks: list, connections: list) -> list:
    """
    构建任务执行顺序（拓扑排序）
    
    Args:
        tasks: 任务列表
        connections: 连接列表
        
    Returns:
        任务ID列表（按执行顺序）
    """
    # 构建邻接表和入度表
    graph = {t['id']: [] for t in tasks}
    in_degree = {t['id']: 0 for t in tasks}
```

## 第N-15页

```python
    for conn in connections:
        source = conn['source']
        target = conn['target']
        graph[source].append(target)
        in_degree[target] += 1
    
    # 拓扑排序
    queue = [t_id for t_id, degree in in_degree.items() if degree == 0]
    order = []
    
    while queue:
        current = queue.pop(0)
        order.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(order) != len(tasks):
        raise ValueError('工作流存在循环依赖')
    
    return order


def execute_task(execution_id: str, task: dict, context: dict) -> dict:
    """
    执行单个任务
    
    Args:
        execution_id: 执行记录ID
        task: 任务定义
        context: 执行上下文
        
    Returns:
        任务执行结果
    """
    task_execution = TaskExecution(
        execution_id=execution_id,
        task_id=task['id'],
        inputs=resolve_inputs(task.get('inputs', {}), context),
        status=TaskStatus.RUNNING,
        started_at=datetime.utcnow()
    )
    db.session.add(task_execution)
    db.session.commit()
    
    try:
        task_type = task['type']
        config = task.get('config', {})
        inputs = task_execution.inputs
        
        # 根据任务类型执行
        if task_type == 'text_generation':
            result = execute_text_generation(inputs, config)
        elif task_type == 'image_generation':
            result = execute_image_generation(inputs, config)
```

## 第N-14页

```python
        elif task_type == 'data_transform':
            result = execute_data_transform(inputs, config)
        elif task_type == 'condition':
            result = execute_condition(inputs, config, context)
        elif task_type == 'http_request':
            result = execute_http_request(inputs, config)
        else:
            raise ValueError(f'未知的任务类型: {task_type}')
        
        task_execution.status = TaskStatus.COMPLETED
        task_execution.outputs = result
        task_execution.completed_at = datetime.utcnow()
        task_execution.duration_ms = int(
            (task_execution.completed_at - task_execution.started_at).total_seconds() * 1000
        )
        db.session.commit()
        
        return {'success': True, **result}
        
    except Exception as e:
        task_execution.status = TaskStatus.FAILED
        task_execution.error_message = str(e)
        task_execution.completed_at = datetime.utcnow()
        db.session.commit()
        
        return {'success': False, 'error': str(e)}


def resolve_inputs(inputs: dict, context: dict) -> dict:
    """
    解析输入参数，替换变量引用
    
    Args:
        inputs: 输入参数定义
        context: 执行上下文
        
    Returns:
        解析后的输入参数
    """
    resolved = {}
    
    for key, value in inputs.items():
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            # 解析变量引用
            var_path = value[2:-2].strip()
            resolved[key] = get_nested_value(context, var_path)
        else:
            resolved[key] = value
    
    return resolved


def get_nested_value(obj: dict, path: str):
    """获取嵌套字典的值"""
    keys = path.split('.')
    value = obj
```

## 第N-13页

```python
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


def execute_text_generation(inputs: dict, config: dict) -> dict:
    """执行文本生成任务"""
    import asyncio
    
    ai_service = AIService()
    
    prompt = inputs.get('prompt', '')
    model = config.get('model', 'gpt-4')
    max_tokens = config.get('max_tokens', 2048)
    temperature = config.get('temperature', 0.7)
    
    result = asyncio.run(ai_service.generate_text(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    ))
    
    return result


def execute_image_generation(inputs: dict, config: dict) -> dict:
    """执行图像生成任务"""
    import asyncio
    
    ai_service = AIService()
    
    prompt = inputs.get('prompt', '')
    model = config.get('model', 'dall-e-3')
    size = config.get('size', '1024x1024')
    
    result = asyncio.run(ai_service.generate_image(
        prompt=prompt,
        model=model,
        size=size
    ))
    
    return result


def execute_data_transform(inputs: dict, config: dict) -> dict:
    """执行数据转换任务"""
    transform_type = config.get('type', 'mapping')
    data = inputs.get('data')
    
    if transform_type == 'mapping':
        mapping = config.get('mapping', {})
        result = {mapping.get(k, k): v for k, v in data.items()}
```

## 第N-12页

```python
    elif transform_type == 'filter':
        condition = config.get('condition', {})
        result = filter_data(data, condition)
    elif transform_type == 'aggregate':
        fields = config.get('fields', [])
        result = aggregate_data(data, fields)
    else:
        result = data
    
    return {'data': result}


def execute_condition(inputs: dict, config: dict, context: dict) -> dict:
    """执行条件判断任务"""
    condition = config.get('condition', '')
    
    # 简单的条件表达式解析
    result = eval_condition(condition, inputs, context)
    
    return {
        'result': result,
        'branch': 'true' if result else 'false'
    }


def execute_http_request(inputs: dict, config: dict) -> dict:
    """执行HTTP请求任务"""
    import httpx
    
    url = config.get('url', '')
    method = config.get('method', 'GET').upper()
    headers = config.get('headers', {})
    timeout = config.get('timeout', 30)
    
    # 替换URL中的变量
    for key, value in inputs.items():
        url = url.replace(f'{{{key}}}', str(value))
    
    with httpx.Client(timeout=timeout) as client:
        if method == 'GET':
            response = client.get(url, headers=headers, params=inputs)
        elif method == 'POST':
            response = client.post(url, headers=headers, json=inputs)
        elif method == 'PUT':
            response = client.put(url, headers=headers, json=inputs)
        elif method == 'DELETE':
            response = client.delete(url, headers=headers)
        else:
            raise ValueError(f'不支持的HTTP方法: {method}')
    
    return {
        'status_code': response.status_code,
        'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
        'headers': dict(response.headers)
    }
```

## 第N-11页

```python
# 文件: app/utils/validators.py
"""
验证器工具模块
"""

from functools import wraps
from flask import request, g, jsonify
from marshmallow import ValidationError


def validate_json(schema_class):
    """
    JSON请求体验证装饰器
    
    Args:
        schema_class: Marshmallow Schema类
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json_data = request.get_json()
            
            if json_data is None:
                return jsonify({
                    'success': False,
                    'error': '请求体必须是JSON格式'
                }), 400
            
            schema = schema_class()
            
            try:
                g.validated_data = schema.load(json_data)
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'error': '数据验证失败',
                    'details': e.messages
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_query(schema_class):
    """
    查询参数验证装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            
            try:
                g.validated_query = schema.load(request.args)
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'error': '查询参数验证失败',
                    'details': e.messages
                }), 400
```

## 第N-10页

```python
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 文件: app/utils/decorators.py
"""
通用装饰器模块
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user


def permission_required(permission):
    """
    权限验证装饰器
    
    Args:
        permission: 权限标识
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return jsonify({
                    'success': False,
                    'error': '权限不足'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(limit: int, period: int = 60):
    """
    请求频率限制装饰器
    
    Args:
        limit: 限制次数
        period: 时间周期（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app, request
            
            key = f'rate_limit:{request.endpoint}:{current_user.id}'
            redis = current_app.redis
```

## 第N-9页

```python
            current_count = redis.get(key)
            
            if current_count is None:
                redis.setex(key, period, 1)
            elif int(current_count) >= limit:
                return jsonify({
                    'success': False,
                    'error': '请求过于频繁，请稍后再试'
                }), 429
            else:
                redis.incr(key)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cache_response(timeout: int = 300, key_prefix: str = ''):
    """
    响应缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒）
        key_prefix: 缓存键前缀
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app, request
            import hashlib
            import json
            
            # 生成缓存键
            cache_key = f'{key_prefix}:{request.path}:{hashlib.md5(request.query_string).hexdigest()}'
            redis = current_app.redis
            
            # 尝试从缓存获取
            cached = redis.get(cache_key)
            if cached:
                return jsonify(json.loads(cached))
            
            # 执行函数并缓存结果
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                data, status_code = response[0], response[1]
            else:
                data, status_code = response, 200
            
            if status_code == 200:
                redis.setex(cache_key, timeout, json.dumps(data.get_json()))
            
            return response
        return decorated_function
    return decorator
```

## 第N-8页

```python
# 文件: app/utils/pagination.py
"""
分页工具模块
"""

from math import ceil
from typing import List, Any


class Pagination:
    """分页类"""
    
    def __init__(self, query, page: int = 1, per_page: int = 20):
        """
        初始化分页
        
        Args:
            query: SQLAlchemy查询对象
            page: 当前页码
            per_page: 每页数量
        """
        self.query = query
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), 100)
        
        self.total = query.count()
        self.items = query.offset((self.page - 1) * self.per_page).limit(self.per_page).all()
    
    @property
    def pages(self) -> int:
        """总页数"""
        return ceil(self.total / self.per_page) if self.total > 0 else 1
    
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.pages
    
    @property
    def prev_num(self) -> int:
        """上一页页码"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self) -> int:
        """下一页页码"""
        return self.page + 1 if self.has_next else None
    
    def to_dict(self, item_converter=None) -> dict:
        """
        转换为字典
        
        Args:
            item_converter: 项目转换函数
        """
```

## 第N-7页

```python
        items = self.items
        if item_converter:
            items = [item_converter(item) for item in items]
        elif hasattr(self.items[0] if self.items else None, 'to_dict'):
            items = [item.to_dict() for item in self.items]
        
        return {
            'items': items,
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'pages': self.pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next
        }


# 文件: app/utils/file_utils.py
"""
文件工具模块
"""

import os
import uuid
import hashlib
from datetime import datetime
from typing import Tuple, Optional

from PIL import Image
from werkzeug.datastructures import FileStorage


# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'flac', 'aac'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md'}
}


def allowed_file(filename: str) -> bool:
    """检查文件是否允许上传"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    all_extensions = set()
    for extensions in ALLOWED_EXTENSIONS.values():
        all_extensions.update(extensions)
    return ext in all_extensions


def get_file_type(filename: str) -> str:
    """获取文件类型"""
    if '.' not in filename:
        return 'other'
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return 'other'
```

## 第N-6页

```python
def generate_upload_path(filename: str, prefix: str = '') -> str:
    """
    生成上传文件路径
    
    Args:
        filename: 原始文件名
        prefix: 路径前缀
        
    Returns:
        生成的文件路径
    """
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    date_path = datetime.now().strftime('%Y/%m/%d')
    unique_name = f'{uuid.uuid4().hex}.{ext}' if ext else uuid.uuid4().hex
    
    if prefix:
        return f'{prefix}/{date_path}/{unique_name}'
    return f'{date_path}/{unique_name}'


def calculate_file_hash(file: FileStorage) -> str:
    """计算文件MD5哈希"""
    hash_md5 = hashlib.md5()
    file.seek(0)
    for chunk in iter(lambda: file.read(4096), b''):
        hash_md5.update(chunk)
    file.seek(0)
    return hash_md5.hexdigest()


def get_image_dimensions(file_path: str) -> Tuple[int, int]:
    """获取图像尺寸"""
    with Image.open(file_path) as img:
        return img.size


def create_thumbnail(
    source_path: str,
    dest_path: str,
    size: Tuple[int, int] = (200, 200)
) -> str:
    """
    创建缩略图
    
    Args:
        source_path: 源文件路径
        dest_path: 目标文件路径
        size: 缩略图尺寸
        
    Returns:
        缩略图路径
    """
    with Image.open(source_path) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        img.save(dest_path, quality=85, optimize=True)
    
    return dest_path
```

## 第N-5页

```python
# 文件: app/schemas/content.py
"""
内容相关Schema定义
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class ContentCreateSchema(Schema):
    """内容创建Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    title = fields.String(required=True, validate=validate.Length(min=1, max=256))
    content_type = fields.String(validate=validate.OneOf(['text', 'image', 'video', 'audio', 'mixed']))
    body = fields.String()
    summary = fields.String(validate=validate.Length(max=512))
    tags = fields.List(fields.String())
    project_id = fields.String()
    cover_image = fields.String()


class ContentUpdateSchema(Schema):
    """内容更新Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    title = fields.String(validate=validate.Length(min=1, max=256))
    body = fields.String()
    summary = fields.String(validate=validate.Length(max=512))
    tags = fields.List(fields.String())
    cover_image = fields.String()


class ContentQuerySchema(Schema):
    """内容查询Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    creator_id = fields.String()
    content_type = fields.String()
    status = fields.String()
    keyword = fields.String()
    tags = fields.List(fields.String())
    project_id = fields.String()


# 文件: app/schemas/workflow.py
"""
工作流相关Schema定义
"""

from marshmallow import Schema, fields, validate, EXCLUDE
```

## 第N-4页

```python
class WorkflowCreateSchema(Schema):
    """工作流创建Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    name = fields.String(required=True, validate=validate.Length(min=1, max=128))
    description = fields.String()
    definition = fields.Dict()
    variables = fields.Dict()
    is_template = fields.Boolean(load_default=False)
    project_id = fields.String()


class WorkflowUpdateSchema(Schema):
    """工作流更新Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    name = fields.String(validate=validate.Length(min=1, max=128))
    description = fields.String()
    definition = fields.Dict()
    variables = fields.Dict()


class WorkflowTaskSchema(Schema):
    """工作流任务Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    name = fields.String(required=True)
    task_type = fields.String(required=True)
    config = fields.Dict()
    position = fields.Dict()
    inputs = fields.List(fields.Dict())
    outputs = fields.List(fields.Dict())


# 文件: app/schemas/generation.py
"""
AI生成相关Schema定义
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class GenerationRequestSchema(Schema):
    """生成请求Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    prompt = fields.String(required=True, validate=validate.Length(min=1))
    model = fields.String()
    max_tokens = fields.Integer(validate=validate.Range(min=1, max=8192))
    temperature = fields.Float(validate=validate.Range(min=0, max=2))
```

## 第N-3页

```python
class ImageGenerationSchema(Schema):
    """图像生成Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    prompt = fields.String(required=True, validate=validate.Length(min=1))
    model = fields.String()
    size = fields.String(validate=validate.OneOf(['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792']))
    quality = fields.String(validate=validate.OneOf(['standard', 'hd']))
    n = fields.Integer(validate=validate.Range(min=1, max=10))


class BatchGenerationSchema(Schema):
    """批量生成Schema"""
    
    class Meta:
        unknown = EXCLUDE
    
    tasks = fields.List(fields.Dict(), required=True)
    max_concurrent = fields.Integer(validate=validate.Range(min=1, max=10), load_default=5)


# 文件: config.py
"""
应用配置模块
"""

import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
```

## 第N-2页

```python
    # AI服务配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE')
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = None
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:password@localhost/aigc_dev'
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    LOG_FILE = '/var/log/aigc/app.log'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

## 第N-1页

```python
# 文件: app/errors/__init__.py
"""
错误处理模块
"""

from flask import jsonify


def handle_400_error(e):
    """处理400错误"""
    return jsonify({
        'success': False,
        'error': '请求参数错误',
        'message': str(e)
    }), 400


def handle_401_error(e):
    """处理401错误"""
    return jsonify({
        'success': False,
        'error': '未授权访问',
        'message': '请先登录'
    }), 401


def handle_403_error(e):
    """处理403错误"""
    return jsonify({
        'success': False,
        'error': '禁止访问',
        'message': '权限不足'
    }), 403


def handle_404_error(e):
    """处理404错误"""
    return jsonify({
        'success': False,
        'error': '资源不存在',
        'message': '请求的资源未找到'
    }), 404


def handle_500_error(e):
    """处理500错误"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': '请稍后再试'
    }), 500


class APIError(Exception):
    """API异常基类"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
```

## 第N页（最后一页）

```python
    def to_dict(self):
        """转换为字典"""
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['error'] = self.message
        return rv


class ValidationError(APIError):
    """数据验证异常"""
    
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400)
        self.errors = errors


class AuthenticationError(APIError):
    """认证异常"""
    
    def __init__(self, message='认证失败'):
        super().__init__(message, status_code=401)


class AuthorizationError(APIError):
    """授权异常"""
    
    def __init__(self, message='权限不足'):
        super().__init__(message, status_code=403)


class NotFoundError(APIError):
    """资源不存在异常"""
    
    def __init__(self, message='资源不存在'):
        super().__init__(message, status_code=404)


class ConflictError(APIError):
    """资源冲突异常"""
    
    def __init__(self, message='资源冲突'):
        super().__init__(message, status_code=409)


class RateLimitError(APIError):
    """频率限制异常"""
    
    def __init__(self, message='请求过于频繁'):
        super().__init__(message, status_code=429)
```

---

**AIGC创作平台系统 V1.0 源程序 后30页 完**

*第N-29页 至 第N页*

