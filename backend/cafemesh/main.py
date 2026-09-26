import json
import uuid
import asyncio
import time
import re
import logging
import httpx
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from . import agents
from .config import settings
from .data import CAFE, MENU, QUEUE, ZONES
from .db import connect, emit, initialize, now
from .observability import build_observability
from .service import ALLOWED_TRANSITIONS, confirm, metrics, prefs, preview, recommend

@asynccontextmanager
async def lifespan(_app):
    initialize()
    yield

app = FastAPI(title="CaféMesh AI", version="0.1.0", lifespan=lifespan)
logger = logging.getLogger("cafemesh.ai")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])
MAPS_LAST_STATUS = {"places": "unavailable", "routes": "unavailable"}
ALLERGY_SAFETY_LANGUAGE = re.compile(r"\b(?:safe|safely|allergy[- ]safe|allergen[- ]free|peanut[- ]free|nut[- ]free)\b", re.IGNORECASE)


def guard_model_summary(summary: str, allergies: list[str]) -> tuple[str | None, str]:
    """Withhold free-form narrative when exact allergy constraints are present."""
    if allergies:
        return None, "withheld_allergy_context"
    if ALLERGY_SAFETY_LANGUAGE.search(summary):
        return None, "withheld_safety_language"
    return summary, "live"


class Request(BaseModel):
    message: str = Field(default="café menu", max_length=1200)
    budget: int = Field(default=350, gt=0, le=10000)
    vegetarian: bool = False
    cold: bool | None = None
    allergies: list[str] = []
    max_total_minutes: int | None = Field(default=None, gt=0, le=1440)

    @model_validator(mode="after")
    def require_search_text(self):
        if not self.message.strip():
            raise ValueError("Describe the drink or visit you want to search for.")
        return self

class PreviewRequest(BaseModel):
    item_id: str
    quantity: int = Field(default=1, ge=1, le=10)
    modifications: list[str] = []
    budget: int = Field(default=350, gt=0, le=10000)
    vegetarian: bool = False
    cold: bool | None = None
    allergies: list[str] = []
    max_total_minutes: int | None = Field(default=None, gt=0, le=1440)
    recommendation_id: str | None = None

class ConfirmRequest(BaseModel):
    proposal: dict
    idempotency_key: str = Field(min_length=8, max_length=100)

class GoogleCredentialRequest(BaseModel):
    credential: str = Field(min_length=20, max_length=10000)

class PlaceSearchRequest(BaseModel):
    query: str = Field(default="cafés in Indiranagar, Bengaluru", min_length=3, max_length=200)
    origin_address: str | None = Field(default=None, min_length=3, max_length=200)
    origin_latitude: float | None = Field(default=None, ge=-90, le=90)
    origin_longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_origin(self):
        if (self.origin_latitude is None) != (self.origin_longitude is None):
            raise ValueError("origin_latitude and origin_longitude must be provided together")
        if self.origin_latitude is not None and self.origin_address:
            raise ValueError("Choose either a current-location coordinate or a typed origin")
        return self

def verify_google_id_token(token: str) -> dict:
    if not settings.google_client_id:
        raise HTTPException(503, "Google Sign-In is not configured")
    try:
        from google.auth.transport.requests import Request as GoogleRequest
        from google.oauth2 import id_token
        claims = id_token.verify_oauth2_token(token, GoogleRequest(), settings.google_client_id)
    except Exception as exc:
        raise HTTPException(401, "Google Sign-In credential is invalid or expired") from exc
    if claims.get("email_verified") not in (True, "true") or not claims.get("sub"):
        raise HTTPException(401, "A verified Google account is required")
    return {"sub": claims["sub"], "email": claims.get("email", ""), "name": claims.get("name", "")}

def require_demo_admin(authorization: str | None = Header(default=None)):
    # Local synthetic development can stay open; public deployments can fail closed.
    if not settings.google_client_id:
        if settings.require_google_auth:
            raise HTTPException(503, "Google Sign-In is required but no OAuth client is configured")
        return {"sub": "local-synthetic-demo"}
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in with Google to open the demo reviewer workspace")
    return verify_google_id_token(authorization[7:])

