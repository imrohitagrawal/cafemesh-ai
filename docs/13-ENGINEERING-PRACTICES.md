# Engineering review and production-readiness roadmap

This is a review of the current public hackathon demo against practices expected in a maintained AI product. It distinguishes controls already implemented from work required before a café pilot. It is intentionally candid: passing the current tests does not certify production safety or reliability.

## Practices present in this repository

- **Reproducible application dependencies:** `uv.lock` and `frontend/package-lock.json` are checked in; Docker uses `npm ci` and the locked Python environment. `make verify` covers backend tests, TypeScript checking, and a production frontend build.
- **Layered policy for consequential actions:** Pydantic validates HTTP inputs; deterministic backend rules own constraints, recommendation eligibility, order confirmation, idempotency, order transitions, and manager decision records. Agents have read tools, not privileged write tools.
- **Grounding and uncertainty:** recommendations expose structured records and evidence IDs; unknown/stale allergy evidence requests staff review; no-match remains no-match; no allergy-safe guarantee is made.
- **Explicit provider states:** live, demo, unavailable, and error states are surfaced; provider failure is not silently converted to demo success.
- **AI regression evidence:** deterministic safety tests and versioned menu retrieval cases exist. Rejected/error activity can be reviewed; human review and regression verification are required before a case or policy is promoted.
- **Shared demo events and observability:** Customer, Operations, and Owner views derive from shared stored records; operations activity, errors, tool latency, decisions, and measured preparation outcomes are inspectable.
- **Secret boundaries:** `.env`, databases, virtual environments, caches, and build output are ignored by Git. Runtime credentials are configured server-side; the public app contains no server API key.
- **Public reuse terms:** the owner selected a CaféMesh AI MIT + Attribution license adapted from their Quorum-AI license; the full terms and end-user-visible attribution are included. This is a custom license, not standard MIT.
- **Deployment evidence:** one Dockerized Cloud Run service hosts UI and API; the current public demo uses synthetic café state and is documented with verification evidence.

## Practices that remain limited or absent

| Priority | Gap | Before what milestone | Concrete next step |
| --- | --- | --- | --- |
| P0 | Firestore is one SQLite-format snapshot with single-instance assumptions, not tenant-safe transactional persistence. | Any café pilot or concurrent real users | Replace with tenant-scoped records and transactional inventory/order writes; test concurrent confirmation and recovery. |
| P0 | Identity distinguishes signed-in reviewer from anonymous customer, not staff/manager/owner roles within café tenants. | Real staff/owner access | Add verified role and tenant claims, least privilege, revocation, audit, and negative authorization tests. |
| P0 | Menu/allergen/stock/occupancy records are synthetic and mostly code fixtures; no authorized café data owner/version workflow. | Any real safety or service claim | Add authenticated administration, provenance, review/expiry, version history, and accountable source owners. |
| P1 | Current telemetry is an application dashboard over persisted demo rows; no Cloud Monitoring alert policies, distributed traces, uptime objective, or incident runbook. | Public pilot SLO | Add request IDs, structured logs, traces, SLO definitions, alert ownership, and a tested incident playbook. |
| P1 | Evaluation is intentionally small: deterministic policies plus three retrieval goldens; no broad adversarial corpus, calibrated LLM-as-judge, or online quality program. | Expanding AI use | Build reviewed, versioned datasets; deterministic hard gates; human-labeled judge calibration/agreement; model/version regression reports. Never let a judge override safety policy. |
| P1 | No document RAG. Structured menu facts should remain tools; future RAG is for governed SOP/accessibility/service documents. | Adding long-form café knowledge | Implement tenant-scoped citations, document freshness/access checks, retrieval/no-answer thresholds, and retrieval + answer-grounding evaluations before rollout. |
| P1 | No explicit app-level rate limiting, abuse budget, or cost/usage budget for public AI calls. | Broader public traffic | Add shared rate limits, request quotas, concurrency and token caps, per-provider budgets, and abuse monitoring. |
| P1 | Privacy lifecycle is minimal for synthetic demo data; no user export/deletion/retention workflow for a production profile. | Collecting real preferences | Define consent, data inventory, retention, deletion/export paths, and ensure logs/backups/provider payloads follow policy. |
| P2 | Deployment currently documents a manual Cloud Run command; no reviewed release workflow, staged promotion, rollback drill, or SBOM/signature attestations. | Stable pilot operations | Automate build/test/deploy with protected environments, immutable image digests, provenance, rollback, and post-deploy smoke checks. |
| P2 | No accessibility, localization, cross-browser, load, concurrency, or resilience test program beyond the current checks. | General availability | Add WCAG review, supported-browser matrix, API load/failure tests, and tested restore/scale behavior. |
| P2 | No feature-flagged experiment framework or controlled prompt/model rollout. | Iterative AI tuning | Version prompts/models, keep a change log, evaluate offline, use human release gates and bounded canaries. |

