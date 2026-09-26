# Architecture

This document shows the running hackathon topology and the intended production direction separately. The current application is a single-service, synthetic-data demo; the target diagrams are not claims that the future services already exist.

## System context (C4 L1)

```mermaid
C4Context
  title CaféMesh AI — system context
  Person(customer, "Customer", "Discovers cafés, explores menu options, previews a synthetic order, and shares preferences.")
  Person(manager, "Café manager", "Reviews synthetic operations signals and records accept/reject decisions.")
  Person(owner, "Café owner", "Reviews metrics derived from shared synthetic records.")
  System(cafemesh, "CaféMesh AI", "Google Cloud hosted café discovery, constrained menu guidance, demo operations, and owner insight.")
  System_Ext(google_identity, "Google Identity", "Signs in authorized demo reviewers; ID tokens are verified by the API.")
  System_Ext(places, "Google Maps Platform", "Live Places directory data and Routes walking estimates.")
  System_Ext(vertex, "Google Agent Platform / Vertex AI", "Optional Gemini model execution through Google ADK.")
  System_Ext(firestore, "Cloud Firestore", "One bounded snapshot document for synthetic hosted demo state.")
  Rel(customer, cafemesh, "Uses public customer experience over HTTPS")
  Rel(manager, cafemesh, "Signs in and reviews demo operations")
  Rel(owner, cafemesh, "Signs in and views demo metrics")
  Rel(cafemesh, google_identity, "Verifies Google ID tokens")
  Rel(cafemesh, places, "Searches cafés and requests walking routes")
  Rel(cafemesh, vertex, "Runs ADK agents when configured")
  Rel(cafemesh, firestore, "Persists synthetic state")
```

## Hackathon containers (C4 L2)

```mermaid
C4Container
  title CaféMesh AI — deployed containers
  Person(user, "Customer / reviewer", "Browser user")
  System_Boundary(cloud, "Google Cloud project · asia-south1") {
    Container(app, "CaféMesh web + API", "Cloud Run · FastAPI", "Serves the built SPA and JSON API; validates inputs, authorizes reviewer actions, enforces business policy, coordinates providers, and writes activity/events.")
    ContainerDb(state, "Demo state", "Firestore snapshot adapter", "One bounded, compare-and-set snapshot of SQLite-format synthetic records; single-instance demo constraint.")
    ContainerDb(local, "Local state", "SQLite", "Default durable local development store.")
  }
  System_Ext(edge, "Cloudflare edge", "Custom-host routing from cafemesh.stackclimb.com to the Cloud Run origin.")
  System_Ext(identity, "Google Identity Services", "Browser sign-in and Google ID token issuer.")
  System_Ext(maps, "Places + Routes APIs", "Live café directory and route estimates.")
  System_Ext(genai, "Vertex AI / Gemini via ADK", "Optional server-side agent execution; no privileged action tools.")
  Rel(user, edge, "HTTPS")
  Rel(edge, app, "Forwards app and API requests")
  Rel(app, state, "Hosted synthetic state")
  Rel(app, local, "Local mode only")
  Rel(app, identity, "Verifies ID token claims")
  Rel(app, maps, "Server-side API-key requests")
  Rel(app, genai, "Optional bounded model request")
```

The Cloud Run service is publicly reachable so anyone can try the customer demo. Reviewer routes require Google sign-in. Cafe/menu/order/occupancy/manager records are synthetic; a live Maps listing does not mean the café participates in ordering. The OAuth consent audience remains in Testing, so protected views are limited to configured testers.

## Runtime components (C4 L3)

```mermaid
flowchart TB
  subgraph Browser[Browser · React + Vite + TypeScript]
    Customer[Customer workspace]
    Operations[Operations and observability]
    Owner[Owner metrics]
    Vision[Vision and walkthroughs]
  end
  subgraph API[FastAPI application · backend/cafemesh]
    Routes[HTTP routes and Pydantic request contracts\nmain.py]
    Auth[Google ID-token verification\nreviewer-route dependency]
    Domain[Recommendation, preview, confirmation, metrics\nservice.py]
    AgentLayer[ADK definitions and read-only fact tools\nagents.py]
    Facts[Menu, café, queue, zones\ndata.py]
    Store[SQLite / Firestore snapshot boundary\ndb.py]
    Events[Events, audit decisions, agent activity]
    Ops[Operational metrics derivation\nobservability.py]
    Maps[Places and Routes provider calls]
  end
  Customer --> Routes
  Operations --> Routes
  Owner --> Routes
  Vision --> Routes
  Routes --> Auth
  Routes --> Domain
  Domain --> Facts
  Domain --> Store
  Routes --> AgentLayer
  AgentLayer --> Facts
  AgentLayer --> Domain
  Routes --> Maps
  Store --> Events
  Routes --> Ops
  Ops --> Store
```