@app.get("/api/health")
def health(): return {"status": "ok", "application": "CaféMesh AI", "dataset": "synthetic"}

@app.get("/api/config")
def public_config():
    return {"google_client_id": settings.google_client_id, "require_google_auth": settings.require_google_auth, "maps_configured": bool(settings.google_maps_api_key), "storage": "Firestore" if settings.storage_backend == "firestore" else "local SQLite", "dataset": "synthetic"}

@app.post("/api/auth/session")
def google_session(request: GoogleCredentialRequest):
    user = verify_google_id_token(request.credential)
    return {"authenticated": True, "user": user, "scope": "synthetic-demo-reviewer"}

@app.post("/api/places/search")
async def places_search(request: PlaceSearchRequest):
    global MAPS_LAST_STATUS
    if not settings.google_maps_api_key:
        MAPS_LAST_STATUS = {"places": "unavailable", "routes": "unavailable"}
        raise HTTPException(503, "Live Google Places is unavailable: no server-side Maps key is configured. No synthetic café was substituted.")
    headers = {"X-Goog-Api-Key": settings.google_maps_api_key, "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.currentOpeningHours.openNow,places.googleMapsUri"}
    query = request.query
    search_body = {"textQuery": query, "includedType": "cafe", "pageSize": 5}
    if request.origin_latitude is not None:
        search_body["locationBias"] = {"circle": {"center": {"latitude": request.origin_latitude, "longitude": request.origin_longitude}, "radius": settings.google_places_bias_radius_meters}}
    elif request.origin_address:
        search_body["textQuery"] = f"{query} near {request.origin_address}"
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        try:
            response = await client.post("https://places.googleapis.com/v1/places:searchText", headers=headers, json=search_body)
            response.raise_for_status()
            results = response.json().get("places", [])
            MAPS_LAST_STATUS["places"] = "live"
        except httpx.HTTPError as exc:
            MAPS_LAST_STATUS["places"] = "error"
            raise HTTPException(502, "Live Google Places request failed; no synthetic result was substituted") from exc
        places = [{"id": p.get("id"), "name": (p.get("displayName") or {}).get("text", "Name unavailable"), "address": p.get("formattedAddress", "Address unavailable"), "rating": p.get("rating"), "rating_count": p.get("userRatingCount"), "open_now": (p.get("currentOpeningHours") or {}).get("openNow"), "location": p.get("location"), "maps_url": p.get("googleMapsUri") if (p.get("googleMapsUri") or "").startswith(("https://www.google.com/maps", "https://maps.google.com/")) else None} for p in results]
        if not places:
            MAPS_LAST_STATUS["routes"] = "unavailable"
            return {"provider": {"status": "live", "name": "Google Places API"}, "query": request.query, "places": [], "route": None, "origin": request.origin_address or ("Your current location" if request.origin_latitude is not None else settings.google_maps_demo_origin), "origin_status": "user_permission" if request.origin_latitude is not None else "typed" if request.origin_address else "demo_reference_point", "message": "Google Places returned no cafés for this query."}
        route = None
        destination = places[0].get("location") or {}
        if destination.get("latitude") is not None and destination.get("longitude") is not None:
            try:
                origin = {"location": {"latLng": {"latitude": request.origin_latitude, "longitude": request.origin_longitude}}} if request.origin_latitude is not None else {"address": request.origin_address or settings.google_maps_demo_origin}
                route_response = await client.post("https://routes.googleapis.com/directions/v2:computeRoutes", headers={"X-Goog-Api-Key": settings.google_maps_api_key, "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"}, json={"origin": origin, "destination": {"location": {"latLng": {"latitude": destination["latitude"], "longitude": destination["longitude"]}}}, "travelMode": "WALK"})
                route_response.raise_for_status()
                first_route = (route_response.json().get("routes") or [None])[0]
                if first_route:
                    seconds = int((first_route.get("duration", "0s")).removesuffix("s"))
                    route = {"distance_meters": first_route.get("distanceMeters"), "duration_seconds": seconds, "duration_minutes": max(1, round(seconds / 60)), "mode": "WALK", "status": "live"}
                MAPS_LAST_STATUS["routes"] = "live"
            except httpx.HTTPError:
                MAPS_LAST_STATUS["routes"] = "error"
                route = {"status": "error", "message": "Live route estimate unavailable; no synthetic ETA was substituted."}
    origin_label = request.origin_address or ("Your current location" if request.origin_latitude is not None else settings.google_maps_demo_origin)
    origin_status = "user_permission" if request.origin_latitude is not None else "typed" if request.origin_address else "demo_reference_point"
    return {"provider": {"status": "live", "name": "Google Places API"}, "query": request.query, "places": places, "route": route, "origin": origin_label, "origin_status": origin_status}

