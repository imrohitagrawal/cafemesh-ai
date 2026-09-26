import json
import re
import time
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from .data import CAFE, MENU, QUEUE, ZONES
from .db import connect, emit, now
from .config import settings

SAFETY_MAX_AGE_DAYS = 30
ALLOWED_TRANSITIONS = {"confirmed": {"preparing", "cancelled"}, "preparing": {"ready", "cancelled"}, "ready": {"completed"}}
MENU_QUERY_SYNONYMS = {
    "espresso": ("espresso",), "coffee": ("coffee", "espresso"), "americano": ("americano",),
    "latte": ("latte",), "cappuccino": ("cappuccino",), "chai": ("chai", "tea"),
    "tea": ("tea", "chai"), "matcha": ("matcha",), "mocha": ("mocha",),
    "frappe": ("frappe",), "cold brew": ("cold brew",),
}
UNSUPPORTED_MENU_TERMS = {"smoothie", "milkshake", "juice", "soda", "bubble tea", "kombucha"}


def menu_matches_query(item: dict, message: str) -> bool:
    """Small, transparent lexical retrieval over the structured menu catalog."""
    text = message.casefold()
    requested = [key for key in MENU_QUERY_SYNONYMS if re.search(rf"\b{re.escape(key)}\b", text)]
    if not requested:
        return True
    catalog = " ".join([item["name"], *item["ingredients"], *item["tags"]]).casefold()
    return any(any(re.search(rf"\b{re.escape(term)}\b", catalog) for term in MENU_QUERY_SYNONYMS[key]) for key in requested)


def prep_estimate(db, item_id: str, base: int):
    samples = [r[0] for r in db.execute("SELECT actual_minutes FROM prep_observations WHERE item_id=? AND source='measured' ORDER BY created_at DESC LIMIT 20", (item_id,))]
    if len(samples) < settings.prep_calibration_min_samples:
        return base, {"source": "synthetic baseline", "status": "demo", "samples": len(samples), "calibrated": False}
    estimate = max(1, min(settings.prep_calibration_max_minutes, round(sum(samples) / len(samples))))
    return estimate, {"source": "measured outcomes moving average", "status": "observed", "samples": len(samples), "calibrated": True}


def prefs(db=None):
    db = db or connect()
    row = db.execute("SELECT data FROM preferences WHERE customer_id='demo-customer'").fetchone()
    value = json.loads(row[0]) if row else {}
    db.close()
    return value


def recommend(request: dict):
    start = time.perf_counter()
    recommendation_id = str(uuid.uuid4())
    db = connect()
    profile = json.loads(db.execute("SELECT data FROM preferences WHERE customer_id='demo-customer'").fetchone()[0])
    out = []
    text = request.get("message", "").casefold()
    requested_menu_terms = [term for term in MENU_QUERY_SYNONYMS if re.search(rf"\b{re.escape(term)}\b", text)]
    unsupported_terms = [term for term in UNSUPPORTED_MENU_TERMS if re.search(rf"\b{re.escape(term)}\b", text)]
    requested_menu_terms += unsupported_terms
    unsupported_requested = bool(unsupported_terms)
    exact_title_terms = [term for term in requested_menu_terms if any(re.search(rf"\b{re.escape(term)}\b", item["name"].casefold()) for item in MENU)]
    matched_items = [] if unsupported_requested else [item for item in MENU if any(re.search(rf"\b{re.escape(term)}\b", item["name"].casefold()) for term in exact_title_terms)] if exact_title_terms else [item for item in MENU if menu_matches_query(item, text)]
    for item in matched_items:
        reasons = []
        if not item["available"]: reasons.append("out of stock")
        if item["price"] > request.get("budget", 350): reasons.append("over budget")
        if request.get("cold") is not None and item["cold"] is not request["cold"]: reasons.append("does not match requested temperature")
        if request.get("vegetarian") and not item["vegetarian"]: reasons.append("not vegetarian")
        allergy = set(request.get("allergies", []))
        if allergy.intersection(item["allergens"]): reasons.append("allergen conflict")
        unknown = item["cross_contact"] == "unknown" or any(datetime.fromisoformat(item["updated_at"]) < datetime.now(UTC) - timedelta(days=SAFETY_MAX_AGE_DAYS) for _ in [0])
        review = bool(allergy) and unknown
        if review: reasons.append("staff review required: cross-contact evidence unknown or stale")
        eligible = not reasons
        item_tags = set(item["tags"])
        score = profile.get("oat_milk", 0) if "oat_milk" in item_tags else 0
        score += profile.get("sweetness", 0) if "low_sweetness" in item_tags else 0
        score += profile.get("quiet_seating", 0) if "quiet" in item_tags else 0
        score -= profile.get("caramel", 0) if "caramel" in item_tags else 0
        prep, calibration = prep_estimate(db, item["id"], item["prep"])
        queue_wait=QUEUE.get("estimated_wait_minutes")
        max_time=request.get("max_total_minutes",40)
        predicted_total=prep+queue_wait if queue_wait is not None else None
        if max_time is not None and predicted_total is None: reasons.append("queue estimate unavailable")
        elif max_time is not None and predicted_total > max_time: reasons.append("exceeds visit time")
        out.append({"item": item, "eligible": not reasons, "staff_review_required": review, "reasons": reasons, "preference_score": score, "predicted_prep_minutes": prep, "predicted_total_minutes":predicted_total, "calibration": calibration, "evidence": [item["source_id"], "inventory-demo", "queue-demo"]})
    db.execute("INSERT INTO activity(agent,tool,evidence,latency_ms,status,summary,created_at) VALUES (?,?,?,?,?,?,?)", ("TasteSafetyAgent", "menu_and_safety_check", json.dumps([x for r in out for x in r["evidence"]]), int((time.perf_counter()-start)*1000), "demo", "Checked menu, constraints, availability, and safety evidence", now()))
    activity=[dict(row) for row in db.execute("SELECT agent,tool,evidence,latency_ms,status,summary,created_at FROM activity ORDER BY id DESC LIMIT 5")]
    db.commit(); db.close()
    out.sort(key=lambda x: (not x["eligible"], -x["preference_score"], x["item"]["price"]))
    db=connect(); emit(db,"recommendation",{"recommendation_id":recommendation_id,"candidate_ids":[x["item"]["id"] for x in out]})
    escalations=[x for x in out if x["staff_review_required"]]
    for item in escalations: emit(db,"safety_escalation",{"recommendation_id":recommendation_id,"item_id":item["item"]["id"],"evidence":item["evidence"]})
    db.commit();db.close()
    return {"recommendation_id":recommendation_id,"cafe": CAFE, "queue": QUEUE, "zones": ZONES, "candidates": out, "constraints": {key: request.get(key) for key in ("budget", "vegetarian", "cold", "allergies", "max_total_minutes")}, "message": "No menu items matched the requested drink terms in the current synthetic catalog." if requested_menu_terms and not matched_items else None, "activity": activity, "provider": {"name": "agents", "status": "demo", "detail": "Deterministic structured menu retrieval; no live Gemini call"}}