## AI quality and evaluation discipline

An appropriate future quality pipeline is:

1. Capture a privacy-minimized failure/rejection as an **untrusted candidate**.
2. A reviewer verifies the user intent, authoritative facts, expected response, and whether the case is safe to retain.
3. Promote an approved case into a versioned golden set with tags, source/version context, expected citations or policy outcomes, and a rubric.
4. Run deterministic safety and authorization gates first. Failures cannot be offset by a high language-quality score.
5. Run retrieval metrics (for example, recall@k and citation/source coverage) and answer metrics (groundedness, completeness, refusal correctness) on a representative held-out set.
6. If using an LLM judge, calibrate it against blinded human labels, report agreement and disagreement, test judge stability/bias, and retain human adjudication for high-impact cases. A judge is a measurement instrument, never an action authority.
7. Compare exact prompt, model, tool, and dataset versions; require review and regression pass before staged promotion; monitor drift and rollback signals.

This pipeline is a recommended direction, not currently implemented. The engineering walkthrough must say so clearly. Current verified evaluation consists of the tests and small retrieval goldens listed in [11 — Verification report](11-VERIFICATION-REPORT.md).

## Repository map and ownership boundaries

```text
backend/cafemesh/    FastAPI routes, typed configuration, domain rules, providers, persistence, observability
frontend/src/        React experience for Customer, Operations, Owner, and Vision
tests/               Deterministic API, policy, persistence, and integration tests
evals/               Versioned retrieval and policy cases (synthetic)
docs/                Product contract, architecture, safety, deployment, demo, and review evidence
scripts/             Repeatable demo, media, and screenshot-preparation tasks
media/               Narration scripts, timing manifests, and sanitized supplied captures
deployment/          Cloudflare routing configuration used by the hosted custom domain
```

The current project is intentionally a compact hackathon monolith. A real multi-team product should split modules only when ownership, test seams, or independent scaling justify it; it should not create microservices merely to look enterprise-ready.

## Release checklist for this demo repository

- [ ] `make verify` and `make demo-smoke` pass on the exact commit.
- [ ] `gitleaks` reports no credentials in files or history; `.env` and unredacted originals are excluded.
- [ ] Dependency audit findings are reviewed; lockfiles are committed.
- [ ] Docker build and health route pass; hosted revision and media URLs are checked after deploy.
- [ ] Authenticated and unauthenticated reviewer routes are both verified.
- [ ] Claims in README, Vision, walkthrough narration, and verification report agree on what is live, synthetic, unavailable, and planned.
- [ ] Rollback path and current Cloud Run revision are recorded.

## Product roadmaps that must remain explicit

- **Hackathon/demo:** shared synthetic lifecycle, deterministic safety and action controls, four read-oriented ADK roles, live Places/Routes, Google reviewer sign-in, Cloud Run, Firestore snapshot persistence, demo operations/owner views, and bounded verification.
- **Café pilot:** tenant/role isolation, governed menu and safety records, normalized transactional persistence, stock/order consistency, customer consent/deletion, notifications/cancellations, operational support, monitoring/alerts, backups, and evaluated AI changes.
- **Longer horizon:** document RAG with citations, reservations and arrival synchronization, group/meet-halfway experiences, POS/payments/loyalty, multilingual voice, demand/staffing forecasts, multi-location insights, BigQuery, Model Armor, and controlled experiments.

The capability-to-user matrix, vertical/horizontal slicing, dependencies, release gates, and scale triggers are maintained in the [roadmap index](roadmap/README.md). Update it whenever product promises or deployment constraints change.
