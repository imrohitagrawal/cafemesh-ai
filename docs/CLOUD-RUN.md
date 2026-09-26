# Cloud Run deployment

CaféMesh is designed for one public Cloud Run service serving both the built React UI and FastAPI. Customer use is open. Operations, Owner, reset, and manager decisions require a Google ID token verified against the OAuth web client. Synthetic menu, occupancy, order, and staff actions remain isolated from real café systems.

## Current project setup

The authorized project is `dependable-keep-509808-j9` in `asia-south1`. Cloud Run, Cloud Build, Artifact Registry, Agent Platform (Vertex AI), Firestore, Places, Routes, Text-to-Speech, API Keys, and Secret Manager APIs are enabled. A runtime service account has `roles/aiplatform.user` and `roles/datastore.user`; the Maps secret is available to it through `roles/secretmanager.secretAccessor`. The Firestore native database and server-side API-restricted Places/Routes key were verified. Billing was already enabled; this project setup did not change billing.

OAuth branding and Google's required API Services User Data Policy agreement have been completed by the project owner. A Web application client is configured with the local origins and deployed service origin. Its client ID is configured in Cloud Run. The consent app remains External / Testing; the owner account is listed as a test user, so reviewer sign-in is limited to that tester until branding is fully completed and the app is published. No client secret is used by this GIS ID-token flow. Google may show an unverified-app interstitial until applicable verification is complete.

## Deployment

The public synthetic demo is served by Cloud Run service `cafemesh-ai` in `asia-south1`; the latest verified revision is `cafemesh-ai-00013-c85`. The public link is `https://cafemesh.stackclimb.com`, routed through the Cloudflare Worker `cafemesh-origin-proxy` to the canonical origin `https://cafemesh-ai-lbqubrb5jq-el.a.run.app`. `/api/health` and the custom-domain app have returned HTTP 200 on 26 September 2026. Revision `cafemesh-ai-00013-c85` serves 100% of traffic.

The owner OAuth client authorizes the Cloud Run origin and custom domain. A live Google Identity Services attempt from the canonical URL reached Google's account chooser after the origin was added, and the owner test account signed in successfully. OAuth is still External / Testing, so only its listed tester can access protected views.

The verified source deployment uses the existing runtime identity, environment variables, and secret reference. A source update can be deployed with `gcloud run deploy cafemesh-ai --source . --region asia-south1 --project dependable-keep-509808-j9`. The initial service configuration used these settings:

```sh
PROJECT_ID=dependable-keep-509808-j9
REGION=asia-south1
SERVICE_ACCOUNT="cafemesh-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
GOOGLE_CLIENT_ID='your-web-client-id.apps.googleusercontent.com'
gcloud config set project "$PROJECT_ID"
gcloud run deploy cafemesh-ai \
  --source . \
  --region "$REGION" \
  --service-account "$SERVICE_ACCOUNT" \
  --allow-unauthenticated \
  --max 1 \
  --concurrency 1 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60 \
  --set-env-vars "CAFEMESH_DEMO_MODE=true,CAFEMESH_STORAGE_BACKEND=firestore,CAFEMESH_REQUIRE_GOOGLE_AUTH=true,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global,GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},CAFEMESH_MODEL=gemini-2.5-flash" \
  --set-secrets "GOOGLE_MAPS_API_KEY=cafemesh-google-maps-key:latest"
```

Public Cloud Run ingress allows anyone with the URL to use customer discovery and synthetic ordering. `CAFEMESH_REQUIRE_GOOGLE_AUTH=true` protects reviewer endpoints with Google ID-token verification. Cloud Run authentication is public at the service layer; application authentication protects operations/owner views and decisions. The runtime service account uses attached identity/ADC; no service-account key is uploaded. The Cloud Build identity has the Cloud Run source builder role and writer access scoped to the source-deploy repository; runtime access is granted separately. Source deployment and API calls use the project's existing billing. `--max 1` and `--concurrency 1` keep the Firestore snapshot approach within hackathon scope; it is not a production multi-tenant store.

Earlier checks on revision `cafemesh-ai-00006-s9n` verified the API, videos, authentication gate, live Places/Routes, and a live Vertex/ADK call. Revision `cafemesh-ai-00008-kfs` verified typed-landmark discovery at the custom hostname; Revisions 11 and 12 include current search, retrieval, error handling, licensing attribution, and walkthrough updates. The latest public checks verified HTTP 200 health/config/homepage and both current walkthrough assets, a 401 response from Ops without an ID token, and 100% traffic on revision 12. Results and walking route were previously returned near Indiranagar Metro Station, Bengaluru. Admin access remains limited to listed OAuth testers while the consent app is in Testing.

## Limits

SQLite remains the local default. Firestore uses one snapshot document for synthetic demo state (700 KB application payload ceiling); use normalized collections/transactions for a real multi-user deployment. The browser geolocation path is opt-in and coordinates are not persisted; a permission-grant E2E check remains unverified. Menu, allergen, stock, order, and manager records remain synthetic. Interactive voice chat, Model Armor, and production-scale identity/data architecture are not included. Cloud Run direct domain mapping is unavailable in `asia-south1`; the active custom hostname uses Cloudflare DNS and a small Worker proxy to the existing Cloud Run service.
