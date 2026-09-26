# CaféMesh AI: code-first architecture audit

Reviewed 26 September 2026. Source: [`76134e6099c4abd0c04de06227b91e7944cc0a6e`](https://github.com/imrohitagrawal/cafemesh-ai/tree/76134e6099c4abd0c04de06227b91e7944cc0a6e), still the head of `master` when this audit began.

**Publication scope:** this audit and the nine diagrams document the reviewed implementation. The accompanying documentation corrections do not fix the application gaps listed below. Findings describe the pinned source snapshot; references to earlier documentation describe what was found before correction.

## Evidence policy

1. **Current implementation:** executable source and committed configuration establish which paths exist. Tests are inspected for the exact behaviors they assert, not accepted from their names alone.
2. **Verified behavior:** an executed test or observed runtime result proves only the behavior and environment exercised. The initial static review did not rerun the application suite. During publication, locked dependencies were installed and `make verify` passed all 29 tests, TypeScript checking and the frontend build; `make demo-smoke` passed 2/2 synthetic rehearsals. Live providers were not rechecked. These existing tests do not close the newly identified gaps.
3. **Deployed infrastructure:** Dockerfile, proxy source, configuration code, and CI YAML are direct evidence. Region, active Cloud Run settings, actual IAM grants, Secret Manager binding, and OAuth Testing audience are described in deployment documentation but were not queried from Google Cloud in this review. Views 02 and 08 explicitly carry this qualification.
4. **Target architecture:** roadmap documents describe intent. These features appear only in the planned view and the future-capability inventory below.

Source is authoritative about what was written, but it is not automatically correct. A code/documentation mismatch can mean a stale document, an implementation defect, or an unmet requirement. The review must retain the mismatch rather than silently redefining the requirement to fit a defect.

## What changed in the diagrams

| View | Revision |
| --- | --- |
| 01 — System context | Added **Cloud Firestore** as an explicit managed dependency with a read/persist relationship. Kept storage mechanics in L2/06. References explain where hosting, secrets, TTS and delivery appear. |
| 02 — Containers/deployment | Added Secret Manager, static-media delivery, alternate API-key model mode, Vite development mode, runtime-status limitations, and the distinction between code evidence and documented deployment settings. |
| 03 — Runtime components | Added UI constraint extraction/geolocation, main.py's feedback/transition/decision/reset/status responsibilities, all eight table names, and the direct-write caveat. No imaginary policy microservice or workflow engine. |
| 04 — Trusted AI/action flow | Added both narrative-guard conditions, actual idempotency behavior, missing safety-age/TTL rechecks, and absence of inventory reservation. |
| 05 — Target production | Added all five product experience families, integration adapters, versioned harness/budgets/replay, calibrated-judge limits, separate approval/action/outcome, and staged rollout/rollback. Everything remains planned. |
| 06 — State and learning | New: code fixtures versus stored records, all eight logical tables, Firestore snapshot mechanics, SQLite alternative, feedback/calibration/review loops. |
| 07 — Agent execution | New: actual parallel Taste/Visit helpers, their real tools, Concierge context, separate owner path, fresh in-memory sessions, and different completion checks. |
| 08 — Delivery and media | New: CI verification, manual source deployment, build-time Cloud TTS, saved MP3/MP4 generation and static playback. |
| 09 — End-to-end capabilities | Added for publication: full product journey, current limited coverage, pilot prerequisites and the reviewed improvement loop; detailed acceptance criteria are in the capability matrix. |

## Findings requiring documentation correction or implementation work

These are static code findings, not newly executed exploits or production incident claims. Source paths are relative to the pinned repository; links are collected below.

| ID | Finding from code | Evidence and consequence | Diagram treatment / suggested next step |
| --- | --- | --- | --- |
| F01 | **Safety-record age is checked during recommendation, not preview/confirmation.** | `service.recommend()` compares `updated_at` to `SAFETY_MAX_AGE_DAYS`. `preview()` and `confirm()` check allergen intersection and unknown cross-contact, but do not repeat the age check. The stale-record test checks recommendation escalation on an already-unknown item; its confirmation assertion tests changed availability, not age. | View 04 states the gap. Centralize and reuse freshness/eligibility validation; add a clear-contact-but-stale case through preview and confirmation. Do not document universal stale-safety blocking today. |
| F02 | **Stored safety preferences are not automatically imposed on every request.** | The UI extracts allergies using regex. `recommend()` reads allergies from the supplied request; stored `preferences.safety` is not merged into those checks. `order_preview()` supplies a constraints dict, so the service's fallback to stored safety is not used on the ordinary API path. `recommendation_id` is optional; when supplied, preview checks candidate membership rather than inheriting the original constraint set. | Describe checks as checks of request-supplied constraints, not a canonical safety-profile enforcement guarantee. A real implementation needs authenticated profile ownership, explicit safety updates and server-bound constraint continuity. |
| F03 | **Proposal expiry has no TTL implementation.** | Proposals have `created_at`; `confirm()` rejects missing, used or changed snapshots but does not inspect age. Its error text includes “expired,” which is stronger than the implemented predicate. | View 04 does not claim expiration enforcement. Either implement an explicit validity interval or correct the wording. |
| F04 | **Inventory is a fixture flag, not a transactional reservation.** | `MENU.available` is checked. `stock_units` drives low-stock alerts but is not reserved/decremented on confirmation or released on cancellation. There is no quantity-versus-stock transaction. | Current views say simulated orders and availability checks. Transactional reservations remain target work. |
| F05 | **Idempotency replays before comparing the incoming proposal.** | `confirm()` returns the order with the existing key before reading or checking the incoming proposal. The UI generates a fresh UUID for each confirm attempt. | View 04 describes exact current behavior. A production command should bind a stable retry key to actor/tenant and payload hash, and reject a conflicting reuse. |
| F06 | **Calibration mixes measured total time with prep time.** | The UI asks for minutes from confirmation to ready; `transition()` records that as `actual_minutes`. `prep_estimate()` averages those measurements and preview/recommendation add queue wait again. The existing test expects 23 from an approximately 15-minute measured average plus 8 queue minutes. Time-constraint rechecks use fixture prep plus queue instead of the calibrated displayed estimate. | View 06 flags the unit mismatch. Define whether the observed value is preparation-only or total elapsed time, then align estimates, constraint gates, labels and tests. |
| F07 | **Declared agent contracts are broader than actual tools.** | `agents.py` exposes only `menu_facts()`, `visit_facts()` and `owner_facts(days)`. VisitOrderAgent has no preview tool; no agent has an order-write tool. Menu and visit tools read `data.py`, not Firestore. `docs/05-AGENT-CONTRACTS.md` lists broader sources/actions. | View 07 follows the tool definitions and actual calls. Update the contract document to the implemented tool surface. |
| F08 | **Recommendation helper tool completion is not enforced.** | `run_live_adk()` prompts Taste/Visit agents to use tools, records tool outcomes, and requires final text. It does not reject every response missing completed menu/visit tool calls. The owner handler explicitly requires completed `owner_facts` and nonempty text. Helper prompts are fixed; user text enters Concierge context later. | View 07 distinguishes “instructed to call” from a completion gate. Add required-tool checks if that is a product guarantee. |
| F09 | **Owner brief grounding is not semantic/numeric verification.** | The handler requires the tool and passes computed metrics, but does not compare every number or claim in generated prose against the tool result. The recommendation narrative guard is a separate path. | View 07 calls this a tool-completion check, not a fact checker or evaluation service. |
| F10 | **All HTTP payloads are not fully typed contracts.** | Recommendation, preview, confirm and Places have Pydantic models, but confirmation embeds a generic `dict`; feedback, decision and transition accept dictionaries with handler-level checks. | View 03 says “schemas + handler checks.” Add explicit nested/request schemas where stronger guarantees are required. |
| F11 | **Reviewer sign-in is not role/tenant authorization.** | `verify_google_id_token()` verifies the token audience and required identity claims. `require_demo_admin()` accepts this identity; it does not look up an app-specific manager/owner/tenant role. There is no app reviewer allowlist. Local mode can remain open when auth is not configured; hosted OAuth Testing is a separate documented external setting. | Current diagrams state the limitation. The PRD's “No ... authentication ... occurs” is stale because Google token verification exists. Real staff/customer isolation remains planned. |
| F12 | **Provider status is not a fresh health check.** | Firestore is labeled live from backend selection. Maps status is process-local. Gemini status reads the most recent Concierge activity, not every owner call. TTS status means an asset exists. Owner error paths do not use the same persisted error recorder as recommendations. | View 02 explains configuration/last-observation semantics. Do not claim all provider errors are persisted or all green states indicate current successful calls. |
| F13 | **Some owner metric names overstate the queried population.** | `metrics()` selects all orders in the time window without excluding cancelled rows. “Orders,” AOV and average predicted wait therefore use that set. `repeat_visits` is `count - 1` for a single synthetic customer. | Treat these as demo formulas, not validated business KPIs. Define included states and customer identity before pilot analytics. |
| F14 | **The policy JSON is an inventory, not an executed parameterized suite.** | `tests/test_app.py` loads the three retrieval goldens. No test or script reads `evals/policy-cases.json` in the inspected source. Related Python tests exist, but not every listed expectation is thereby proven. There are 29 test functions across the two test files. | View 08 lists the actual test/build commands. Retain separate executed cases, documented intentions and coverage gaps. |
| F15 | **Some recommendation gates differ from preview gates.** | `recommend()` does not check café opening and compares `item['price']` directly; a missing price is guarded in preview but would not be handled the same way in recommendation. | Avoid claiming every stage shares one complete safety/eligibility validator. Consolidate validation and add stage-specific tests. |

## Implementation coverage matrix

| Implemented area / dependency | Where shown | Code evidence |
| --- | --- | --- |
| Customer, Operations, Owner, Vision tabs; in-memory reviewer token | 01, 03; API inventory | `frontend/src/App.tsx` |
| Regex constraint extraction, timeout/JSON-response handling | 03, 04 | `App.tsx: extractConstraints(), api()` |
| Typed origin and opt-in one-time coordinates | 01–03; API inventory | `App.tsx: useMyLocation(), searchPlaces()`; `main.py: PlaceSearchRequest, places_search()` |
| Google Identity ID-token sign-in and reviewer route dependency | 01–03 | `main.py: verify_google_id_token(), require_demo_admin(), google_session()` |
| Places search: up to five directory results; route to first located result | 01, 02 | `main.py: places_search()` |
| Route failure returns an error route without synthetic ETA | API inventory | `main.py: places_search()` |
| FastAPI + Uvicorn serving built React/Vite app | 02, 03, 08 | `Dockerfile`; `main.py` static delivery; `frontend/package.json` |
| Cloudflare request proxy | 02, 08 | `deployment/cloudflare/worker.js` |
| Maps key via env; documented Secret Manager binding | 02, 08 | `config.py`; `.env.example`; binding only in `docs/CLOUD-RUN.md` |
| ADK/Gemini: Vertex/ADC or API-key mode | 01–04, 07 | `agents.py`; `config.py`; `main.py: run_live_adk()` |
| Lexical structured menu matching and deterministic ranking | 03, 04 | `service.py: menu_matches_query(), recommend()` |
| Preview snapshot and synthetic confirmation | 03, 04, 06 | `service.py: preview(), confirm()` |
| Order transition allowlist and measured-ready outcome | 03, 06; API inventory | `service.py: ALLOWED_TRANSITIONS`; `main.py: transition()` |
| Manager accept/reject audit; no execution | 01, 03, 06 | `main.py: decision()` |
| Windowed owner metrics and separate optional owner agent | 01, 03, 07 | `service.py: metrics()`; `main.py: owner()` |
| Feedback, four bounded taste weights, fixed synthetic customer | 03, 06 | `main.py: feedback()`; `service.py: recommend(), prefs()` |
| Calibration from measured-only latest-20 samples | 06 | `service.py: prep_estimate()`; `config.py` defaults |
| Persisted activity/errors/review flags, latency and prep error | 03, 06, 07 | `observability.py: build_observability()` |
| Firestore single snapshot, in-memory SQLite bridge, CAS, ceiling | **01**, 02, 06 | `db.py: FirestoreSnapshotConnection` |
| Local SQLite, initialization and global synthetic reset | 02, 06; API inventory | `db.py: connect(), initialize()` |
| Health, public config, provider status and vision inventory | 03; API inventory | `main.py` |
| Saved narration and product/engineering videos | 02, 03, 08 | `App.tsx`; `scripts/generate_voiceover.py`; render scripts; asset tree |
| CI tests, build, audits, smoke, image and secret checks | 08 | `.github/workflows/quality.yml`; `Makefile`; test and smoke source |
| Manual deployment and Google Cloud runtime settings | 02, 08, explicitly documentary | `docs/CLOUD-RUN.md`; no deploy job in workflow YAML |

## API inventory derived from route decorators

“Reviewer” means the `require_demo_admin` dependency, with the configuration-dependent behavior described in F11. “Public” means there is no such dependency; endpoint-specific validation still applies.

| Method | Route | Access | Responsibility |
| --- | --- | --- | --- |
| GET | `/api/health` | Public | Process response and synthetic dataset label |
| GET | `/api/config` | Public | Browser-facing auth/maps/storage flags; no provider key |
| POST | `/api/auth/session` | Public token exchange | Validate supplied Google ID token; return reviewer identity |
| POST | `/api/places/search` | Public | Live directory and optional first-result walking route |
| GET | `/api/status` | Public | Configuration/last-observation provider labels |
| POST | `/api/recommend` | Public | Deterministic candidates; optional advisory Gemini |
| POST | `/api/preview` | Public | Validate request-supplied constraints; persist exact proposal |
| POST | `/api/confirm` | Public | Replay key or check proposal and write synthetic order |
| GET | `/api/ops` | Reviewer | Active orders, fixtures, alerts, decisions, activity and monitoring |
| POST | `/api/ops/decision` | Reviewer | Record accept/reject; execution not performed |
| POST | `/api/ops/order/{order_id}/transition` | Reviewer | Enforce allowlist and record measured-ready timing |
| GET | `/api/owner` | Reviewer | Windowed metrics, recent events and optional owner brief |
| GET | `/api/preferences` | Public | Shared synthetic customer preferences |
| POST | `/api/feedback` | Public | Bounded taste updates plus feedback/event records |
| POST | `/api/reset` | Reviewer | Clear/reseed synthetic state |
| GET | `/api/vision` | Public | Hard-coded feature/status inventory; not proof of deployment |

Static mounts and SPA fallback are additional delivery routes. FastAPI's default OpenAPI/documentation endpoints are framework-provided, not part of the 16 business/API route count.

## Exact record scope and state transitions

The eight tables are `orders`, `proposals`, `preferences`, `feedback`, `prep_observations`, `events`, `decisions`, and `activity`. They do not form eight Firestore collections: the hosted adapter serializes the SQLite database to a single configurable Firestore document (defaults: `cafemesh_state/demo`). There are no declared foreign-key constraints; associations use identifiers and JSON payloads. Recommendations and safety escalations are event kinds, not separate tables.

Current order transitions are:

| Current | Allowed next states |
| --- | --- |
| `confirmed` | `preparing`, `cancelled` |
| `preparing` | `ready`, `cancelled` |
| `ready` | `completed` |
| `completed`, `cancelled` | No outgoing transition |

Marking ready requires a measured value from 1 through the configured maximum (default 180 minutes). This does not resolve the semantic mismatch described in F06.

## Future capability coverage

These come from product/roadmap intent and are **not implemented claims**. View 05 groups them architecturally; this table preserves the feature detail without overloading the drawing.

| Experience / foundation | Future detail represented |
| --- | --- |
| Companion | Verified participating cafés and amenities; reservations/waitlists; arrival-aware preparation; assistance; cancellation/refund/collection rules; current-demand guidance |
| Connect | Opt-in events and interest tables; groups and meet-halfway planning; later person matching only after consent, identity, moderation, block/report and deletion controls |
| Operations | Transactional reserve/release; oversell controls; stations, shifts and handover; actual occupancy/reservations; voluntary Room Pulse; owned service recovery; reviewed forecasts; separate acceptance, execution and outcome |
| Owner | Multi-location comparisons; cancellation/refund/late-order metrics; waste and lost demand; capacity/station bottlenecks; intervention outcomes; contribution margins only with verified cost inputs |
| Administration | Café onboarding; governed menu/ingredient/allergen/cross-contact/price/tax/hours/space records; version and correction history; staff roles; integration health; audit/support; consent/export/deletion |
| Integrations | POS, payments, loyalty and notifications; multilingual conversational voice/Gemini Live; consented location/arrival workflows |
| Data and analytics | Tenant-scoped transactional storage replacing snapshots; outbox/reliable events; canonical definitions, lineage and data-quality checks before BigQuery |
| AI and retrieval | Model Armor; ACL/freshness-aware document ingestion and cited RAG for SOPs/policies; structured services retain authority for price, allergens, stock and commands |
| Harness and evaluation | Prompt/model/tool/version registry; step/time/token/cost budgets; redacted correlated traces; replay/fault injection; reviewed goldens/adversarial sets; optional judge calibrated against human labels; no judge override of hard safety gates |
| Recovery and delivery | Bounded retries/circuits for safe operations; human-reviewed fixes; shadow/canary, exact-version promotion and rollback; protected deployment, image provenance and operational drills |
| Cross-cutting | Tenant/RBAC/least privilege; privacy and retention; accessibility/localization; backups/restore; rate/abuse/cost limits; SLOs/alerts/runbooks; load/concurrency/resilience tests |

No LangGraph, Temporal, vector database, production distributed tracing, automatic self-improvement or real POS/payment workflow is inferred merely because it might be useful.

## Source links

- [Backend routes and runtime coordination](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/main.py)
- [Domain rules, matching, confirmation and metrics](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/service.py)
- [Agent definitions and actual tools](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/agents.py)
- [Persistence adapter and schema](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/db.py)
- [Configuration](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/config.py)
- [Fixture facts](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/data.py)
- [Operational metrics](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/backend/cafemesh/observability.py)
- [Browser UI and flows](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/frontend/src/App.tsx)
- [Application tests](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/tests/test_app.py) and [snapshot tests](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/tests/test_firestore_snapshot.py)
- [CI workflow](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/.github/workflows/quality.yml), [Dockerfile](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/Dockerfile), [Worker](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/deployment/cloudflare/worker.js)
- [TTS generation](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/scripts/generate_voiceover.py) and [video renderer](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/scripts/render_demo_video.py)
- [Deployment documentation: unqueried settings](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/docs/CLOUD-RUN.md)
- [Target product vision](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/docs/01-PRODUCT-VISION.md) and [roadmap](https://github.com/imrohitagrawal/cafemesh-ai/blob/76134e6099c4abd0c04de06227b91e7944cc0a6e/docs/roadmap/README.md)

## Validation of this deliverable

The application code, frontend flows, two test modules, evaluation inputs, CI workflow, container/proxy/configuration, and media-generation paths were inspected. Documentation was compared against these, not used to override them. Binary walkthroughs and screenshots were inventoried as assets; they were not treated as evidence of live application behavior.

All nine diagrams were rendered and visually inspected. SVG XML and editable-scene JSON were parsed; generation checks enforce text width and card height. Route coverage and schema coverage are checked against extracted code inventory. Excalidraw scenes remain editable native JSON, but import into the Excalidraw application was not exercised. Mermaid representations preserve the main relationships rather than the exact designed layout.

Publication verification ran `make verify` (29 tests, TypeScript check and production build passed) and `make demo-smoke` (2/2 synthetic rehearsals passed). No local Docker build, deployment, live provider invocation, browser sign-in or geolocation E2E test was executed. Earlier release/deployment evidence remains historical. See the [atlas validation record](README.md#publication-validation), [developer handoff](DEVELOPER-HANDOFF.md), and [capability matrix](../14-END-TO-END-CAPABILITIES.md).
