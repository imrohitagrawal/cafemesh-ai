# CaféMesh AI

**Your café experience, intelligently connected.**

CaféMesh AI is a Google Cloud hosted hackathon application connecting customer discovery and constrained menu guidance with café operations and owner insight. It includes a public customer demo, Google-signed reviewer views, a shared synthetic-data workflow, live Google Maps discovery, and two narrated walkthroughs. The repo documents what is implemented, simulated, unavailable, and planned; the roadmap is not a claim of shipped functionality.

[![Quality workflow](https://github.com/imrohitagrawal/cafemesh-ai/actions/workflows/quality.yml/badge.svg?branch=master)](https://github.com/imrohitagrawal/cafemesh-ai/actions/workflows/quality.yml)

## Try the application and media

- **Public source repository:** [github.com/imrohitagrawal/cafemesh-ai](https://github.com/imrohitagrawal/cafemesh-ai)
- **Live application:** [cafemesh.stackclimb.com](https://cafemesh.stackclimb.com)
- **Product walkthrough video:** [MP4](https://cafemesh.stackclimb.com/videos/cafemesh-product-walkthrough.mp4?v=20260926-public-release) · [source audio](frontend/public/audio/cafemesh-product-walkthrough.mp3) · [narration script](media/cafemesh-product-walkthrough.txt)
- **Engineering walkthrough video:** [MP4](https://cafemesh.stackclimb.com/videos/cafemesh-engineering-walkthrough.mp4?v=20260926-public-release) · [source audio](frontend/public/audio/cafemesh-engineering-walkthrough.mp3) · [narration script](media/cafemesh-engineering-walkthrough.txt)
- **Short demo video:** [MP4](media/cafemesh-two-minute-demo.mp4)
- **Screenshots:** sanitized owner-supplied captures used in the videos are mapped in [media/provided-app-screenshots/README.md](media/provided-app-screenshots/README.md). Unredacted originals are intentionally outside this repository.

The videos use paragraph-matched point-in-time app screenshots and narration. They are not continuous screen recordings or word-level lip sync. The deployed UI and videos are public; reviewer Operations/Owner views require Google sign-in and are currently restricted by the OAuth project's Testing audience. Café menu, allergen, inventory, orders, occupancy, and manager actions in the demo are synthetic. Google Places and Routes directory/route results are live and separate from the synthetic café catalog.

## What works in this release

- **Customer:** capture visit intent and constraints; retrieve structured menu items; show evidence, price, time, and safety-review status; preview and explicitly confirm an eligible synthetic order; collect feedback and persist bounded taste preferences.
- **Operations:** see shared synthetic orders, transitions, preparation estimates, stock/occupancy/safety alerts, provider/tool activity, errors, latency, manager decisions, and learning signals. Managers can accept/reject recommendations; this records a decision but does not execute a real-world change.
- **Owner:** see time-windowed metrics and a grounded owner brief from the same records; unavailable measurements remain explicit.
- **Vision:** review the full product journey, live/demo/planned boundaries, architecture, and roadmap.
- **Google services:** Cloud Run hosting, Google Identity ID-token verification for protected reviewer routes, live Places/Routes, optional ADK/Gemini through Vertex AI, Firestore-backed synthetic demo state, and saved Indian-English Google TTS narration.

See [product scope](docs/02-HACKATHON-SCOPE.md), [architecture](docs/04-ARCHITECTURE.md), and [verification evidence](docs/11-VERIFICATION-REPORT.md) for exact status and caveats.

## Run locally

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer and npm
- [`uv`](https://docs.astral.sh/uv/) for the locked Python environment

### Install and start

```sh
make setup
make dev
```

Open <http://localhost:5173> for the Vite development UI. The API is at <http://localhost:8000> and its OpenAPI page at <http://localhost:8000/docs>. For a single-port production-style local run:

```sh
make build
make serve
```

Then open <http://localhost:8000>. Local synthetic state is stored in `data/cafemesh.db`. Use the in-app reset control to restore the seeded demo state. Never point this demo reset control at real business records.

### Optional provider setup

Copy `.env.example` to `.env`. Defaults use SQLite and deterministic demo behavior; no Google credential is needed to explore locally. To use a live provider, configure only the server-side variables documented in the example. For Vertex AI, use Application Default Credentials or the attached Cloud Run service identity, set `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION`, and ensure the project/API/IAM setup is valid. For Maps, set a restricted server-side `GOOGLE_MAPS_API_KEY`. Never use a secret in a `VITE_*` variable or check `.env` into Git.

When sign-in is configured, set `GOOGLE_CLIENT_ID` and `CAFEMESH_REQUIRE_GOOGLE_AUTH=true` to protect reviewer routes. A local Google OAuth client must include the exact browser origin in Authorized JavaScript origins. See [Cloud Run setup](docs/CLOUD-RUN.md) for deployment identity, APIs, domain routing, and current hosted limitations.

Provider failures stay visible; they do not silently return a successful deterministic fallback. Integration state is available from `/api/status` and the Operations view.

## Verification

```sh
make verify       # Backend tests, TypeScript check, Vite production build
make demo-smoke   # Rehearses the synthetic Customer → Ops → Owner → feedback flow twice
```

Current evidence and limitations are recorded in [docs/11-VERIFICATION-REPORT.md](docs/11-VERIFICATION-REPORT.md). The current deterministic retrieval goldens and policy cases are under [`evals/`](evals/). These are bounded regression evidence, not proof of total safety, broad semantic retrieval quality, or a production SLO.

## Architecture, practices, and roadmap

- [System context, C4 containers/components, runtime sequences, data boundaries, and target architecture](docs/04-ARCHITECTURE.md)
- [Roadmap overview: horizons, vertical product slices, horizontal enablers, scaling triggers, and agent harness direction](docs/roadmap/README.md)
- [Café pilot slice detail and cross-cutting prerequisites](docs/roadmap/README.md#vertical-product-slices)
- [Agent harness, self-healing, and controlled self-improvement applicability](docs/roadmap/README.md#agentic-ai-self-improvement-and-operational-recovery)
- [Engineering-practice review: present controls, pilot blockers, AI evaluation, and release gates](docs/13-ENGINEERING-PRACTICES.md)
- [Agent permissions and contracts](docs/05-AGENT-CONTRACTS.md)
- [Safety and evaluation policy](docs/06-SAFETY-AND-EVALUATION.md)
- [Retrieval and future RAG decision](docs/12-RETRIEVAL-AND-RAG.md)
- [Deployment and operations notes](docs/CLOUD-RUN.md)

The roadmap maps capabilities to customer, café-team, and owner outcomes, and distinguishes vertical end-to-end product slices from horizontal platform enablers. Future agent harness, RAG, calibrated LLM-as-a-judge, self-healing, and self-improvement are described with applicability and human-control gates; they are not presented as implemented today.

## Repository map

```text
backend/cafemesh/    FastAPI app, domain policy, agent tools, persistence, observability
frontend/src/        React + TypeScript UI
tests/               Backend policy, API, and storage tests
evals/               Synthetic deterministic policy/retrieval cases
docs/                Product, contracts, architecture, safety, release evidence, roadmap
docs/roadmap/        Horizontally and vertically sliced future plan and scale triggers
scripts/             Demo rehearsal, narration, screenshot and video workflows
media/               Narration sources, timing manifests, sanitized screenshot scenes
deployment/          Cloudflare origin-routing configuration
```

## Security and public-repository notes

- This is a public demo with synthetic business data. Do not add customer records, café credentials, provider keys, OAuth secrets, or unredacted personal screenshots.
- `.env`, local databases, virtual environments, package caches, and build output are Git-ignored. `.env.example` contains placeholders only.
- Runtime credentials belong in Google Secret Manager or workload identity/ADC; use least privilege and server-side access.
- Google sign-in currently identifies authorized demo reviewers; it is not production café role/tenant authorization.
- `gitleaks` and lockfile/package audits should be run before public releases. Review the full release checklist in [engineering practices](docs/13-ENGINEERING-PRACTICES.md).
- GitHub Actions runs tests/build, the connected demo rehearsal, JavaScript dependency audit, Docker build, and a history-aware secret scan on push/PR and weekly.
- The app does not place real orders, charge payments, update a POS, reserve real seating, or dispatch staff.
- Security reports and contribution guidance are in [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## License and contribution status

This repository uses the [CaféMesh AI Source Code License (MIT + Attribution)](LICENSE), adapted at the owner's direction from their Quorum-AI repository license. It is a custom MIT-derived license, not the standard MIT SPDX license. Redistributions and derivative works must preserve the copyright/permission notice and visible end-user attribution in `NOTICE`; the CaféMesh footer provides that notice in the hosted UI. Review the complete terms before reuse. Contribution/release conventions are in [CONTRIBUTING.md](CONTRIBUTING.md).