@app.get("/api/status")
def status():
    live_configured = bool(settings.google_api_key) or settings.google_genai_use_vertexai
    db=connect(); last=db.execute("SELECT status FROM activity WHERE agent='ConciergeAgent' AND tool='adk_run_async' ORDER BY id DESC LIMIT 1").fetchone();db.close()
    gemini_state=(last[0] if last else "unavailable") if live_configured else "demo"
    auth_mode = "Vertex AI with ADC" if settings.google_genai_use_vertexai else "Google API key"
    detail="Successful ADK call recorded" if gemini_state=="live" else "Most recent configured ADK call failed" if gemini_state=="error" else f"{auth_mode} configured but no live call has succeeded" if live_configured else "Deterministic demo path; no Gemini credentials configured"
    maps_detail = "A live request succeeded in this process" if MAPS_LAST_STATUS["places"] == "live" else "Maps key configured but not live-verified yet" if settings.google_maps_api_key else "No server-side Maps key configured"
    storage_status = "live" if settings.storage_backend == "firestore" else "demo"
    voice_asset = Path(__file__).resolve().parents[2] / "frontend" / "public" / "audio" / "cafemesh-product-walkthrough.mp3"
    if not voice_asset.is_file():
        voice_asset = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "audio" / "cafemesh-product-walkthrough.mp3"
    voice_status = "generated" if voice_asset.is_file() else "unavailable"
    voice_detail = "Google Cloud Gemini-TTS en-IN Despina narration generated; playback uses a saved MP3 and makes no runtime synthesis call" if voice_status == "generated" else "No narration asset is bundled"
    return {"providers": {"gemini": {"status": gemini_state, "detail": detail}, "places": {"status": MAPS_LAST_STATUS["places"], "detail": maps_detail}, "routes": {"status": MAPS_LAST_STATUS["routes"], "detail": maps_detail}, "firestore": {"status": storage_status, "detail": "Single-document snapshot store for synthetic demo state" if storage_status == "live" else "Local SQLite"}, "text_to_speech": {"status": voice_status, "detail": voice_detail}, "model_armor": {"status": "unavailable"}}, "agents": "available" if agents.ADK_AVAILABLE else "unavailable", "demo_mode": not live_configured}

