# End-to-end product capability coverage

The complete product connects a customer's visit to café fulfillment, owner learning, and an approved improvement for the next visit. This is the product-level companion to the [technical architecture](04-ARCHITECTURE.md), based on the current source at `76134e6` and the approved [product vision](01-PRODUCT-VISION.md)/[roadmap](roadmap/README.md). It is a target capability map, not a statement that the complete product exists.

![End-to-end capabilities and current coverage](architecture/09-end-to-end-capabilities.svg)

## What the finished experience looks like

A café administrator onboards a location and publishes reviewed menu, safety, price, stock, hours, and space information. A customer discovers a participating café, describes the visit and constraints, sees trustworthy choices, and explicitly confirms a current proposal. Authorized systems reserve capacity/stock, handle payment when enabled, coordinate arrival, and route preparation to staff. The customer receives status, collection/seating instructions, and help with problems or cancellation.

Staff see the same order, stock, queue, and service-recovery state. A manager's decision, any authorized execution, and its observed outcome are separately recorded. Feedback updates visible, reversible preferences without learning or weakening safety rules. Owners see consistently defined service and business measures; reviewed improvements flow back through governed administration and controlled releases. Optional community experiences require consent and moderation throughout.

## Status legend

- **Implemented — limited:** a code path exists, usually using synthetic facts or records, with the stated limitations. This does not certify current live-provider health or full requirement coverage.
- **Mixed:** a small implemented path supports part of the capability; substantial target behavior is missing.
- **Planned:** no complete implemented workflow was found. A document, UI vision card, or agent description alone does not count as implementation.

No completion percentages are assigned: a checkbox or count would hide the difference between a demo path and a dependable end-to-end workflow. Audit IDs refer to the [developer handoff](architecture/DEVELOPER-HANDOFF.md).

## Feature-by-feature coverage

| Stage / owner | Complete-product capability | Current coverage and evidence | Missing work / proposed acceptance criterion |
| --- | --- | --- | --- |
| Onboard / administrator | Participating locations, responsible operators and tenant boundaries | **Planned.** One synthetic café in `data.py`; Google identity covers reviewers only | Onboard a location, assign tenant-bound roles, and prove another tenant cannot access its data |
| Govern / administrator | Versioned menu/variants/tax/price, ingredients/allergens/cross-contact, hours and space | **Planned.** Business facts are fixtures | Authorized edits with provenance, review/expiry, history and rollback; unsafe/unknown records block relevant actions |
| Discover / customer | Café search, verified participation, amenities/accessibility, suitable work/meeting/social/takeaway spaces | **Mixed.** `places_search` supplies Places directory results and a route; zones are synthetic | Distinguish directory from participating café and verified amenities; no order enabled solely by a Maps result |
| Plan / customer | Typed origin or consented location, group halfway choice, best-time/demand guidance | **Mixed.** Typed origin or one-time coordinates; route to first located result | Explicit location consent/lifecycle; selectable destination and group travel trade-offs; evaluated demand estimates |
| Personalize / customer | Inspect/edit/reset preferences and explicit safety constraints | **Mixed.** UI regex extraction, persisted four-weight feedback, demo reset; shared demo identity | Customer ownership, canonical server constraints, reversible corrections and separately audited safety updates; F02 |
| Choose / customer | Menu matching with reliable diet, allergy, budget, temperature and time handling | **Implemented — limited.** Lexical matching, deterministic filters, source IDs, optional ADK explanation | Consistent stage-specific rules and unknown-data behavior, broader reviewed cases, no unsupported safety claims; F01/F02/F15 |
| Preview / customer | Versioned quote with item/variants, quantity, price/tax, constraints and expiry | **Mixed.** Stored exact synthetic proposal | Bind canonical constraints and catalog version; TTL and changes trigger a new preview; F01–F03 |
| Commit / customer and backend | Explicit confirmation, stable retries and transactional inventory | **Mixed.** Simulated confirmation, snapshot matching and duplicate-key replay | Same command retry returns one result; conflicting key reuse fails; last-unit race cannot oversell; F04/F05 |
| Pay / customer and integration | Approved payment/POS/loyalty workflows, reconciliation, refunds | **Planned.** No payment or POS write | Signed/verified provider events, reconciliation, refund policy and audited failure recovery; no inferred success |
| Reserve / customer and staff | Seats, capacity, waitlists, expiry, cancellation and no-show policy | **Planned.** Synthetic zone information only | Atomic capacity checks and release; customer/staff share reservation state and policy |
| Arrive / customer and staff | Consented arrival-aware preparation and collection/seating guidance | **Planned.** Route information is not arrival tracking or fulfillment coordination | Consent-controlled updates, bounded preparation policy, explicit stale-location behavior and customer opt-out |
| Fulfill / café team | Station routing, workload, ordered lifecycle, collection and cancellation | **Mixed.** Manual synthetic confirmed → preparing → ready → completed transitions, with allowed cancellations | Role-bound station ownership, durable events, approved integrations and consistent customer/staff status |
| Estimate / café team | Queue/prep/total timing with measured calibration | **Implemented — limited.** Latest measured samples calibrate; seeded samples excluded | Resolve total-versus-prep semantics, align time gates, display and accuracy calculation; F06 |
| Inventory / café team | Stock reserve/release, low-stock response, substitutions and lost demand | **Mixed.** Fixture flags and low-stock alerts | Governed quantities and atomic reservations/release, reviewed substitutions, reconciliation and oversell tests; F04 |
| Safety review / authorized staff | Owned case, accountable evidence correction, resolution and audit | **Mixed.** Staff-review status and safety events; no resolver workflow | Authorized review never becomes an unsupported safety certification; corrected evidence is versioned and all action gates re-run |
| Experience / customer and staff | Assistance, voluntary Room Pulse, service recovery and shift handover | **Planned.** Some synthetic queue/occupancy signals | Consent-based signals, assigned case owner, action/resolution trail and handover continuity; no sensitive inference |
| Operate / manager | Recommendations with separate decision, execution and outcome | **Mixed.** Accept/reject audit and shared Ops read model | Role-authorized interventions, explicit execution status, failure recovery and measured outcomes; never equate acceptance with execution |
| Return / customer | Feedback, preference corrections, loyalty and repeat visits | **Mixed.** Four bounded feedback weights and single demo customer | Authenticated customer journey, correction/consent controls, opt-in loyalty and meaningful visit identity; F02/F13 |
| Connect / community | Café events, moderated interest tables, consented joins and group ordering | **Planned.** Vision/roadmap only | Start with events/tables; leave/hide/block/report, moderation and deletion before direct person matching |
| Analyze / owner | Windowed conversion, order value, waits, service quality, cancellations/refunds | **Mixed.** Shared-record demo metrics and optional owner brief | State/window/denominator definitions and expected-math tests; distinguish observations/hypotheses; F09/F13 |
| Optimize / owner | Waste, substitutions/lost demand, station/capacity, interventions, forecasts | **Planned.** Low-stock and basic timing signals do not implement these analyses | Capture reliable inputs/outcomes; evaluate forecasts and interventions without causal overclaims |
| Scale / regional owner | Multi-location comparisons and verified cost/margin measures | **Planned.** One synthetic café; no verified costs | Canonical location/time/currency definitions, governed cost inputs and access isolation before margin claims |
| Administer / administrator | Staff/shift roles, integrations, support/audit and policy configuration | **Planned.** Reviewer token checks and config/environment variables only | Least privilege, revocation, tenant-bound administration, audit and support procedures; F11 |
| Control data / customer and administrator | Consent, inspection, export, deletion and retention across providers/backups | **Planned.** Demo reset is not an individual privacy lifecycle | Documented data inventory, identity-checked requests, deletion/export propagation and retention tests |
| Communicate / platform | Reliable notifications, multilingual accessible UI and conversational voice | **Mixed.** Saved TTS narration/video playback; no runtime voice session | Delivery state, consent/unsubscribe, accessibility/localization checks; evaluated live voice with the same action gates |

