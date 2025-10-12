# Driver Assistant Agent

基于 FastAPI 与 LangGraph 的司机助理 Agent 示例，使用 uv 进行依赖管理（兼容 `uv pip install -r requirements` 形式）。该服务模拟对接业务系统，构建具备 **Planner + Memory + ReAct** 能力的智能体，覆盖司机画像、货源画像、触发机制和行业知识库查询等核心能力。

## 快速开始

1. 安装依赖（推荐使用 [uv](https://github.com/astral-sh/uv)）：
   ```bash
   uv pip install -r <(uv pip compile pyproject.toml)
   ```
   或者使用标准 pip：
   ```bash
   pip install -e .
   ```

2. 启动服务：
   ```bash
   uvicorn agent_app.main:app --reload
   ```

3. 触发 Agent：
   ```bash
   curl -X POST http://localhost:8000/agent/v1/trigger \
     -H "Content-Type: application/json" \
     -d '{
       "driver_id": "DRV-001",
       "channel": "app",
       "utterance": "帮我找找高价货",
       "timestamp": "2024-04-17T12:00:00Z"
     }'
   ```

响应中会包含司机画像（含最近 10 条履约/取消/未成交记录和语音摘要）、偏好标签、推荐的货源列表，以及可追溯的 Planner 步骤。

## 目录结构

- `agent_app/models.py`：领域模型与 Planner 步骤定义。
- `agent_app/memory.py`：对话记忆环形缓存，负责多轮上下文保留。
- `agent_app/planner.py`：基于业务意图的规则化 Planner，生成工具执行计划。
- `agent_app/agent.py`：LangGraph 编排的智能体，结合 Planner、记忆与 ReAct 工序。
- `agent_app/tools.py`：Mock 工具层，覆盖司机画像、货源画像、触发识别、行业知识库等能力。
- `agent_app/main.py`：FastAPI 服务入口。
- `pyproject.toml`：项目依赖与 uv 兼容配置。

## 后续规划

- 接入真实业务系统接口替换 Mock 工具。
- 增加对话记忆压缩与多轮协作的子 Agent。
- 构建自动化评测集与离线指标监控。
