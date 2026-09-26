# Repository presentation and discoverability

This guide keeps the repository's public description, media and navigation consistent with implemented behavior. The README is the main product and engineering entry point. GitHub's About fields and topics are separate repository settings; committing this file does not apply those settings automatically.

## Repository definition

| Field | Intended value |
| --- | --- |
| Repository name | `cafemesh-ai` |
| Display name | CaféMesh AI |
| Tagline | Your café experience, intelligently connected. |
| About description | A synthetic-data café demo connecting discovery, menu guidance, orders, operations and owner insights with Google ADK/Gemini and Google Cloud. |
| Website | `https://cafemesh.stackclimb.com` |
| Audience | Product reviewers, café workflow stakeholders, and engineers evaluating the demo and target architecture |
| Current maturity | Working synthetic-data demo; known implementation gaps and pilot prerequisites documented |
| Main technical entry point | `docs/architecture/README.md` |
| Full product entry point | `docs/14-END-TO-END-CAPABILITIES.md` |

Use About for the short description, live-demo website and relevant topics. Keep screenshots, video choices, access instructions, architecture and limitations in the README, where they can be explained and versioned.

## Recommended GitHub topics

```text
cafe-management cafe-discovery generative-ai ai-agents google-adk gemini
vertex-ai google-cloud cloud-run firestore fastapi react typescript python
synthetic-data hackathon
```

These terms describe the product domain and actual stack. Do not add `rag`, `payments`, `pos`, `production-ready`, or other planned capabilities as if they were implemented. GitHub topics are discovery labels; Git tags are version references and should follow a separate release decision.

## Public entry points

| Surface | Content |
| --- | --- |
| README first screen | Plain product definition, demo boundary, quality badge, demo/video/architecture links and actual UI preview |
| Video section | Product and engineering walkthroughs, measured lengths, repository fallbacks, clear screenshot-versus-slide labels |
| Screenshot gallery | Customer, Operations, Owner and Vision; descriptive alt text, capture date, full-size links and provenance |
| Capability table | Implemented behavior paired with explicit limitations; planned features linked to the full map |
| Architecture | Firestore-visible system context and nine-view atlas; current versus planned evidence distinguished |
| Documentation | Reader-oriented links plus `docs/README.md` for the complete index |
| Contribution | Bug/feature forms, PR template, contribution/security guidance and existing community conduct policy |
| Media sources | `media/README.md`: assets, scripts, audio, timings, attribution and capture provenance |

## Review findings and maintenance

The 26 September 2026 presentation review found an About description and website, no repository topics, a text-heavy README without inline UI captures, and no repository-specific issue forms or PR template. GitHub displayed community conduct guidance; existing license, security and contribution files were present. No GitHub release or local Git version tag was present at review time. Package version `0.1.0` alone is not a published GitHub release.

The README/media/index/template changes address the file-based presentation gaps. About/topic changes require repository-settings access and should be verified separately. Keep the current repository name and custom license identity; do not relabel the license as standard MIT to obtain a badge or automatic detection.

For a future release, select the tested commit, write accurate release notes, decide a version tag, and attach verified assets as appropriate. Do not invent a release or mark the product production-ready merely to populate the Releases sidebar. A custom social-preview image is optional; choose an authentic sanitized capture or an accurate branded cover and verify it before uploading through repository settings.

When refreshing the presentation:

1. Read the changed code and update current capability claims before editing promotional text.
2. Verify demo/video URLs and relative links; inspect the rendered GitHub README and image loads.
3. Retain screenshot dates, synthetic labels and the distinction between actual UI, slides and target architecture.
4. Run `make verify` as required by `AGENTS.md`; record the actual results and limits.
5. Update About/topics separately when the product definition or implemented stack changes.

The 15-finding [implementation handoff](architecture/DEVELOPER-HANDOFF.md) remains open until code/test evidence closes individual findings. A presentation improvement does not fix application behavior.
