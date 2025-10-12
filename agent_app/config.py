"""Application configuration models."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field


class KnowledgeBaseConfig(BaseModel):
    """Configuration for knowledge base retrieval."""

    namespaces: List[str] = Field(
        default_factory=lambda: ["freight_policies", "pricing_rules", "safety_guidelines"],
        description="Ordered namespaces to search when answering driver questions.",
    )
    top_k: int = Field(default=4, ge=1, le=10, description="Number of documents to retrieve per query.")


class AgentConfig(BaseModel):
    """Configuration for the driver assistant agent."""

    knowledge_base: KnowledgeBaseConfig = Field(default_factory=KnowledgeBaseConfig)
    max_history_turns: int = Field(
        default=12,
        ge=1,
        description="How many interaction turns to keep when compressing conversation context.",
    )


@lru_cache(maxsize=1)
def get_agent_config() -> AgentConfig:
    """Return the cached agent configuration."""

    return AgentConfig()