async def run_live_adk(user_text: str, facts: dict):
    if not agents.ADK_AVAILABLE or agents.root_agent is None:
        raise HTTPException(503, "Gemini credential is configured but the ADK runtime is unavailable")
    try:
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        async def invoke(agent, app_name: str, prompt: str):
            runner = InMemoryRunner(app_name=app_name, agent=agent)
            session = await runner.session_service.create_session(app_name=app_name, user_id="demo-customer")
            texts=[]; tool_outcomes={}
            async for event in runner.run_async(user_id="demo-customer", session_id=session.id, new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)])):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        call=getattr(part,"function_call",None)
                        response=getattr(part,"function_response",None)
                        if call is not None and call.name: tool_outcomes[call.name]="called"
                        if response is not None and response.name: tool_outcomes[response.name]="completed"
                        if part.text and event.is_final_response(): texts.append(part.text)
            return " ".join(texts)[-2400:],tool_outcomes

        async def collect():
            taste, visit = await asyncio.gather(
                invoke(agents.agents["TasteSafetyAgent"], "cafemesh-taste", "Call menu_facts. Summarize one available cold vegetarian drink and identify any unknown peanut cross-contact. Never guarantee safety."),
                invoke(agents.agents["VisitOrderAgent"], "cafemesh-visit", "Call visit_facts. Summarize the supplied queue timing and quiet seating facts."),
            )
            context = json.dumps({"request": user_text[:1200], "authoritative_candidate_facts": facts["candidates"], "queue": facts["queue"], "taste_safety_tool_result": taste[0], "visit_order_tool_result": visit[0], "rule": "These records are synthetic. Preserve explicit constraints; unknown evidence requires review. Never place an order."})
            answer, concierge_tools = await invoke(agents.root_agent, "cafemesh-concierge", context)
            tool_outcomes = {**taste[1], **visit[1], **concierge_tools}
            return answer, tool_outcomes
        started=time.perf_counter()
        answer,tool_outcomes=await asyncio.wait_for(collect(), timeout=settings.request_timeout_seconds)
        elapsed=int((time.perf_counter()-started)*1000)
        evidence=json.dumps([x["item"]["source_id"] for x in facts["candidates"]])
        db=connect(); db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)",("ConciergeAgent","adk_run_async",evidence,elapsed,"live","Gemini ADK response completed" if answer else "Gemini ADK returned no text",now()))
        agent_by_tool={"menu_facts":"TasteSafetyAgent","visit_facts":"VisitOrderAgent","owner_facts":"OpsOwnerAgent"}
        for tool_name,outcome in tool_outcomes.items(): db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)",(agent_by_tool.get(tool_name,"ConciergeAgent"),tool_name,evidence,elapsed,"live" if outcome=="completed" else "error",f"ADK tool {outcome}",now()))
        db.commit(); db.close()
        if not answer: raise RuntimeError("ADK returned no assistant response")
        return answer, {"name":"Google ADK + Gemini","status":"live","latency_ms":elapsed}
    except asyncio.TimeoutError as exc:
        record_adk_error("Gemini ADK request timed out",int(settings.request_timeout_seconds*1000))
        raise HTTPException(504, "Gemini ADK request timed out; no demo fallback was used") from exc
    except HTTPException:
        raise
    except Exception as exc:
        error_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        safe_code = str(error_code)[:32] if isinstance(error_code, (str, int)) else "unknown"
        logger.warning("ADK provider call failed type=%s code=%s", type(exc).__name__, safe_code)
        record_adk_error(f"Gemini ADK request failed ({type(exc).__name__}; code={safe_code})",0)
        raise HTTPException(502, "Gemini ADK request failed; no demo fallback was used") from exc

def record_adk_error(summary: str, latency_ms: int):
    db=connect();db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)",("ConciergeAgent","adk_run_async","[]",latency_ms,"error",summary,now()));db.commit();db.close()

@app.post("/api/recommend")
async def recommendation(request: Request):
    facts=recommend(request.model_dump())
    # Empty retrieval is a no-answer. Do not let a language model fill the gap
    # with a plausible but unlisted menu item.
    if not facts["candidates"]:
        facts["provider"]={"name":"structured retrieval","status":"demo","detail":"No catalog candidate matched; generation was skipped"}
        return facts
    if settings.google_api_key or settings.google_genai_use_vertexai:
        summary, provider=await run_live_adk(request.message, facts)
        summary, summary_status = guard_model_summary(summary, request.allergies)
        facts["assistant_summary"]=summary
        facts["assistant_summary_status"]=summary_status
        if summary_status.startswith("withheld_"):
            notice="Gemini's free-form summary was withheld because this request includes an allergy. Review the structured candidates and evidence; deterministic checks control eligibility, and no item is guaranteed allergy-safe."
            facts["assistant_summary_notice"]=notice
            db=connect(); db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)",("ConciergeAgent","summary_safety_guard",json.dumps([x["item"]["source_id"] for x in facts["candidates"]]),0,"review",notice,now())); db.commit(); db.close()
            facts["activity"].insert(0,{"agent":"ConciergeAgent","tool":"summary_safety_guard","summary":"Model summary withheld: allergy-safety wording requires review","latency_ms":0,"status":"review"})
        facts["provider"]=provider
        db=connect(); facts["activity"]=[dict(row) for row in db.execute("SELECT agent,tool,evidence,latency_ms,status,summary,created_at FROM activity ORDER BY id DESC LIMIT 5")]; db.close()
    return facts

@app.post("/api/preview")
def order_preview(request: PreviewRequest): return preview(request.item_id, request.quantity, request.modifications, {"budget":request.budget,"vegetarian":request.vegetarian,"cold":request.cold,"allergies":request.allergies,"max_total_minutes":request.max_total_minutes},request.recommendation_id)

