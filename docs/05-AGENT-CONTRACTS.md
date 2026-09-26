# Agent contracts

This document describes the tools and orchestration implemented in `backend/cafemesh/agents.py` and `main.py`, reviewed at `76134e6`. Agent names and prompt instructions do not establish capabilities or enforcement. See [view 07](architecture/07-agent-execution.svg) and audit findings F07–F09.

## Implemented tool surface

| Agent definition / ADK name | Actual tool or delegation | Authoritative source | Implemented use |
| --- | --- | --- | --- |
| Concierge / `concierge` | Registers all three agents below as sub-agents; no custom domain tool | Supplied request, deterministic candidate facts, queue, helper text | Final recommendation explanation after the two helpers |
| TasteSafetyAgent / `taste_safety` | `menu_facts()` | Selected `data.MENU` fixture fields | Fixed-prompt helper for menu evidence; cannot compute authoritative eligibility or confirm orders |
| VisitOrderAgent / `visit_order` | `visit_facts()` | `data.QUEUE` and `data.ZONES` fixtures | Fixed-prompt helper for visit context; no preview or order tool despite the agent description |
| OpsOwnerAgent / `ops_owner` | `owner_facts(days=30)` | `service.metrics(days)`, derived from shared stored records | Separate owner-endpoint summary for a 1–365 day window; also registered under Concierge |

Menu/visit facts are code fixtures, not Firestore collections. Tools return strings (Python representations or JSON); there is no universal typed `Fact[T]` envelope. None of the three tools writes orders, preferences, inventory, staff actions, or policy.

## Recommendation execution

1. The backend retrieves candidates and applies deterministic rules first. No candidates means no model execution.
2. Without configured Gemini credentials/Vertex mode, the response uses explicit deterministic demo behavior.
3. With configuration present, TasteSafety and VisitOrder run concurrently using fixed helper prompts. Each has a fresh `InMemoryRunner` session.
4. Concierge receives the user request, candidate facts, queue context, and helper output in its own runner session.
5. The path records tool/activity outcomes and requires final text. Helper prompts request tool use, but completed menu/visit calls are not mandatory response gates.
6. Declared allergies or detected allergy-safety language suppress generated recommendation prose. Configured provider errors return errors (502/503/504 as applicable), not successful demo fallback.

User text is untrusted input, not authority. Model prose never authorizes a write; preview/confirmation remain HTTP/domain operations. Their unresolved validation gaps are documented in [Safety and evaluation](06-SAFETY-AND-EVALUATION.md).

## Owner execution

The owner endpoint computes metrics, then optionally invokes OpsOwner directly. It requires a completed `owner_facts` call and nonempty final text. This is a tool-completion check, not verification of every number or causal assertion in the generated prose. Owner error handling is not identical to recommendation error persistence.

## Enforcement and intended guarantees

Instructions prohibit invented facts, allergy-safe guarantees, constraint weakening, and execution claims. Those instructions are not proof that an LLM always complies. Deterministic candidate rules, the recommendation narrative guard, tool restrictions, and explicit action endpoints provide the implemented controls. Stronger required-tool checks, structured output validation, semantic/numeric grounding checks, and versioned evaluation remain work to verify and implement.

Activity stores visible agent/tool outcomes, evidence IDs, status and latency; it is not distributed tracing or hidden reasoning. A manager decision records accept/reject separately from any future execution outcome. No real café write occurs.
