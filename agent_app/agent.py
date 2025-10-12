"""Driver assistant agent orchestrated via LangGraph."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional, TypedDict

from langgraph.graph import END, StateGraph

from .config import AgentConfig, get_agent_config
from .memory import ConversationMemory
from .models import (
    AgentResponse,
    DriverProfile,
    FreightOpportunity,
    IntentType,
    PlanStep,
    PlanStepType,
    TriggerContext,
)
from .planner import RuleBasedPlanner
from .tools import DriverAssistantToolkit


class AgentState(TypedDict, total=False):
    """Mutable state passed between planner, executor, and reactor nodes."""

    trigger: TriggerContext
    memory: ConversationMemory
    intent: IntentType
    plan: List[PlanStep]
    step_index: int
    observations: List[str]
    profile: DriverProfile
    recommendations: List[FreightOpportunity]
    knowledge: str
    last_observation: str
    response: AgentResponse


class DriverAssistantAgent:
    """High-level agent encapsulating planner, memory, and tool execution."""

    def __init__(
        self,
        *,
        toolkit: Optional[DriverAssistantToolkit] = None,
        config: Optional[AgentConfig] = None,
        planner: Optional[RuleBasedPlanner] = None,
    ) -> None:
        self.toolkit = toolkit or DriverAssistantToolkit()
        self.config = config or get_agent_config()
        self.planner = planner or RuleBasedPlanner()
        self._graph = self._build_graph().compile()
        self._memory_store: Dict[str, ConversationMemory] = {}

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        def plan_node(state: AgentState) -> AgentState:
            trigger = state["trigger"]
            memory = state.get("memory") or ConversationMemory(self.config.max_history_turns)
            memory.add_turn("user", trigger.utterance, timestamp=trigger.timestamp)
            intent = self.toolkit.intent_router.infer_intent(trigger.utterance)
            plan = self.planner.make_plan(intent, trigger, memory)
            state.update(
                {
                    "memory": memory,
                    "intent": intent,
                    "plan": plan,
                    "step_index": 0,
                    "observations": [],
                }
            )
            return state

        def act_node(state: AgentState) -> AgentState:
            plan = state["plan"]
            idx = state["step_index"]
            step = plan[idx]
            trigger = state["trigger"]

            observation: str
            if step.step_type == PlanStepType.REASON:
                if step.name == "align_preferences":
                    profile = state.get("profile")
                    if not profile:
                        profile = self.toolkit.driver_profile.fetch_profile(trigger.driver_id)
                        state["profile"] = profile
                    pref = profile.preferences
                    observation = (
                        "偏好侧重：高价({}), 近距离({}), 装货及时({})。"
                    ).format(
                        "是" if pref.prefers_high_price else "否",
                        "是" if pref.prefers_nearby else "否",
                        "是" if pref.prefers_fast_turnaround else "否",
                    )
                elif step.name == "profile_summary":
                    profile = state.get("profile")
                    if profile:
                        observation = (
                            f"画像得分 {profile.score:.2f}，最近履约 {len(profile.recent_wins)}，取消 {len(profile.recent_cancellations)}，未成交 {len(profile.recent_missed)}。"
                        )
                    else:
                        observation = "暂未获取画像，建议先刷新画像信息。"
                elif step.name == "clarify_question":
                    observation = f"司机问题指向：{trigger.utterance}，准备检索对应规则。"
                elif step.name == "ground_answer":
                    knowledge = state.get("knowledge")
                    observation = (
                        f"结合司机历史与知识库回答，给出可执行建议：{knowledge}" if knowledge else "等待知识库结果以给出建议。"
                    )
                elif step.name == "clarify_intent":
                    observation = "无法定位意图，需要向司机澄清需求。"
                else:
                    observation = step.description
            elif step.name == "fetch_profile":
                profile = self.toolkit.driver_profile.fetch_profile(trigger.driver_id)
                state["profile"] = profile
                observation = "司机画像已刷新，包含最新履约记录和偏好。"
            elif step.name == "recommend_freight":
                profile = state.get("profile") or self.toolkit.driver_profile.fetch_profile(trigger.driver_id)
                recommendations = self.toolkit.freight_catalog.recommend(profile)
                state["recommendations"] = recommendations
                observation = f"根据画像匹配到 {len(recommendations)} 条候选货源。"
            elif step.name == "query_knowledge":
                knowledge = self.toolkit.knowledge_base.query(trigger.utterance)
                state["knowledge"] = knowledge
                observation = f"知识库反馈：{knowledge}"
            else:
                observation = f"暂不支持的执行步骤：{step.name}"

            state["last_observation"] = observation
            return state

        def react_node(state: AgentState) -> AgentState:
            observation = state.get("last_observation", "")
            observations = state.get("observations", [])
            step = state["plan"][state["step_index"]]
            observations.append(f"[{step.name}] {observation}")
            state["observations"] = observations
            state["step_index"] = state.get("step_index", 0) + 1
            return state

        def should_continue(state: AgentState) -> Literal["continue", "respond"]:
            if state.get("step_index", 0) < len(state.get("plan", [])):
                return "continue"
            return "respond"

        def respond_node(state: AgentState) -> AgentState:
            intent = state.get("intent", IntentType.UNKNOWN)
            profile = state.get("profile")
            recommendations = state.get("recommendations", [])
            knowledge = state.get("knowledge")
            memory = state.get("memory") or ConversationMemory(self.config.max_history_turns)

            if intent == IntentType.FIND_FREIGHT and recommendations:
                rec_lines = [
                    f"{rec.order_id}: {rec.origin}->{rec.destination}, ¥{rec.price:.0f}, {rec.distance_km:.0f}公里, 装货 {rec.pickup_time:%m-%d %H:%M}"
                    for rec in recommendations
                ]
                message = "\n".join(
                    [
                        "已根据您的偏好挑选以下优质货源：",
                        *rec_lines,
                        "如需我代为联系货主或继续筛选，请告诉我。",
                    ]
                )
            elif intent == IntentType.FIND_FREIGHT:
                message = "暂未找到符合画像的货源，我会持续关注新单，有更新立即同步给您。"
            elif intent == IntentType.UPDATE_PROFILE and profile:
                pref = profile.preferences
                message = (
                    "画像已更新：偏好高价{}、近距离{}、装货及时{}。最近10票履约、取消、未成交记录已整理，可随时复盘。"
                ).format(
                    "✅" if pref.prefers_high_price else "❌",
                    "✅" if pref.prefers_nearby else "❌",
                    "✅" if pref.prefers_fast_turnaround else "❌",
                )
            elif intent == IntentType.KNOWLEDGE_QUERY and knowledge:
                message = f"针对您的问题，我查到的规则是：{knowledge} 如果需要进一步解释或案例，请继续提问。"
            elif intent == IntentType.KNOWLEDGE_QUERY:
                message = "暂未检索到相关规则，我会继续搜索，也欢迎提供更多上下文。"
            else:
                message = "我还不确定您的需求，麻烦说明是要找货、查看画像还是咨询规则。"

            memory.add_turn("assistant", message, timestamp=datetime.utcnow())
            response = AgentResponse(
                intent=intent,
                message=message,
                recommended_orders=recommendations,
                driver_profile=profile,
                plan=state.get("plan", []),
            )
            state["memory"] = memory
            state["response"] = response
            return state

        graph.add_node("plan", plan_node)
        graph.add_node("act", act_node)
        graph.add_node("react", react_node)
        graph.add_node("respond", respond_node)

        graph.set_entry_point("plan")
        graph.add_edge("plan", "act")
        graph.add_edge("act", "react")
        graph.add_conditional_edges("react", should_continue, {"continue": "act", "respond": "respond"})
        graph.add_edge("respond", END)

        return graph

    def _memory_for_driver(self, driver_id: str) -> ConversationMemory:
        if driver_id not in self._memory_store:
            self._memory_store[driver_id] = ConversationMemory(self.config.max_history_turns)
        return self._memory_store[driver_id]

    def run(self, trigger: TriggerContext) -> AgentResponse:
        """Invoke the agent for the provided trigger context."""

        memory = self._memory_for_driver(trigger.driver_id)
        state: AgentState = {"trigger": trigger, "memory": memory}
        output = self._graph.invoke(state)
        updated_memory = output.get("memory", memory)
        self._memory_store[trigger.driver_id] = updated_memory
        return output["response"]