@app.post("/api/confirm")
def order_confirm(request: ConfirmRequest): return confirm(request.model_dump())

@app.get("/api/ops")
def operations(_user: dict = Depends(require_demo_admin)):
    db = connect(); orders = [dict(x) for x in db.execute("SELECT * FROM orders WHERE status IN ('confirmed','preparing','ready') ORDER BY created_at DESC")]; decisions = [dict(x) for x in db.execute("SELECT * FROM decisions ORDER BY created_at DESC")]; activity = [dict(x) for x in db.execute("SELECT * FROM activity ORDER BY id DESC LIMIT 10")]; observability = build_observability(db); db.close()
    low_stock=[x for x in MENU if x["stock_units"] <= x["low_stock_threshold"]]
    alerts=[{"level":"warning","text":f"Low stock: {x['name']} has {x['stock_units']} synthetic units remaining"} for x in low_stock]
    alerts += [{"level": "review", "text": "Peanut cross-contact evidence is unknown for the iced matcha; staff review required"}, {"level": "info", "text": "Community table currently has no seats (synthetic occupancy)"}]
    return {"orders": orders, "queue": QUEUE, "zones": ZONES, "alerts": alerts, "recommendation": "Review cross-contact records with staff before serving allergy-sensitive customers.", "decisions": decisions, "activity": activity, "observability": observability, "providers": status()["providers"]}

@app.post("/api/ops/decision")
def decision(payload: dict, _user: dict = Depends(require_demo_admin)):
    if payload.get("decision") not in {"accept", "reject"}: raise HTTPException(422, "Manager decision must be accept or reject")
    db=connect(); db.execute("INSERT INTO decisions(recommendation,decision,created_at) VALUES (?,?,?)", (payload.get("recommendation", "Review safety evidence"), payload["decision"], now())); emit(db, "manager_decision", {"decision": payload["decision"], "execution": "not performed"}); db.commit(); db.close(); return {"recorded": True, "execution": "not performed", "status": "demo"}

@app.post("/api/ops/order/{order_id}/transition")
def transition(order_id: str, payload: dict, _user: dict = Depends(require_demo_admin)):
    state=payload.get("status"); db=connect(); row=db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row: db.close(); raise HTTPException(404, "Order not found")
    if state not in ALLOWED_TRANSITIONS.get(row["status"], set()): db.close(); raise HTTPException(409, "Illegal order-state transition")
    actual=payload.get("actual_minutes")
    if state == "ready" and actual is None: db.close(); raise HTTPException(422, "Measured total time is required when marking an order ready")
    if actual is not None and not 1 <= actual <= settings.prep_calibration_max_minutes: db.close(); raise HTTPException(422, "Measured total time outside configured range")
    db.execute("UPDATE orders SET status=?,actual_minutes=COALESCE(?,actual_minutes) WHERE id=?", (state,actual,order_id))
    if state=="ready":
        db.execute("INSERT INTO prep_observations(item_id,predicted_minutes,actual_minutes,source,created_at) VALUES (?,?,?,?,?)",(row["item_id"],row["predicted_minutes"],actual,"measured",now()))
    emit(db,"order_transition",{"order_id":order_id,"status":state,"actual_minutes":actual}); db.commit(); db.close(); return {"status":state,"actual_minutes":actual,"execution":"demo"}

