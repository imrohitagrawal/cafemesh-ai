# Implementation plan and acceptance map

| Work | Acceptance criteria | Verification |
|---|---|---|
| Shared SQLite fixtures and API | One synthetic source feeds all views | `pytest` API/service tests |
| Concierge/taste recommendation | Grounded constraints and facts; unknown safety escalates | safety/eval tests; UI request |
| Preview/confirm | Bound quote, revalidation, idempotency, legal transition | order tests |
| Feedback/learning | Persisted bounded preference; allergy unchanged | learning tests and return journey |
| Ops/Owner | shared orders/events, decision audit, explicit windows | metric/approval tests |
| Vision/safety/status | full horizon, truthful integration states | frontend build and API status checks |
| Container readiness | one container serves SPA and API | Docker image build and local production-mode smoke test passed; rerun after final narration asset update |

Commands: `make setup`, `make verify`, `make demo-smoke`, `make build`, `make serve`. `make demo-smoke` repeats the connected synthetic customer→operations→owner→feedback journey twice. Live-provider commands are documented only when configured; no spend or unrelated Cloud project is assumed.
