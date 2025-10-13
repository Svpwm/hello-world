"""Deterministic planner assembling tool execution plans for the driver assistant agent."""

from __future__ import annotations

from typing import List

from .memory import ConversationMemory
from .models import IntentType, PlanStep, PlanStepType, TriggerContext


class RuleBasedPlanner:
    """Simple rule-based planner mapping intents to tool sequences."""

    def make_plan(
        self,
        intent: IntentType,
        trigger: TriggerContext,
        memory: ConversationMemory,
    ) -> List[PlanStep]:
        """Create an ordered list of plan steps for the current trigger."""

        if intent == IntentType.FIND_FREIGHT:
            return [
                PlanStep(
                    step_type=PlanStepType.TOOL,
                    name="fetch_profile",
                    description="刷新司机画像，获取最近履约、取消、未成交记录与偏好。",
                ),
                PlanStep(
                    step_type=PlanStepType.REASON,
                    name="align_preferences",
                    description="结合历史对话与画像偏好，判断当前找货需求的重点。",
                ),
                PlanStep(
                    step_type=PlanStepType.TOOL,
                    name="recommend_freight",
                    description="匹配符合偏好的即时货源，并准备推荐话术。",
                ),
            ]

        if intent == IntentType.UPDATE_PROFILE:
            return [
                PlanStep(
                    step_type=PlanStepType.TOOL,
                    name="fetch_profile",
                    description="同步司机画像详情并提炼可用亮点。",
                ),
                PlanStep(
                    step_type=PlanStepType.REASON,
                    name="profile_summary",
                    description="结合最近对话，为司机总结画像重点和建议。",
                ),
            ]

        if intent == IntentType.KNOWLEDGE_QUERY:
            return [
                PlanStep(
                    step_type=PlanStepType.REASON,
                    name="clarify_question",
                    description="理解司机问题的意图，确定需要查询的规则方向。",
                ),
                PlanStep(
                    step_type=PlanStepType.TOOL,
                    name="query_knowledge",
                    description="查询行业知识库或平台规则，返回具体指引。",
                ),
                PlanStep(
                    step_type=PlanStepType.REASON,
                    name="ground_answer",
                    description="结合司机画像及场景，给出可执行建议。",
                ),
            ]

        # Default fall-back prompts the agent to clarify the intent.
        return [
            PlanStep(
                step_type=PlanStepType.REASON,
                name="clarify_intent",
                description="当前无法识别司机需求，需要向司机澄清目标。",
            )
        ]