@app.get("/api/owner")
async def owner(days: int = 30, _user: dict = Depends(require_demo_admin)):
    if not 1 <= days <= 365: raise HTTPException(422,"Window must be 1–365 days")
    values=metrics(days)
    db=connect(); rows=[dict(r) for r in db.execute("SELECT kind,data,created_at FROM events ORDER BY id DESC LIMIT 20")]; db.close()
    brief={"status":"demo","text":"Shared synthetic order history is small. Use customer feedback and measured preparation outcomes to improve service; no causal conclusion is supported."}
    if settings.google_api_key or settings.google_genai_use_vertexai:
        try:
            from google.adk.runners import InMemoryRunner
            from google.genai import types
            agent=agents.agents["OpsOwnerAgent"]
            runner=InMemoryRunner(app_name="cafemesh-owner",agent=agent)
            session=await runner.session_service.create_session(app_name="cafemesh-owner",user_id="demo-owner")
            prompt=json.dumps({"window_days":days,"provided_metrics":values,"instruction":"Call owner_facts with this exact window_days, then provide a concise grounded brief using only that tool result. State no causal conclusions and do not invent figures or actions."})
            async def collect():
                text=[]; tools_seen={}
                async for event in runner.run_async(user_id="demo-owner",session_id=session.id,new_message=types.Content(role="user",parts=[types.Part.from_text(text=prompt)])):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            call=getattr(part,"function_call",None); result=getattr(part,"function_response",None)
                            if call is not None and call.name: tools_seen[call.name]="called"
                            if result is not None and result.name: tools_seen[result.name]="completed"
                            if part.text and event.is_final_response(): text.append(part.text)
                return " ".join(text)[-1600:],tools_seen
            started=time.perf_counter()
            summary,tools_seen=await asyncio.wait_for(collect(),timeout=settings.request_timeout_seconds)
            elapsed=int((time.perf_counter()-started)*1000)
            if tools_seen.get("owner_facts")!="completed" or not summary:
                raise HTTPException(502,"Gemini owner brief did not complete its required metrics tool call")
            evidence=json.dumps([f"owner_metrics_{days}_days"])
            db=connect(); db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)",("OpsOwnerAgent","owner_facts",evidence,elapsed,"live","Grounded owner metrics tool completed",now())); db.commit(); db.close()
            brief={"status":"live","text":summary}
        except asyncio.TimeoutError as exc:
            raise HTTPException(504,"Gemini owner brief timed out; deterministic substitution was not used") from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(502,"Gemini owner brief failed; deterministic substitution was not used") from exc
    return {"metrics":values,"brief":brief,"events":rows}

@app.get("/api/preferences")
def get_preferences(): return prefs()

@app.post("/api/feedback")
def feedback(payload: dict):
    data={k:bool(payload.get(k)) for k in ("oat_milk","low_sweetness","no_caramel","quiet_seating")}
    db=connect(); old=json.loads(db.execute("SELECT data FROM preferences WHERE customer_id='demo-customer'").fetchone()[0]);
    for source,target in (("oat_milk","oat_milk"),("low_sweetness","sweetness"),("no_caramel","caramel"),("quiet_seating","quiet_seating")):
        if data[source]: old[target]=max(-3,min(3,old.get(target,0)+1))
    old["explicit"] = list(set(old.get("explicit",[])) | {k for k,v in data.items() if v})
    db.execute("UPDATE preferences SET data=? WHERE customer_id='demo-customer'",(json.dumps(old),)); db.execute("INSERT INTO feedback(customer_id,data,created_at) VALUES (?,?,?)",("demo-customer",json.dumps(data),now())); emit(db,"feedback",data); db.commit(); db.close()
    return {"preferences":old,"updated":data,"safety_unchanged":True}

@app.post("/api/reset")
def reset(_user: dict = Depends(require_demo_admin)): initialize(reset=True,seed_history=True); return {"reset":True,"dataset":"synthetic seeded baseline"}

@app.get("/api/vision")
def vision(): return {"implemented":["live Google Places and walking Routes","Firestore-backed synthetic state","Google Sign-In integration (OAuth client required)","Google Cloud Text-to-Speech sample with Despina","grounded menu constraints","simulated confirmation","operations queue","shared owner metrics","bounded preference learning","manager decision audit"],"simulated":["menu and allergen records","occupancy","staff review","manager actions","orders"],"planned":["Model Armor","BigQuery","group orders","payments and POS","multilingual voice interaction","meet-halfway discovery","GPS arrival synchronization"],"loops":["customer preferences","prep-time calibration","reviewed AI evaluation"],"architecture":"hackathon"}

STATIC = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if STATIC.exists():
    app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")
    if (STATIC / "audio").exists():
        app.mount("/audio", StaticFiles(directory=STATIC / "audio"), name="audio")
    @app.get("/{path:path}")
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404,"API route not found")
        file=STATIC/path
        return FileResponse(file if file.exists() and file.is_file() else STATIC/"index.html")
