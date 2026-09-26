# Contributing

The repository's reuse terms are defined in [LICENSE](LICENSE) and [NOTICE](NOTICE). A pull request does not grant rights beyond those terms or establish a separate contribution license agreement. The project owner has not adopted a separate contribution license agreement.

## Before opening a pull request

1. Keep changes focused and explain the user or engineering outcome.
2. Do not include secrets, real café/customer data, unredacted screenshots, generated local databases, or private credentials.
3. Update the relevant product/architecture/roadmap/verification document when behavior or capability status changes.
4. Run `make verify` and `make demo-smoke` for application changes. Add a regression test for a reproduced contract or safety defect.
5. Keep provider integrations behind explicit adapters and surface `live`, `demo`, `unavailable`, and `error` states honestly.
6. Do not let model output authorize safety, order, inventory, staff, or policy changes. Keep high-impact changes behind deterministic checks and an explicit human gate.

GitHub Actions repeats tests, the demo rehearsal, frontend dependency audit, Docker build, and secret scanning on pushes and pull requests. No external service should be contacted and no real café action should be performed by a test.

## Issues, proposals and review evidence

Use the repository issue forms for reproducible bugs and scoped feature proposals. Check the [developer handoff](docs/architecture/DEVELOPER-HANDOFF.md) and [capability map](docs/14-END-TO-END-CAPABILITIES.md) first, and reference the relevant finding or planned workflow. The pull-request template asks for the problem, resulting behavior, actual validation results and remaining limits.

For README, diagram or media changes, verify relative links and rendered output, label capture dates and planned capabilities, and follow the [presentation guide](docs/REPOSITORY-PRESENTATION.md). Existing community conduct guidance shown by GitHub continues to apply.
