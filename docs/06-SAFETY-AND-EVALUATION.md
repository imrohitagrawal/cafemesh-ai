# Safety and evaluation

The backend owns deterministic checks; model confidence is not evidence, and an agent has no order-write tool. This document distinguishes implemented controls from required guarantees that remain incomplete. The [code-first audit](architecture/ARCHITECTURE-AUDIT.md) and [developer handoff](architecture/DEVELOPER-HANDOFF.md) contain evidence and proposed verification cases.

## Current checks and unresolved gaps

| Area | Implemented behavior | Remaining gap / intended guarantee |
| --- | --- | --- |
| Recommendation safety | Checks supplied diet/allergy constraints, allergen intersection, unknown cross-contact and safety-record age; returns staff-review status; withholds allergy-related model narrative | Stored safety preferences are not universally imposed. Missing-price/opening behavior differs from preview. No safety guarantee should be inferred. F01/F02/F15 |
| Preview and confirmation | Preview saves a bound proposal and supplied constraints; confirmation checks snapshot and business predicates | No repeated safety-age gate or proposal TTL. Optional recommendation linkage checks candidate membership without inheriting the full original constraint set. F01–F03 |
| Inventory | Reads fixture availability and uses stock units for alerts | No quantity-aware reservation, decrement, cancellation release, or concurrent oversell control. F04 |
| Idempotency | Existing key returns its prior order; duplicate key does not create a second order | Replay occurs before incoming proposal comparison, and UI attempts generate new UUIDs. Stable retry keys and conflicting-payload rejection remain work. F05 |
| Order lifecycle | Allowlisted transitions; measured duration required on ready | Confirmation-to-ready measurement is reused as prep time and queue is added again; constraint and display estimates differ. F06 |
| Reviewer access | Verifies Google token audience and required identity claims when configured | No app role/tenant lookup or reviewer allowlist; local mode may be open. OAuth Testing is an external setting, not app authorization. F11 |
| Inputs and models | Pydantic schemas on selected routes plus handler checks; escaped React rendering; narrow read tools and finite configured model timeouts | Some payloads/nested proposals remain dictionaries. Recommendation helper completion and owner prose fact checking are incomplete. F08–F10 |
| Manager and learning | Accept/reject decisions are recorded without execution; feedback never learns safety fields | Stored safety values are not a canonical server-enforced profile across requests. Profile ownership and separately audited safety edits remain requirements. F02 |

All café/order/inventory/staff records are synthetic. There is no POS, payment, or real fulfillment write. Provider requests may still contact Google services when configured. A configured model failure is not silently converted to successful demo output. Provider-status labels are configuration/last-observation evidence, not fresh health checks (F12).

## What evaluation actually executes

`make verify` runs the backend tests, TypeScript checking, and the Vite build. The reviewed source has 29 Python test functions across `tests/test_app.py` and `tests/test_firestore_snapshot.py`; their exact assertions determine coverage. `tests/test_app.py` loads three versioned menu-retrieval goldens for the canonical allergy request, hot espresso, and an unsupported smoothie query.

`evals/policy-cases.json` is a case inventory: no inspected test/script loads it. Related Python tests exist, but listing a case does not demonstrate that its expectation is executed. In particular, the stale-record test does not establish a confirmation-age gate. The snapshot adapter tests use test doubles; they are not live Firestore integration tests. See F01/F14.

`make demo-smoke` rehearses a connected synthetic Customer → Operations → Owner → feedback flow twice. This is bounded regression evidence, not broad safety certification, semantic retrieval evaluation, or an LLM-as-judge pipeline. The [verification report](11-VERIFICATION-REPORT.md) preserves historical results; the architecture publication has its own validation record.

## Required evaluation direction

Fixes should introduce focused regressions for the reproduced gaps, using the developer handoff's verification cases. Define each policy once where feasible and exercise it at every entry point, including direct API calls, retries and conflicting state. Keep deterministic safety/authorization gates separate from language-quality scoring.

A failed or rejected response may become an untrusted evaluation candidate. Human review must establish the facts and expected behavior before promotion to a versioned golden set; regression checks and a release gate precede prompt/model/policy changes. There is no automatic self-editing production loop.
