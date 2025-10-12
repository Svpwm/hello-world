# Driver Assistant Agent Architecture & Team Organization

## 1. Context & Objectives
- **Business goal**: empower platform drivers to earn more with less effort by automating planning, execution support, and issue resolution throughout the delivery lifecycle.
- **Product north star**: "One-tap co-pilot" that integrates seamlessly with existing driver app, surfaces timely guidance, and coordinates follow-up actions across the logistics ecosystem.
- **Team reality**: 7-8 AI engineers covering agent, ML, backend, and ops responsibilities. Need clear ownership aligned with agent lifecycle to avoid fragmented delivery.

## 2. Architectural Layers
| Layer | Purpose | Key Capabilities | Suggested Tech Stack |
| --- | --- | --- | --- |
| Experience Orchestration | Manage end-to-end driver journeys, dialogue state, and KPI tracking | Scenario routing, evaluation harness, outcome attribution | LangGraph agent graphs (Planner+ReAct), FastAPI, internal logging/metrics |
| Agent Runtime & Infra | Provide reliable execution environment for agents and sub-agents | Session management, tool registry, execution tracing, fault handling | LangGraph, uv package mgmt, OpenTelemetry, feature flags |
| Knowledge & Context Fabric | Aggregate driver profile, intents, ops data, and industry knowledge | Context synthesis, retrieval-augmented prompting, knowledge governance | Vector DB, feature store, cached profiles, domain KB connectors |
| Tooling Layer | Encapsulate platform & external actions via mockable tool interfaces | Order ops APIs, navigation, pricing, compliance checks, support workflows | FastAPI wrappers, typed clients, synthetic mocks, contract tests |
| Feedback & Evaluation Loop | Measure agent quality, collect driver feedback, and trigger improvements | Scenario definitions, eval suites, offline/online metrics, human review | Eval harness (LangSmith, custom), dashboards, annotation tools |

## 3. Agent System Design
1. **Agent Control Loop（Planner + Memory + ReAct）**
   - Planner：根据触发意图生成工具/推理步骤序列（例如刷新画像 → 偏好对齐 → 匹配货源），并向外暴露可追溯的计划列表。
   - ReAct Executor：逐步执行计划，调用工具获取画像、货源或知识库反馈，并将观察写入 scratchpad。
   - 记忆：使用环形缓存维护最近多轮对话，支撑 Planner 调整策略并输出可追溯的计划。
2. **Multi-Agent Topology**
   - *Coordinator Agent*: supervises conversations, delegates to specialists, applies escalation policies.
   - *Specialist Agents*: execution planning, compliance advisor, earnings optimizer, support concierge. Each exposes a narrow tool set for the coordinator.
   - *Knowledge Agents*: handle driver profile enrichment and knowledge retrieval; provide structured context objects instead of direct conversation.
3. **Dialogue & Memory Strategy**
   - Conversation graph with checkpoints (pre-trip, en-route, post-delivery).
   - Rolling short-term memory (recent turns) plus episodic summaries via compress-and-cache strategy.
   - Prompt templates referencing driver persona, current job, environment signals.
4. **Tool Management**
   - Contract-first definitions; ability to mock tools for offline testing.
   - Tool health monitoring (latency, error rate) with automatic fallback to scripted flows.

## 4. Triggering & Intent Flow
1. **Trigger Sources**: driver app events, telematics, order lifecycle events, manual pings.
2. **Intent Detection**: lightweight classifier + heuristics. Support intent upsert and feedback loop.
3. **Context Assembly**: fetch driver baseline profile, current tasks, historical incidents, weather/traffic signals, and scenario-specific knowledge cards.
4. **Action Selection**: orchestrator picks best sub-agent/tools; ensures SLA guardrails.

## 5. Team Structure & Ownership
| Pod | Headcount | Primary Scope | Deliverables |
| --- | --- | --- | --- |
| Agent Orchestration Pod | 2 | Conversation graph, coordinator agent, evaluation harness | LangGraph flows, policy configs, scenario scorecards |
| Infra & Reliability Pod | 2 | Runtime stability, observability, fault recovery, deployment | Tool registry, tracing dashboards, chaos testing playbook |
| Knowledge & Profile Pod | 2 | Driver persona modeling, knowledge ingestion, context APIs | Profile service, retrieval pipelines, quality benchmarks |
| Tooling & Integration Pod | 1-2 | Platform API wrappers, mock tools, trigger ingestion | Tool SDK, mock harness, contract tests |
| Feedback & Insights Pod (part-time) | 1 | Evaluation data analysis, driver feedback loop | Eval reports, annotation guidelines, prioritization backlog |

> **Responsibility Model**: Each pod owns both build & run of its scope; coordinator role (tech lead) ensures cross-pod alignment and reviews.

## 6. Delivery Cadence & Interfaces
- **Quarterly**: roadmap alignment, scenario expansion targets, shared OKRs (activation, retention, NPS, automation rate).
- **Biweekly**: agent-level demos & eval reviews; cross-pod dependency sync.
- **Weekly**: pod standups, runbook updates, incident reviews.
- **Artifacts**: API contracts, prompt specs, tool schemas, scenario scorecards, eval dashboards.

## 7. Sub-Agent Definition Guidance
- Define sub-agents around **driver-facing capabilities** (e.g., earnings optimization), not data assets.
- Each sub-agent must own: prompt templates, tools, evaluation cases, fallback flows.
- Supporting pods (e.g., profile) deliver consumable **context services** to sub-agents, but do not operate as agents.
- Use RFC checklist before adding new sub-agent: business KPI impact, tool availability, observability plan, evaluation coverage.

## 8. Execution Guardrails
- **Observability**: standard tracing + conversation analytics; automated alerts on failure spikes.
- **Stability**: degraded-mode prompts, circuit breakers for flaky tools, synthetic fallback responses.
- **Compliance & Safety**: scenario-specific guardrails (no unsafe driving advice), human handoff policy.
- **Knowledge Governance**: freshness SLAs, versioned KB releases, audit logs for critical guidance.

## 9. Next Steps (0-1 Plan)
1. Align on top 3 driver scenarios (e.g., load acceptance, en-route issue resolution, post-trip earnings insights).
2. Build MVP coordinator with mock tools and scripted evaluation harness.
3. Stand up observability baseline (tracing, logging) + failure triage workflow.
4. Deliver first persona & context APIs; integrate into prompt assembly.
5. Run scenario pilots with closed beta drivers; collect feedback -> iterate.

