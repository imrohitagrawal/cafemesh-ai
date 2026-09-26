# Demo media guide

Use the product walkthrough for a first review, the engineering walkthrough for technical context, and the short overview for a quick introduction. All café business records shown are synthetic. The main README embeds existing sanitized captures so readers can understand the application without playing a video.

## Videos

| Asset | Duration | Format | Content and evidence boundary |
| --- | --- | --- | --- |
| [Product walkthrough](../frontend/public/videos/cafemesh-product-walkthrough.mp4) · [hosted playback](https://cafemesh.stackclimb.com/videos/cafemesh-product-walkthrough.mp4) | 6:55 | 1280×720, H.264/AAC | Narrated point-in-time Customer, Operations, Owner and Vision screenshots |
| [Engineering walkthrough](../frontend/public/videos/cafemesh-engineering-walkthrough.mp4) · [hosted playback](https://cafemesh.stackclimb.com/videos/cafemesh-engineering-walkthrough.mp4) | 9:41 | 1280×720, H.264/AAC | Screenshot-based explanation of architecture, policy, agents, evaluation and roadmap |
| [Two-minute overview](cafemesh-two-minute-demo.mp4) | 2:00 | 1280×720, H.264/AAC | Narrated slides; not a continuous app recording |

Durations and codecs were inspected with `ffprobe` on 26 September 2026; display times are rounded to the nearest second. A video is a historical presentation asset, not a current API/provider health check. Written code-reviewed architecture and audit findings take precedence over stronger or older narration claims. Do not represent planned features as available from a video alone.

## Screenshot gallery and provenance

The [capture manifest](provided-app-screenshots/README.md) explains the supplied originals, sanitization, and scene mapping. Originals with personal/account information remain outside this repository. The following existing product scenes are reused without alteration in the README:

| Scene | README use | Caption boundary |
| --- | --- | --- |
| [01](provided-app-screenshots/product/scene-01.png) | Clickable product walkthrough preview | Customer request and directory discovery; Maps results are not participating-café guarantees |
| [03](provided-app-screenshots/product/scene-03.png) | Customer gallery | Menu candidates and review labels from the captured state |
| [05](provided-app-screenshots/product/scene-05.png) | Operations gallery | Synthetic queue/signals and historical provider activity, including visible errors |
| [07](provided-app-screenshots/product/scene-07.png) | Owner gallery | Demo values and brief; KPI/grounding limits are in the audit |
| [00](provided-app-screenshots/product/scene-00.png) | Vision gallery | Intended product journey including planned scope |

Captures are dated 26 September 2026. GitHub links each preview to its original PNG for full-size inspection. The README uses a linked thumbnail and ordinary MP4 links; it does not depend on autoplay or custom video-player HTML.

## Narration and reproducibility

| Product | Engineering |
| --- | --- |
| [Narration text](cafemesh-product-walkthrough.txt) | [Narration text](cafemesh-engineering-walkthrough.txt) |
| [Saved audio](../frontend/public/audio/cafemesh-product-walkthrough.mp3) | [Saved audio](../frontend/public/audio/cafemesh-engineering-walkthrough.mp3) |
| [Timing manifest](cafemesh-product-walkthrough-timing.json) | [Timing manifest](cafemesh-engineering-walkthrough-timing.json) |

Media scripts: [voiceover generation](../scripts/generate_voiceover.py), [supplied screenshot preparation](../scripts/prepare_supplied_screenshots.py), [engineering slide rendering](../scripts/render_engineering_slides.py), and [video assembly](../scripts/render_demo_video.py). Review their configuration and external-input requirements before running them. TTS generation contacts a configured Google service; screenshot preparation requires the owner-supplied source files. Saved playback does not require runtime voice generation.

When refreshing media, review current code/claims first, use synthetic records, sanitize account details, retain [attribution](video-attribution.txt), verify audio/video synchronization and update durations/captions. Publish a new date rather than presenting an older capture as a live verification result.
