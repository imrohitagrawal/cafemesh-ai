# Learning loops

See [state and learning](architecture/06-state-and-learning.svg) and audit findings F02/F06/F12/F13 for exact current boundaries.

## Customer feedback

Feedback adjusts four persisted preference weights (oat milk, sweetness, caramel, and quiet seating), bounded to −3…3, with explicit markers. Current feedback logic increases selected positive signals; it is not a general model of dislikes or contradictory feedback. The UI shows signals and effects, and demo reset is available.

Safety fields are excluded from learning. This does not mean stored allergies are automatically enforced: recommendation and the ordinary preview API use supplied constraints, and recommendation linkage does not restore the full original constraints. Canonical profile ownership, explicit safety editing/audit, and server-bound constraint continuity remain work (F02).

## Operational calibration

`prep_observations` distinguishes seeded history from measured outcomes. Seeded samples never calibrate estimates. The estimator uses the latest 20 measured samples once the configured minimum is met (default three); transition validation bounds supplied durations (default 1–180 minutes).

**Unresolved measurement mismatch (F06):** the UI requests confirmation-to-ready time, but the estimator treats the average as preparation time and adds queue wait again. Time eligibility uses fixture prep plus queue, rather than the same calibrated estimate shown to users. Agree on preparation-only versus total elapsed semantics, then align collection, calculation, labels, and tests before interpreting accuracy.

## Owner analytics

Owner metrics derive from shared records over a requested window, but the current order population includes cancelled rows. Repeat visits are count minus one for the single synthetic customer. These demo formulas are not validated business KPIs; define states, identity, windows, and denominators before pilot analytics (F13).

## AI-quality review

Persisted error/review activity produces visible, unpromoted signals in Operations. Coverage is uneven: owner errors do not follow the same persistence path as recommendation errors, and provider status is not a comprehensive health check (F12). There is no automatic golden-case, prompt, or policy promotion.

User-rejected-answer capture and an in-product review/promotion workflow remain planned. A human must verify each candidate and regression results before any prompt/policy change. Future experimentation should version prompts, models, tools, datasets and metrics, with bounded rollout and rollback.
