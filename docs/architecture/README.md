# CaféMesh AI architecture atlas

Nine code-reviewed architecture and product views. Implementation evidence is pinned to [`76134e6099c4abd0c04de06227b91e7944cc0a6e`](https://github.com/imrohitagrawal/cafemesh-ai/tree/76134e6099c4abd0c04de06227b91e7944cc0a6e), reviewed on 26 September 2026. The publication changes documentation and assets; it does not fix the recorded application gaps.

Start with the [architecture narrative](../04-ARCHITECTURE.md), [full audit](ARCHITECTURE-AUDIT.md), [developer gap handoff](DEVELOPER-HANDOFF.md), or [end-to-end capability matrix](../14-END-TO-END-CAPABILITIES.md).

| View | Primary image | Raster | Editable scene | Relationship source |
| --- | --- | --- | --- | --- |
| 01 — System context, including Firestore | [SVG](01-c4-system-context.svg) | [PNG](01-c4-system-context.png) | [Excalidraw](01-c4-system-context.excalidraw) | [Mermaid](01-c4-system-context.mmd) |
| 02 — Containers and deployment | [SVG](02-c4-containers-deployment.svg) | [PNG](02-c4-containers-deployment.png) | [Excalidraw](02-c4-containers-deployment.excalidraw) | [Mermaid](02-c4-containers-deployment.mmd) |
| 03 — Runtime components | [SVG](03-c4-runtime-components.svg) | [PNG](03-c4-runtime-components.png) | [Excalidraw](03-c4-runtime-components.excalidraw) | [Mermaid](03-c4-runtime-components.mmd) |
| 04 — Trusted AI and action flow | [SVG](04-trusted-ai-request-flow.svg) | [PNG](04-trusted-ai-request-flow.png) | [Excalidraw](04-trusted-ai-request-flow.excalidraw) | [Mermaid](04-trusted-ai-request-flow.mmd) |
| 05 — Planned production reference | [SVG](05-target-production-architecture.svg) | [PNG](05-target-production-architecture.png) | [Excalidraw](05-target-production-architecture.excalidraw) | [Mermaid](05-target-production-architecture.mmd) |
| 06 — State and learning | [SVG](06-state-and-learning.svg) | [PNG](06-state-and-learning.png) | [Excalidraw](06-state-and-learning.excalidraw) | [Mermaid](06-state-and-learning.mmd) |
| 07 — Agent execution | [SVG](07-agent-execution.svg) | [PNG](07-agent-execution.png) | [Excalidraw](07-agent-execution.excalidraw) | [Mermaid](07-agent-execution.mmd) |
| 08 — Delivery and media | [SVG](08-delivery-and-media.svg) | [PNG](08-delivery-and-media.png) | [Excalidraw](08-delivery-and-media.excalidraw) | [Mermaid](08-delivery-and-media.mmd) |
| 09 — End-to-end product capabilities | [SVG](09-end-to-end-capabilities.svg) | [PNG](09-end-to-end-capabilities.png) | [Excalidraw](09-end-to-end-capabilities.excalidraw) | [Mermaid](09-end-to-end-capabilities.mmd) |

Views 01/03/04/06/07 follow current code. Views 02/08 also carry explicitly labeled deployment-documentation evidence. View 05 is planned; view 09 maps the target product against limited current coverage. Code-reviewed does not mean production-certified or currently live-verified.

## Editing and regeneration

`build_diagrams.py` is the deterministic source for SVG, Excalidraw, and Mermaid. It uses Python, Pillow, and DejaVu Sans fonts at the paths declared near the top. This optional documentation tool is separate from the application's locked runtime dependencies. Change the generator before regenerating; hand-edited outputs will be overwritten. Update the reviewed source/date and audit when reviewing changed application behavior.

From the repository root, in an environment with Pillow and DejaVu Sans installed:

```sh
python docs/architecture/build_diagrams.py
```

Render SVGs to PNG with Inkscape installed:

```sh
for diagram in docs/architecture/*.svg; do
  inkscape "$diagram" --export-type=png --export-dpi=120 --export-filename="${diagram%.svg}.png"
done
```

PNG exports in this publication were rendered using Sharp at 120 dpi. Different renderers may produce small raster differences. SVG is the scalable primary image. Excalidraw scenes contain editable grouped shapes/text; native JSON structure was checked, but application import was not exercised. Mermaid preserves primary relationships and uses its own automatic layout, rather than the exact designed page.

`code-inventory.json` is a pinned audit snapshot: 16 API routes, eight tables, four agent definitions, test names and source-file hashes. Its hashes refer to the reviewed commit, including documents before their corrections, not the publication working tree. It is not an automatically maintained coverage claim.

## Publication validation

On 26 September 2026, after installing the repository's locked dependencies:

- `make verify`: **29 backend tests passed**, TypeScript check passed, Vite production build passed.
- `make demo-smoke`: **2/2 synthetic rehearsals passed**.
- All nine PNGs decoded/verified; SVG XML and Excalidraw JSON parsed; generator text-width/card-height assertions passed. The new capability view and refreshed rendered assets were visually reviewed.
- Relative documentation/asset links, pinned source hashes, route/schema inventory, and Git whitespace checks were checked before publication.

The test run emitted an existing Starlette/httpx deprecation warning; npm emitted an environment proxy-configuration warning. Neither failed the checks. No new live provider calls, Cloud Run/IAM/OAuth queries, deployment, browser sign-in or geolocation E2E checks were performed. Existing walkthrough media and historical release evidence were preserved. Passing the current suite does not close the audit findings; use the handoff's focused regressions.
