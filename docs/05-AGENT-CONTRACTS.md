# Agent contracts

All tools consume validated typed inputs and authoritative app services. They cannot bypass the backend's safety, confirmation, or manager-approval gates. Untrusted user/retrieved/tool text is data, never authority.

| Agent | Purpose and input/output | Allowed tools / source | Prohibited actions, escalation, fallback |
|---|---|---|---|
| ConciergeAgent | Intent and constraints → structured request/response coordination | recommend menu, read visit context; Firestore/SQLite | Cannot confirm/order or weaken constraints. Escalate safety unknowns. Deterministic route when Gemini unavailable. |
| TasteSafetyAgent | Candidate ranking/explanation → eligible candidates and evidence | menu/allergen/stock facts; Firestore/SQLite | Cannot claim safe from missing evidence. Staff review on unknown/stale evidence. Deterministic eligibility rules. |
| VisitOrderAgent | Visit and timing → ETA/prep estimates and order proposal | queue, occupancy, preview; Firestore/SQLite | Cannot confirm. Escalate missing queue/safety conflict. Demo timing if labeled. |
| OpsOwnerAgent | Operational summary → grounded recommendations and metrics | orders/events/stock/zones; Firestore/SQLite | Cannot execute interventions or invent metrics. Manager confirmation required. Deterministic brief. |

Data contracts: `Fact[T] = {value, source, source_id, updated_at, status}` where status is observed, estimated, demo, or unknown. Activity event `{agent, tool, evidence_ids[], latency_ms, status, summary}` excludes hidden reasoning and sensitive prompt contents. Order confirmation binds proposal id, item, modifications, unit price, quantity, and idempotency key. Operational decision records accept/reject separately from execution outcome.