This reflects the current code boundaries, including the intentionally compact `main.py`; it is not a claim of independently deployable microservices. Provider status is represented explicitly. A configured provider error is returned as an error rather than silently converted to a successful demo response.

## Recommendation and safety sequence

```mermaid
sequenceDiagram
  autonumber
  actor Guest as Customer
  participant UI as React UI
  participant API as FastAPI
  participant Rules as Structured retrieval + policy
  participant ADK as ADK agents (optional)
  participant Store as SQLite / Firestore demo state
  Guest->>UI: Request, budget, diet, allergies, time
  UI->>API: POST /api/recommend (validated schema)
  API->>Rules: Match known menu records and apply hard constraints
  Rules->>Store: Record recommendation, evidence, and safety events
  opt Gemini is configured and candidates exist
    API->>ADK: Provide bounded request and authoritative facts
    ADK-->>API: Text and read-tool outcomes
  end
  API->>API: Withhold free-form allergy narrative; retain structured result
  API-->>UI: Candidates, evidence IDs, eligibility, provenance, status
  UI-->>Guest: Explain candidate or staff-review/no-match outcome
```

The ADK layer can interpret and explain but has no order-write tool. Deterministic policy is authoritative. Unknown or stale allergy evidence requires staff review; no menu item is represented as guaranteed allergy-safe.

## Order confirmation sequence

```mermaid
sequenceDiagram
  autonumber
  actor Guest as Customer
  participant UI as React UI
  participant API as FastAPI
  participant Policy as Backend validation
  participant DB as Shared demo store
  Guest->>UI: Select an eligible candidate
  UI->>API: POST /api/preview
  API->>Policy: Validate current menu, constraints, price, stock, opening, queue, safety
  Policy->>DB: Persist exact proposal snapshot
  API-->>UI: Proposal ID and bound item/modifications/price/quantity
  Guest->>UI: Explicitly confirm this preview
  UI->>API: POST /api/confirm + idempotency key + unchanged proposal
  API->>DB: Verify proposal unused and exact snapshot unchanged
  API->>Policy: Revalidate business invariants
  Policy->>DB: Create simulated order and audit event atomically
  API-->>UI: Confirmed synthetic order
  UI-->>Guest: Show demo status and order ID
```

No external café POS, payment, or fulfillment write occurs. A manager accept/reject decision is similarly recorded as a decision; it does not execute staffing or inventory changes.

## Data and trust boundaries

```mermaid
flowchart LR
  Input[Untrusted customer text / browser coordinates / provider response] --> Schema[Pydantic validation and size/range checks]
  Schema --> Retrieval[Structured menu and visit facts]
  Retrieval --> Rules[Deterministic eligibility, safety, budget, and state rules]
  Schema --> Agent[Optional ADK interpretation]
  Retrieval --> Agent
  Agent --> OutputGuard[Output policy and allergy-summary guard]
  Rules --> Response[Structured API response]
  OutputGuard --> Response
  Rules --> ActionGate[Preview + explicit confirmation + idempotency]
  ActionGate --> DemoWrite[(Synthetic demo state only)]
  Rules --> Audit[Evidence IDs, events, decisions, status, latency]
```

User text, retrieved text, tool output, model text, and provider responses are untrusted. They cannot grant authority. React escapes rendered text; backend schemas and code enforce safety, role checks, and state transitions. Secrets stay server-side and are supplied by deployment configuration/Secret Manager, never in browser bundles.

## Persisted-record relationships (logical, not database foreign keys)

