# Decisions and assumptions

- Product name, tagline, personas, Google AI core, safety boundaries, and MVP-first delivery are approved and settled.
- This workspace is the repository; it was initially empty except untracked `.agents/`, `.codex/`, and `skills-lock.json`. Preserve these user-supplied setup artifacts.
- No hackathon materials/rules were available, so no rule/judging claims are made.
- Demo café/menu/occupancy/customer records are synthetic; all actions are simulated.
- GCP project `dependable-keep-509808-j9` is configured for Vertex AI, Firestore, Places, Routes, Cloud Text-to-Speech, Cloud Build, and Cloud Run APIs. Live Places/Routes and Vertex/ADK calls, Firestore snapshot access, Cloud Run hosting, the custom domain, OAuth web client, and en-IN Despina narration were verified. Typed landmark discovery has been tested; browser geolocation remains opt-in and its permission flow is not fully verified.
- Google `agents-cli info` returned no usable output. Its current skill identifies normal Python scaffold patterns; CLI docs do not establish `.agents-cli-spec.md` as a special config filename.
- UI skill in workspace explicitly targets React Native, so its stack recipe is inapplicable to required React/Vite; accessibility/visual principles were used.
- External repositories named in the request were not copied into this empty project. Reuse was not needed for the coherent synthetic MVP.
- SQLite single-process demo is selected for speed and isolation; multi-user production storage/auth are future work.
