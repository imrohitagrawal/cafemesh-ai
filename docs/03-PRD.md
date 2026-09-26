# Product requirements

## Personas and journeys

Customer: state time, diet, safety, budget, drink and seating needs → inspect evidence-backed recommendation → preview → confirm → see preparation and order state → give feedback → return to adjusted recommendation.

Operations/manager: inspect connected orders, estimates and alerts → review grounded recommendation → accept/reject → see an audit record distinct from execution.

Owner: choose an explicit window → see metrics derived from orders/events/feedback → review grounded or deterministic brief → identify insufficient data and possible next action.

## Functional requirements

These are intended requirements. The [code-first audit](architecture/ARCHITECTURE-AUDIT.md) records unmet guarantees, including safety freshness at confirmation, constraint continuity, inventory, timing, and recommendation-stage opening/price checks. The [capability matrix](14-END-TO-END-CAPABILITIES.md) maps the full product to current coverage and future acceptance criteria.

1. Capture canonical request constraints: 40 minutes; vegetarian; severe peanut allergy; cold drink under ₹350; quiet work seat.
2. Recommend only available, priced, open-café candidates; show evidence, price, timing, and safety review status.
3. Detect dietary mismatch, known allergens, unknown/stale ingredients/cross-contact, budget failure, missing price, closed café, missing queue and unknown item without inventing values.
4. Preview and bind confirmation to item, modifications, price, quantity; revalidate; enforce idempotency and legal order transitions.
5. Persist order events visible to Ops and owner metrics.
6. Record feedback and bounded explicit/inferred preferences; explicit preference beats inferred; never infer/learn allergens.
7. Compare predicted/actual prep times and calibrate only from measured outcomes with adequate sample count.
8. Capture AI-quality evaluation candidates for review; no automatic prompt or policy edits.
9. Provide reliable loading, empty, error, retry, reset, provenance, and provider status states.

The reset baseline contains four clearly synthetic orders (three historical and one active), synthetic feedback, and seeded preparation observations. Seeded outcomes are labeled separately from measured outcomes and never count toward calibration.

## Product boundaries

All state is synthetic and isolated. Staff-review confirmations and manager actions are demo actions, not real safety certification or real-world execution. Google ID-token authentication exists for configured reviewer routes; application role/tenant authorization remains planned. No payment, POS, or third-party café business write occurs.

## Target product requirements beyond this MVP

The target product expands into CaféMesh Companion, optional CaféMesh Connect, Operations, Owner Intelligence, and Administration; see `01-PRODUCT-VISION.md` for the complete roadmap. Requirements deliberately deferred from this sprint include:

- **Companion:** work/meeting/social/relax/takeaway intent, participating-café status, verified accessibility/amenities, reservations and waitlists, consented arrival synchronization, current-demand visit timing, customer assistance, and cancellation/refund/tracking policies.
- **Connect:** event and interest-table discovery first; existing-group and meet-halfway planning; later, consented person-to-person matching only after identity, moderation, block/report, and deletion controls exist.
- **Operations:** transactional stock reservation/release; station workload and shift handover; verified occupancy/reservation state; voluntary Room Pulse; service recovery with owner/action/resolution; forecasts; and separate audit records for recommendation, manager acceptance, execution, and outcome.
- **Owner:** defined-window and sourced measures for service, cancellations/refunds, customer return, menu substitutions/lost demand, waste, station/capacity use, and intervention outcomes. Contribution margin and profitability remain unavailable until verified costs are integrated. Reports distinguish observation, hypothesis, and recommendation.
- **Administration:** location onboarding; versioned menu, price/tax, ingredient, allergen/cross-contact, inventory, hours, and space management; role/shift access; integrations and policy status; support/audit tools; and consent, export, deletion, retention, and notification controls for customers.
- **Platform:** tenant isolation, transactional persistence, production roles, POS/payments/loyalty, notification delivery, backups and recovery, operational budgets/incident response, multilingual Gemini Live voice, BigQuery, evaluated recommendations, controlled experiments, and Model Armor as defense in depth.

No real-world ordering or sensitive people-matching capability should move out of this roadmap until its café participation, identity, safety, privacy, consent, and operational controls are ready.