```mermaid
erDiagram
  PREFERENCE ||--o{ FEEDBACK : "customer signal"
  RECOMMENDATION ||--o{ SAFETY_EVENT : "may escalate"
  RECOMMENDATION ||--o{ PROPOSAL : "offers candidate"
  PROPOSAL ||--o| ORDER : "confirmed once"
  ORDER ||--o{ PREP_OBSERVATION : "measured outcome"
  ORDER ||--o{ BUSINESS_EVENT : "lifecycle events"
  MANAGER_DECISION }o--|| RECOMMENDATION : "reviews suggestion"
  AGENT_ACTIVITY }o..o{ BUSINESS_EVENT : "observes workflow"
  PREFERENCE {
    string customer_id PK
    json taste_and_safety_profile
  }
  RECOMMENDATION {
    string recommendation_id
    json candidate_ids
    timestamp created_at
  }
  PROPOSAL {
    string proposal_id PK
    json immutable_preview_snapshot
    boolean confirmed
  }
  ORDER {
    string order_id PK
    string idempotency_key UK
    string state
    number predicted_minutes
    number actual_minutes
  }
  FEEDBACK {
    integer feedback_id PK
    string customer_id
    json taste_signal
  }
  PREP_OBSERVATION {
    integer observation_id PK
    number predicted_minutes
    number actual_minutes
    string source
  }
  BUSINESS_EVENT {
    integer event_id PK
    string event_kind
    json event_data
    timestamp created_at
  }
  MANAGER_DECISION {
    integer decision_id PK
    string recommendation
    string accept_or_reject
  }
  AGENT_ACTIVITY {
    integer activity_id PK
    string agent_and_tool
    json evidence_ids
    number latency_ms
    string status
  }
```

The diagram describes the current logical links through IDs and event payloads, not normalized relational constraints. `db.py` stores demo events, preferences, proposals, orders, feedback, decisions, prep observations, and activity. The hosted adapter serializes these records into a single Firestore snapshot; this must be redesigned for a real tenant or concurrent workload.

## Target production architecture (separate from current implementation)

```mermaid
flowchart TB
  Clients[Customer web/mobile · staff console · owner console] --> Edge[Cloud Load Balancing / WAF / rate limits]
  Edge --> Identity[Identity, tenant and role authorization]
  Identity --> API[Versioned FastAPI service on Cloud Run]
  API --> Orchestration[ADK workflow with bounded tools]
  Orchestration --> Policy[Deterministic policy and action authorization]
  Policy --> Catalog[Versioned menu, allergen and policy services]
  Policy --> Inventory[Transactional stock reservation]
  Policy --> Orders[Order lifecycle and outbox]
  API --> Maps[Places / Routes adapters]
  API --> Guard[Model Armor plus deterministic input/output controls]
  API --> Docs[Governed café-document retrieval with citations]
  Catalog --> Firestore[(Tenant-scoped Firestore or fit-for-purpose SQL)]
  Inventory --> Firestore
  Orders --> Firestore
  Firestore --> Events[Analytics export / event pipeline]
  Events --> BQ[(BigQuery)]
  BQ --> Eval[Versioned offline evals and reviewed experiments]
  Eval --> Human[Human review and release gate]
  Human --> Orchestration
  API --> Monitor[Cloud Logging, Monitoring, traces, cost and quality alerts]
```

Production requires an architectural review before adoption: tenant isolation, transactional inventory, access controls, privacy lifecycle, service objectives, backup/restore, rate limits, alert response, and documented data ownership. The snapshot adapter must be replaced; the diagram is a direction, not a deployed system.

## Current integrations and explicit gaps

| Area | Current evidence | Boundary / next engineering step |
| --- | --- | --- |
| ADK + Gemini | Four ADK agent definitions; a live deployed tool interaction was recorded previously. | Model text is advisory; use deterministic facts/rules and human review. No broad judge pipeline. |
| Menu retrieval | Small lexical matching over structured records with deterministic filters. | Not vector search or RAG; three versioned retrieval goldens are only a smoke-sized set. |
| Maps | Live Places results and walking Routes estimate; typed origins and opt-in browser location. | Directory listings do not imply participation; browser permission flow still needs fresh E2E verification. |
| Persistence | Local SQLite; hosted single-document Firestore snapshot with compare-and-set and payload ceiling. | Synthetic demo only; production needs tenant-scoped transactional data model. |
| Operations | Persisted app events, activity, errors, decisions, latency, and prep samples feed the Ops dashboard. | Not Cloud Monitoring, distributed traces, alerting, or production SLO telemetry. |
| Identity | Google ID token verified on protected reviewer routes. | OAuth audience is Testing; no café staff role/tenant authorization system. |
| Narration | Saved Google Cloud TTS `en-IN` asset; no runtime voice session. | Voice chat is not implemented. |
| Model Armor / BigQuery | Not connected. | Roadmap only. |

For the retrieval decision and future document-RAG gates, see [12 — Retrieval and RAG](12-RETRIEVAL-AND-RAG.md). For test scope and safety policies, see [06 — Safety and evaluation](06-SAFETY-AND-EVALUATION.md) and [11 — Verification report](11-VERIFICATION-REPORT.md).
