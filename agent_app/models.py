"""Domain models for driver assistant agent."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FreightStatus(str, Enum):
    """Status of a freight order."""

    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"


class VoiceSummary(BaseModel):
    """Summary of a voice conversation."""

    transcript: str = Field(description="Transcribed content of the call or voice note.")
    duration_seconds: int = Field(ge=0, description="Duration of the recording in seconds.")


class FreightOrder(BaseModel):
    """Freight order record."""

    order_id: str
    origin: str
    destination: str
    price: float
    pickup_time: datetime
    status: FreightStatus
    voice: Optional[VoiceSummary] = None


class DriverPreference(BaseModel):
    """Driver preference profile extracted from history."""

    prefers_high_price: bool = Field(default=False, description="Driver prioritises high paying shipments.")
    prefers_nearby: bool = Field(default=False, description="Driver prioritises nearby shipments to reduce deadhead miles.")
    prefers_fast_turnaround: bool = Field(default=False, description="Driver prefers shipments starting soon.")
    notes: str = Field(default="", description="Additional qualitative preference notes.")


class DriverProfile(BaseModel):
    """Aggregated driver profile with freight history."""

    driver_id: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    recent_wins: List[FreightOrder] = Field(default_factory=list)
    recent_cancellations: List[FreightOrder] = Field(default_factory=list)
    recent_missed: List[FreightOrder] = Field(default_factory=list)
    preferences: DriverPreference = Field(default_factory=DriverPreference)


class FreightOpportunity(BaseModel):
    """Candidate freight opportunity for matching."""

    order_id: str
    origin: str
    destination: str
    price: float
    distance_km: float
    pickup_time: datetime
    cargo_type: str
    weight_tons: float


class IntentType(str, Enum):
    """Enumerated intents recognised by the agent."""

    FIND_FREIGHT = "find_freight"
    UPDATE_PROFILE = "update_profile"
    KNOWLEDGE_QUERY = "knowledge_query"
    UNKNOWN = "unknown"


class PlanStepType(str, Enum):
    """Kinds of planning steps the agent can execute."""

    TOOL = "tool"
    REASON = "reason"


class PlanStep(BaseModel):
    """Single step within the agent planner output."""

    step_type: PlanStepType = Field(description="Whether this step uses a tool or is internal reasoning.")
    name: str = Field(description="Identifier for the step, typically matching a tool or reasoning label.")
    description: str = Field(description="Natural language explanation of what the step is accomplishing.")


class TriggerContext(BaseModel):
    """Trigger context passed to the agent when invoked."""

    driver_id: str
    channel: str
    utterance: str
    timestamp: datetime


class AgentResponse(BaseModel):
    """Response returned to the client after processing."""

    intent: IntentType
    message: str
    recommended_orders: List[FreightOpportunity] = Field(default_factory=list)
    driver_profile: Optional[DriverProfile] = None
    plan: List[PlanStep] = Field(default_factory=list, description="Planner steps executed for this response.")