## Shared platform coverage

| Enabler | Current boundary | Complete-product gate |
| --- | --- | --- |
| Persistence and concurrency | SQLite or one bounded Firestore snapshot; compare-and-set; eight tables | Tenant-scoped transactional records, migration/recovery plan, concurrent inventory/order tests and backups/restore |
| Identity and policy | Google reviewer token verification; no app role/tenant lookup; partial schema coverage | Canonical actor/tenant/role checks on every sensitive operation, typed contracts and negative authorization tests; F10/F11 |
| AI and factual authority | Four ADK definitions, three read tools, optional model paths, recommendation guard | Versioned tools/prompts/models, required completion/output contracts and evaluated grounding; model text never authorizes actions; F07–F09 |
| Retrieval | Structured lexical catalog, three retrieval goldens | Keep structured fact authority; add document RAG only for governed documents with ACL/freshness/citations and no-answer tests |
| Observability and recovery | Persisted app rows, local status and timing measures | Correlated traces, known status age, SLOs/alerts, incident ownership, safe retries/circuits, load/failure/restore exercises; F12 |
| Quality and delivery | Tests/typecheck/build, smoke rehearsal, audits, Docker and secrets CI; manual deployment | Executed policy coverage, reviewed datasets, protected exact-version release, shadow/canary, rollback and evidence; F14 |
| Governed improvement | Bounded feedback/calibration and unpromoted error/review signals | Human-reviewed goldens; calibrated judge only if useful; controlled experiments; no autonomous safety/policy rewriting |
| Analytics and budgets | Demo formulas; no BigQuery, cost budgets or rate-limiting program | Reliable outbox/events, canonical lineage and definitions, privacy checks, usage/cost/abuse limits before expanded traffic |

## Suggested delivery slices and release gates

| Slice | End-to-end result | Gate before claiming completion |
| --- | --- | --- |
| 1 — Trustworthy synthetic journey | Demo discovery → choice → preview → confirmation → Ops → Owner → feedback | Verify/close applicable F01–F15 findings, reconcile labels, execute focused regressions and the connected smoke journey |
| 2 — One controlled café pilot | Onboard → govern facts → authorize staff → transact inventory/order → fulfill → recover | Tenant/role isolation, governed safety data, atomic inventory, approved integration, privacy lifecycle, monitoring and recovery drills |
| 3 — Complete visit and service | Reservations/arrival → stations → collection/seating → help/cancel/refund → return | Shared lifecycle and consent, reliable notifications, explicit exception owners, accessibility and tested provider failures |
| 4 — Optional community and owner expansion | Moderated events/groups; comparable multi-location service/business insight | Community consent/moderation controls; reliable identity, metric definitions and verified costs before financial claims |
| 5 — Evaluated optimization | Governed RAG/voice/forecasting and reviewed improvement | Versioned evidence, hard policy gates, representative evaluations, bounded rollout, monitoring and rollback |

These slices are proposed sequencing, not deadlines or claims of approved staffing. Some platform work must precede each slice; it cannot be deferred merely because a UI feature can be demonstrated.

## Keeping this map credible

Assign an accountable owner and acceptance test to each capability before implementation. Track **implemented**, **tested**, **deployed**, and **operationally supported** as separate evidence fields. Update status only from code and executed evidence, and retain explicit unknowns. A complete product is a set of connected, supportable workflows, including failures and recovery, rather than a collection of screens.