def preview(item_id: str, quantity: int = 1, modifications=None, constraints=None, recommendation_id=None):
    item = next((x for x in MENU if x["id"] == item_id), None)
    if not item: raise HTTPException(404, "Menu item not found")
    if not CAFE["open"]: raise HTTPException(409, "Café is closed")
    if not item["available"]: raise HTTPException(409, "Item unavailable")
    if item["price"] is None: raise HTTPException(409, "Price unavailable")
    if QUEUE.get("estimated_wait_minutes") is None: raise HTTPException(409,"Queue timing is unknown; cannot confirm a time-constrained visit")
    constraints = constraints or {"budget": 350, "vegetarian": True, "cold": True, "allergies": prefs().get("safety", [])}
    if constraints.get("budget") is not None and item["price"] * quantity > constraints["budget"]: raise HTTPException(409, "Order exceeds the stated budget")
    if constraints.get("vegetarian") and not item["vegetarian"]: raise HTTPException(409, "Item does not meet vegetarian constraint")
    if constraints.get("cold") is not None and item["cold"] is not constraints["cold"]: raise HTTPException(409, "Item does not meet the requested temperature")
    if constraints.get("max_total_minutes") is not None and item["prep"]+QUEUE["estimated_wait_minutes"]>constraints["max_total_minutes"]: raise HTTPException(409,"Item exceeds the visit time constraint")
    conflict = set(constraints.get("allergies", [])).intersection(item["allergens"])
    if conflict: raise HTTPException(409, "Known allergen conflict")
    review = item["cross_contact"] == "unknown" and bool(constraints.get("allergies"))
    if review: raise HTTPException(409, "Staff review required; synthetic confirmation cannot certify allergy safety")
    calibration_db=connect(); prep, calibration=prep_estimate(calibration_db,item_id,item["prep"]); calibration_db.close()
    if recommendation_id:
        check=connect(); known=check.execute("SELECT data FROM events WHERE kind='recommendation' AND json_extract(data,'$.recommendation_id')=?",(recommendation_id,)).fetchone();check.close()
        if not known or item_id not in json.loads(known[0]).get("candidate_ids",[]): raise HTTPException(409,"Recommendation context expired or item was not offered; request fresh options")
    proposal = {"proposal_id": str(uuid.uuid4()), "recommendation_id":recommendation_id, "item_id": item_id, "item_name": item["name"], "quantity": quantity, "unit_price": item["price"], "total": item["price"]*quantity, "modifications": modifications or [], "constraints": constraints, "predicted_minutes": prep + QUEUE["estimated_wait_minutes"], "calibration":calibration, "status": "demo", "safety_review": "eligible under current synthetic records"}
    db=connect();db.execute("INSERT INTO proposals(id,snapshot,created_at) VALUES (?,?,?)",(proposal["proposal_id"],json.dumps(proposal,sort_keys=True),now()));db.commit();db.close()
    return proposal


