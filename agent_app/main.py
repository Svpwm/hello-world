"""FastAPI service exposing the driver assistant agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .agent import DriverAssistantAgent
from .config import AgentConfig, get_agent_config
from .models import AgentResponse, TriggerContext


def create_app(config: AgentConfig | None = None) -> FastAPI:
    app = FastAPI(title="Driver Assistant Agent", version="0.1.0")
    agent_config = config or get_agent_config()
    agent = DriverAssistantAgent(config=agent_config)

    @app.post("/agent/v1/trigger", response_model=AgentResponse)
    async def trigger_agent(
        payload: TriggerContext,
    ) -> JSONResponse:
        response = agent.run(payload)
        return JSONResponse(status_code=200, content=response.model_dump())

    @app.get("/agent/v1/ping")
    async def ping() -> Dict[str, Any]:
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    return app


app = create_app()
