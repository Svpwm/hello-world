"""Mock business tools for the driver assistant agent."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from .models import (
    AgentResponse,
    DriverPreference,
    DriverProfile,
    FreightOpportunity,
    FreightOrder,
    FreightStatus,
    IntentType,
    TriggerContext,
    VoiceSummary,
)


class DriverProfileTool:
    """Fetch driver profiles and behavioural preferences."""

    def fetch_profile(self, driver_id: str) -> DriverProfile:
        now = datetime.utcnow()
        voice = VoiceSummary(transcript="货主希望下午四点前装车", duration_seconds=78)
        base_order = dict(origin="上海", destination="杭州", price=5200.0, pickup_time=now - timedelta(days=2))
        wins = [
            FreightOrder(
                order_id=f"WIN-{i}",
                status=FreightStatus.WON,
                voice=voice,
                **base_order,
            )
            for i in range(1, 11)
        ]
        cancellations = [
            FreightOrder(
                order_id=f"CANCEL-{i}",
                status=FreightStatus.CANCELLED,
                pickup_time=now - timedelta(days=3 + i),
                origin="上海",
                destination="苏州",
                price=4100.0,
                voice=voice,
            )
            for i in range(1, 6)
        ]
        missed = [
            FreightOrder(
                order_id=f"MISSED-{i}",
                status=FreightStatus.LOST,
                pickup_time=now - timedelta(days=1 + i),
                origin="上海",
                destination="南京",
                price=6200.0,
                voice=voice,
            )
            for i in range(1, 6)
        ]
        preferences = DriverPreference(
            prefers_high_price=True,
            prefers_nearby=True,
            prefers_fast_turnaround=True,
            notes="司机偏好高价、近距离且装货时间更近的货源。",
        )
        return DriverProfile(
            driver_id=driver_id,
            score=0.86,
            recent_wins=wins,
            recent_cancellations=cancellations,
            recent_missed=missed,
            preferences=preferences,
        )


class FreightCatalogTool:
    """Mock tool providing freight opportunities."""

    def recommend(self, driver_profile: DriverProfile, limit: int = 5) -> List[FreightOpportunity]:
        base_pickup = datetime.utcnow() + timedelta(hours=2)
        opportunities = [
            FreightOpportunity(
                order_id="NEW-001",
                origin="上海",
                destination="杭州",
                price=6600.0,
                distance_km=180.0,
                pickup_time=base_pickup,
                cargo_type="电子产品",
                weight_tons=10.0,
            ),
            FreightOpportunity(
                order_id="NEW-002",
                origin="上海",
                destination="嘉兴",
                price=5200.0,
                distance_km=95.0,
                pickup_time=base_pickup + timedelta(hours=1),
                cargo_type="日用品",
                weight_tons=8.0,
            ),
            FreightOpportunity(
                order_id="NEW-003",
                origin="上海",
                destination="苏州",
                price=4800.0,
                distance_km=100.0,
                pickup_time=base_pickup + timedelta(hours=3),
                cargo_type="冷链食品",
                weight_tons=12.0,
            ),
        ]
        # Filter according to preferences
        filtered = [opp for opp in opportunities if opp.price >= 5000 or driver_profile.preferences.prefers_nearby]
        return filtered[:limit]


class KnowledgeBaseTool:
    """Mock tool simulating knowledge base lookup."""

    def query(self, question: str) -> str:
        return "根据平台规则，装货前需提前30分钟到场并完成安全检查。"


class IntentRouterTool:
    """Simple intent classifier."""

    def infer_intent(self, utterance: str) -> IntentType:
        utterance = utterance.lower()
        if "找货" in utterance or "货" in utterance:
            return IntentType.FIND_FREIGHT
        if "资料" in utterance or "画像" in utterance:
            return IntentType.UPDATE_PROFILE
        if "规则" in utterance or "怎么" in utterance:
            return IntentType.KNOWLEDGE_QUERY
        return IntentType.UNKNOWN


class DriverAssistantToolkit:
    """Aggregate toolkit used by the driver assistant agent."""

    def __init__(self) -> None:
        self.driver_profile = DriverProfileTool()
        self.freight_catalog = FreightCatalogTool()
        self.knowledge_base = KnowledgeBaseTool()
        self.intent_router = IntentRouterTool()

    def handle(self, trigger: TriggerContext) -> AgentResponse:
        intent = self.intent_router.infer_intent(trigger.utterance)
        profile = self.driver_profile.fetch_profile(trigger.driver_id)

        if intent == IntentType.FIND_FREIGHT:
            recommendations = self.freight_catalog.recommend(profile)
            message = "已为您挑选符合偏好的最新货源，是否需要立即联系货主？"
            return AgentResponse(
                intent=intent,
                message=message,
                recommended_orders=recommendations,
                driver_profile=profile,
            )
        if intent == IntentType.UPDATE_PROFILE:
            message = "已同步司机画像，包括最近履约、取消、未成交记录及偏好标签。"
            return AgentResponse(intent=intent, message=message, driver_profile=profile)
        if intent == IntentType.KNOWLEDGE_QUERY:
            answer = self.knowledge_base.query(trigger.utterance)
            message = f"为您找到的规则：{answer}"
            return AgentResponse(intent=intent, message=message, driver_profile=profile)

        message = "我没有理解您的需求，请问是要找货、更新画像还是咨询平台规则？"
        return AgentResponse(intent=intent, message=message, driver_profile=profile)