def confirm(payload: dict):
    db = connect()
    previous = db.execute("SELECT * FROM orders WHERE idempotency_key=?", (payload["idempotency_key"],)).fetchone()
    if previous:
        db.close()
        return dict(previous)
    proposal = payload["proposal"]
    stored=db.execute("SELECT snapshot,confirmed FROM proposals WHERE id=?",(proposal.get("proposal_id"),)).fetchone()
    if not stored or stored[1] or json.loads(stored[0]) != proposal:
        db.close();raise HTTPException(409,"Order preview was changed, already used, or expired; create a fresh preview")
    item = next((x for x in MENU if x["id"] == proposal["item_id"]), None)
    if not item or not item["available"] or not CAFE["open"]: db.close(); raise HTTPException(409, "Item, stock, or café status changed")
    if item["price"] != proposal["unit_price"]: db.close(); raise HTTPException(409, "Price changed; create a new preview")
    if QUEUE.get("estimated_wait_minutes") is None: db.close(); raise HTTPException(409,"Queue timing is unknown; request a new preview later")
    constraints = proposal.get("constraints", {})
    if item["price"] * proposal["quantity"] > constraints.get("budget", 10000): db.close(); raise HTTPException(409, "Order exceeds the stated budget")
    if constraints.get("vegetarian") and not item["vegetarian"] or constraints.get("cold") is not None and item["cold"] is not constraints["cold"]: db.close(); raise HTTPException(409, "Item no longer meets visit constraints")
    if constraints.get("max_total_minutes") is not None and item["prep"]+QUEUE["estimated_wait_minutes"]>constraints["max_total_minutes"]: db.close(); raise HTTPException(409,"Item exceeds the visit time constraint")
    if set(constraints.get("allergies", [])).intersection(item["allergens"]): db.close(); raise HTTPException(409, "Known allergen conflict")
    if item["cross_contact"] == "unknown" and constraints.get("allergies"): db.close(); raise HTTPException(409, "Staff review required")
    order_id = str(uuid.uuid4())
    db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (order_id, item["id"], item["name"], proposal["quantity"], item["price"], json.dumps(proposal.get("modifications", [])), "confirmed", proposal["predicted_minutes"], None, "demo-customer", now(), payload["idempotency_key"]))
    db.execute("UPDATE proposals SET confirmed=1 WHERE id=?",(proposal["proposal_id"],))
    emit(db, "order_confirmed", {"order_id": order_id, "amount": item["price"]*proposal["quantity"], "recommendation_id":proposal.get("recommendation_id")})
    db.commit(); row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone(); db.close()
    return dict(row)


def metrics(days: int = 30):
    db = connect()
    since = (datetime.now(UTC)-timedelta(days=days)).isoformat()
    orders = db.execute("SELECT * FROM orders WHERE created_at>=?", (since,)).fetchall()
    feedback = db.execute("SELECT COUNT(*) FROM feedback WHERE created_at>=?", (since,)).fetchone()[0]
    safety = db.execute("SELECT COUNT(*) FROM events WHERE kind='safety_escalation' AND created_at>=?", (since,)).fetchone()[0]
    stockouts = sum(not x["available"] for x in MENU)
    recommendation_count=db.execute("SELECT COUNT(*) FROM events WHERE kind='recommendation' AND created_at>=?",(since,)).fetchone()[0]
    conversions=db.execute("SELECT COUNT(DISTINCT json_extract(data,'$.recommendation_id')) FROM events WHERE kind='order_confirmed' AND created_at>=? AND json_extract(data,'$.recommendation_id') IS NOT NULL",(since,)).fetchone()[0]
    count = len(orders)
    result = {"window_days": days, "orders": count, "average_order_value": round(sum(r["unit_price"]*r["quantity"] for r in orders)/count, 2) if count else None, "average_wait_minutes": round(sum(r["predicted_minutes"] for r in orders)/count, 1) if count else None, "repeat_visits": max(0, count-1), "recommendation_conversion": round(min(conversions,recommendation_count)/recommendation_count*100,1) if recommendation_count else None, "stockouts": stockouts, "feedback_count": feedback, "safety_escalations": safety, "insufficient_data": count == 0, "definitions": {"average_wait_minutes": "mean predicted wait among confirmed orders", "repeat_visits": "orders after the first synthetic customer order", "recommendation_conversion": "unique recommendations followed by a confirmed linked order / recorded recommendations"}}
    db.close(); return result
