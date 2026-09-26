# Hackathon scope

No hackathon rules, submission materials, or judging criteria were supplied or discovered in the workspace. This scope follows the approved product direction and does not claim eligibility or compliance with unknown rules.

## MVP

Synthetic single-café app; Customer, Operations, Owner, Vision; local SQLite with Cloud Firestore demo-state adapter; grounded recommendations; deterministic dietary/allergen checks; explicit preview/confirmation; order lifecycle; queue/occupancy and safety review; manager accept/reject audit; shared event-derived owner metrics; feedback and bounded preference learning; preparation-time calibration; ADK/Gemini agents configured through Vertex AI; live Places/Routes discovery; Google Sign-In with External/Testing audience and owner test user; Indian-English Despina Gemini-TTS narration; persistent Ops monitoring panel; verified public Cloud Run deployment.

## Stretch

Public OAuth consent publication for admin/reviewer access beyond the listed owner tester; a polished Gemini Live voice interaction; meet-halfway discovery for groups; Model Armor; richer calibration visualization; and an in-product reviewed evaluation-candidate workflow. MVP Gemini, Places, Routes, Firestore, Google Sign-In, and Cloud Run integrations are connected; verification evidence and known caveats are in `11-VERIFICATION-REPORT.md`.

## Café pilot prerequisites

Before connecting a real café: tenant isolation and role-based access; café onboarding; reviewed menu/ingredient/allergen/cross-contact/price/stock/hours/space administration with history; transactional stock reservations; staff/station/shift operations; customer consent and profile inspection/edit/reset/export/deletion; cancellation/refund and notification policies; backups, monitoring budgets, incident support, and a controlled approved system integration. Maps listings alone do not imply café participation.

## Future product scope

The roadmap is further organized into customer/team/owner **vertical product slices** and cross-cutting **horizontal platform enablers**, with horizon gates and scaling triggers. See [docs/roadmap/README.md](roadmap/README.md). This prevents roadmap capability names from being mistaken for shipped features and makes dependencies reviewable.

- **Companion:** verified amenities and accessible/quiet/meeting spaces; reservations/waitlists; best-time and demand guidance; arrival-synchronized preparation; assistance; cancellation/refund/collection tracking.
- **CaféMesh Connect:** opt-in event and interest-table modes, group preferences/orders, meet-halfway discovery, and consented join requests. Person-to-person matching requires moderation, reporting/block controls, and privacy review.
- **Operations:** station routing/workload, inventory reserve/release/oversell controls, real occupancy and reservations, voluntary Room Pulse, owned service recovery, shift handover, and reviewed demand/inventory/staffing forecasts.
- **Owner:** richer service quality, cancellation/refund, late-order, waste, substitution/lost-demand, station/capacity, intervention, and multi-location metrics. Margin/profit requires verified cost inputs; every metric has a definition/window/source; briefs separate observation from hypothesis.
- **Administration:** location onboarding, versioned menu/tax/safety records, staff roles/shifts, integration health, audit/support, customer consent/data controls, retention/deletion, and notifications.
- **Platform:** POS, payments, loyalty, multilingual Gemini Live voice, BigQuery, recommendation models, controlled experiments, Model Armor, and production-scale tenancy/authentication. See `01-PRODUCT-VISION.md` for the full capability map and prerequisites.

## Acceptance requirements and current gaps

The following are acceptance requirements, not a claim that every guarantee is implemented. The [audit](architecture/ARCHITECTURE-AUDIT.md) found missing safety-age rechecks at confirmation, incomplete constraint continuity, no stock reservation or proposal TTL, and timing/idempotency limitations. These remain open implementation work; see the [developer handoff](architecture/DEVELOPER-HANDOFF.md).

- All customer, operations, and owner screens read/write the same persisted records.
- Unknown/stale safety evidence blocks confirmation and clearly requests staff review.
- Confirmation is bound to the preview and revalidates policy, price, stock, and opening.
- Duplicate idempotency keys cannot create another order.
- Operational recommendations require manager decision and only record that decision.
- Owner metrics are calculated from shared records/events and show insufficient data where appropriate.
- Feedback persists bounded preferences; explicit safety restrictions remain unchanged.
- Every provider state is labeled live, demo, unavailable, or error.
