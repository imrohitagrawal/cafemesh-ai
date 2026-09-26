# Product vision

CaféMesh AI connects a guest's intent, café service, and owner decisions across the complete café visit: **Your café experience, intelligently connected.** The product helps people discover and plan a visit, helps teams serve safely and recover well, and turns observed outcomes into better reviewed decisions.

## Product experiences

1. **CaféMesh Companion — customer:** discover participating cafés, plan for work, a meeting, social time, relaxation, or takeaway; inspect evidence-backed food and drink choices; enforce hard constraints; order; coordinate arrival; select a suitable space; request help; and give feedback.
2. **CaféMesh Connect — opt-in community:** find café events and interest tables, coordinate with an existing group, and eventually discover a suitable halfway café. Person-to-person matching is gated on explicit consent, moderation, and controls to leave, hide, block, and report.
3. **CaféMesh Operations — café team:** coordinate orders, preparation stations, queue, inventory, occupancy, safety reviews, service recovery, handover, and manager-approved recommendations.
4. **CaféMesh Owner Intelligence — owner and regional leads:** understand commercial performance, service quality, menu performance, customer experience, operational effectiveness, and improvement opportunities across explicit reporting windows.
5. **CaféMesh Administration — café administrators:** onboard locations, maintain authoritative menu and safety records, manage staff roles and access, configure integrations and policies, and support customer data controls.

Trust, observability, and controlled learning span all five experiences.

The detailed delivery roadmap separates complete end-to-end product slices from shared horizontal enablers and defines scale-up triggers. See [the roadmap index](roadmap/README.md) and [engineering practice review](13-ENGINEERING-PRACTICES.md) for what exists today versus what must be added for a café pilot.

For a diagram and feature-by-feature mapping of the complete product, current code coverage, and acceptance criteria, see [end-to-end capability coverage](14-END-TO-END-CAPABILITIES.md). Existing implementation gaps remain in the [code-first audit](architecture/ARCHITECTURE-AUDIT.md).

## Complete customer journey

Discover → plan → personalize → validate constraints → coordinate travel and preparation → confirm an order → prepare → arrive → seat → experience → get help if needed → feedback → learn → operate → analyze → improve → return.

A listing found through Maps is not automatically a participating café. Live directory information must not be confused with a café's verified menu, stock, staff, ordering, seating, or reservation system.

## Capability roadmap

### Hackathon MVP — implemented or integrated now

One synthetic café; Customer, Operations, Owner, and Vision UI; deterministic safety and order rules; simulated ordering and manager decisions; shared Firestore state in the deployed demo with local SQLite mode; bounded feedback and preparation calibration; a lightweight persisted-events monitoring view; live Places/Routes discovery; Google Sign-In protection for reviewer workspaces; ADK/Gemini through Vertex AI; and a generated Indian-English Despina walkthrough. See `02-HACKATHON-SCOPE.md` and `11-VERIFICATION-REPORT.md` for exact status and limits.

### Café pilot — prerequisites before connecting a real café

Tenant isolation and role-based authentication; café onboarding; authorized menu, ingredient, price, allergen, cross-contact, stock, hours, and space editing with review history; transactional inventory reservations; staff/station and shift workflows; customer consent and preference inspection/edit/reset/export/deletion; cancellation and refund policies; notification consent; recovery runbooks; backup/restore; production monitoring, budgets, and incident response; and one approved café-system integration in a controlled pilot. A live map result alone never enables a real order.

### Complete product — staged future scope

- **Companion:** supported reservations and waitlists with capacity, expiry, cancellation, and no-show rules; verified accessible/social/quiet/meeting spaces; current demand and best-time guidance; arrival-aware preparation; assistance requests; and order tracking across accepted, preparing, ready, collected, cancelled, refunded states.
- **Connect:** optional quiet/open-to-conversation/event modes; customer-selected interests; café events and moderated interest tables; consented join requests; group constraints and coordinated orders; meet-halfway discovery; and leave/hide/block/report controls. Begin with events and interest tables; defer direct person matching until identity and moderation are mature.
- **Operations:** station workload and preparation routing; stock reservation/release and oversell prevention; real occupancy/reservation updates; voluntary Room Pulse (noise, cleanliness, comfort, Wi-Fi, service); service recovery with owner, action, and resolution follow-up; shift handover; demand/stockout/staff forecasts; and recommendations whose acceptance, execution, and outcome remain separate audited records.
- **Owner:** cancellations/refunds, late orders, preparation accuracy, complaint and resolution time, repeat visits, preference corrections, recommendation conversion, substitutions and lost demand, waste, station bottlenecks, capacity utilization, and intervention outcomes. Ingredient cost and contribution margin appear only when authoritative cost data exists. Multi-location comparisons use consistent definitions and windows. Briefs separate observations, hypotheses, and recommendations; correlation is never presented as causation.
- **Administration and platform:** café/location onboarding, menu variants/taxes/versioning, safety-record review, role and shift access, integration health, support/audit investigation, customer consent/data controls, reliable notifications, localization, and tenant-scoped retention and deletion.
- **Intelligence and integrations:** conversational Gemini Live and multilingual voice; POS, payments, loyalty/rewards, and notifications; arrival synchronization; demand, inventory, and staffing models; multi-location intelligence; BigQuery; reviewed recommendation models; controlled experiments; and Model Armor as an added input/output defense. Deterministic policy controls remain in force regardless.

## Learning and human boundaries

1. **Customer learning:** bounded, visible, reversible taste and seating preferences. Explicit preferences override inferred tendencies. Allergies, religious restrictions, and other safety rules are never learned or relaxed. Customers can inspect, change, reset, and eventually delete profile data.
2. **Operations learning:** compare predicted and measured preparation time; distinguish seeded history from observed outcomes; reject unreasonable durations; calibrate only with enough measured samples.
3. **AI-quality learning:** record failures and rejected answers as candidates, require human review before promoting trusted evaluation cases, and require regression checks before changing prompts or policy. Production behavior never rewrites itself.

Customers explicitly confirm the exact order proposal. Authorized staff review uncertain safety facts. Managers decide whether to accept recommendations. Recommendation acceptance, real-world execution, and outcome are different events. No demo action creates a real café order, moves staff, charges a payment, or reserves a real seat.
