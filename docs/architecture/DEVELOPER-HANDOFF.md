# Developer handoff — verify and close implementation gaps

Source reviewed: [`76134e6099c4abd0c04de06227b91e7944cc0a6e`](https://github.com/imrohitagrawal/cafemesh-ai/tree/76134e6099c4abd0c04de06227b91e7944cc0a6e). These are static findings to reproduce against the current branch, not newly executed exploits or claims about live infrastructure. Documentation has been corrected; application behavior has not been changed by this publication. The [full audit](ARCHITECTURE-AUDIT.md) supplies evidence and architectural context.

## Suggested order of work

1. **Before any real café pilot:** settle and fix safety freshness, canonical constraint continuity, stock transactions, retry identity, and role/tenant isolation. Define the persistence model before implementing concurrent inventory on the snapshot adapter.
2. **Before relying on demo analytics or timing:** align duration semantics and metric populations; make acceptance cases executable.
3. **Before expanding AI use:** define required-tool/output contracts and provider telemetry, then add focused failure/grounding tests.

Priority here is an engineering recommendation based on potential impact, not a production incident severity. Keep product requirements intact; a failing implementation is not a reason to weaken its acceptance criterion.

## Verification and fix checklist

| ID | Gap and code to inspect | Verification case to add or run | Suggested resolution / closure evidence |
| --- | --- | --- | --- |
| F01 | Safety age is checked in `service.recommend`, not `preview`/`confirm`; inspect `tests/test_app.py` stale test | Use an otherwise eligible item with clear cross-contact evidence but old `updated_at`; test direct preview and an existing proposal after evidence ages | Shared freshness predicate at every consequential stage; all stale paths require review, with focused regressions |
| F02 | Supplied constraints can omit stored/original safety restrictions; inspect `main.order_preview`, `service.recommend/preview`, and UI extraction | Store an allergy, omit it from requests; weaken constraints between recommend/preview/confirm; call preview without recommendation ID | Decide authenticated profile ownership and canonical constraints; bind a server-validated constraint snapshot/version to the proposal; reject weakening |
| F03 | `confirm` ignores proposal `created_at` despite “expired” wording | Confirm a proposal beyond a defined TTL, at the boundary, and with missing/invalid age metadata | Agree validity rules, implement server-side expiry and deterministic clock tests; align API/UI errors |
| F04 | `MENU.available` is checked but `stock_units` is not reserved/decremented | Request quantity above stock, concurrent last-unit confirmations, retry, cancellation and release | Governed inventory plus atomic reserve/commit/release and oversell tests; requires production persistence decision |
| F05 | `confirm` replays a key before comparing the new payload; UI generates a fresh UUID on each attempt | Same key/same payload, same key/different proposal, lost response followed by retry, another actor reusing key | Stable per-command retry key, actor/tenant scope and payload hash; return original result only for an identical command |
| F06 | `prep_estimate`, `transition`, UI duration label and time gates mix total elapsed and prep-only time | With nonzero queue and known measured samples, compare displayed estimate, eligibility and stored accuracy; cover min sample threshold | Choose one duration contract and separate queue/prep/total as needed; align labels, formulas and regression expectations |
| F07 | Earlier agent documentation advertised tools/sources that do not exist; inspect `agents.py` | Enumerate custom tools and their sources; prove no preview/order write tool is exposed | Documentation now matches the three read tools; developer verifies it and either closes the documentation gap or designs any new tool separately |
| F08 | Recommendation helpers are prompted, but not required, to complete menu/visit tools; inspect `run_live_adk` | Fake final text with no tool call, started-but-incomplete call, error tool result and completed call | Decide whether completion is mandatory; enforce and test it if promised. Do not describe instructions as a runtime gate |
| F09 | Owner requires `owner_facts` completion but does not verify narrative numbers/claims | Return a completed tool call followed by invented numbers or unsupported causality | Prefer structured validated output or a defined verifier; withhold unsupported prose; keep authoritative metrics separate |
| F10 | Feedback/decision/transition use dictionaries and confirm nests a generic proposal dictionary | Missing fields, wrong types, excessive lengths, unexpected nested fields and invalid enums through HTTP | Explicit request/nested models and handler invariants; documented errors with no partial write |
| F11 | Google identity is not app reviewer allowlisting or staff/owner/tenant authorization; inspect `require_demo_admin` | Verified unapproved identity, wrong audience/unverified email, role mismatch, cross-tenant access, configured/unconfigured auth | Decide demo reviewer policy; add app authorization where required. Production needs tenant-bound roles and negative tests |
| F12 | Status mixes configuration/last activity; owner errors are not recorded like recommendation errors | Backend selected but inaccessible; old status; failed owner call; process restart; absent TTS asset | Separate configured/last-success/error/timestamp/health semantics, unify error capture, document intentional probe limits |
| F13 | `metrics` includes cancelled orders; repeat visits is count minus one for one demo identity | Mix cancelled/completed orders, boundary windows, multiple customers and missing denominators | Define each KPI's state population, window, identity and denominator; deterministic expected-math tests and accurate labels |
| F14 | `policy-cases.json` is never loaded; test names overstate some assertions | Map every policy case to an executed assertion; intentionally violate an expected condition to establish that its test fails | Implement parameterized coverage where appropriate, or explicitly retain the file as a planning inventory; publish exact coverage |
| F15 | Recommendation lacks the preview opening check and directly compares price | Closed café, missing/null price, unknown item and missing queue at each entry point | Share stage-appropriate validation, fail predictably on unknown data, and test recommendation and action stages independently |

## Additional product prerequisites (planned scope, not defects)

The current implementation intentionally lacks tenant-scoped transactional storage, governed catalog administration, real POS/payment/notification adapters, reservations, station/shift workflows, consent/export/deletion, production SLOs and reviewed deployment promotion. The [end-to-end capability matrix](../14-END-TO-END-CAPABILITIES.md) covers these separately. Do not count them as delivered merely because a future diagram names them.

## Instructions for the implementing agent

Re-read the current source before acting; the reviewed commit may no longer be head. For each finding, report **confirmed**, **partially confirmed**, **not reproduced**, or **superseded**, with code and test evidence. For confirmed gaps, agree the intended behavior where this table identifies a product decision, make a focused fix, add a meaningful regression, and run the repository's required `make verify` plus `make demo-smoke` for application changes.

Return the changed commit, exact commands/results, any remaining limitations, and which finding IDs are closed. Update the architecture, contracts, capability status and audit when behavior changes. Passing existing tests alone does not close a newly identified gap; do not mark a static finding resolved merely by editing its description.
