"""Run the two-pass synthetic judge journey against the real API app."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient
from cafemesh import db
from cafemesh.main import app


def run_journey(client: TestClient, run: int) -> None:
    client.post("/api/reset").raise_for_status()
    baseline_orders=client.get("/api/owner").json()["metrics"]["orders"]
    response=client.post("/api/recommend",json={"message":"I have 40 minutes. I’m vegetarian and severely allergic to peanuts. I want a cold drink under ₹350 and somewhere quiet to work.","budget":350,"vegetarian":True,"cold":True,"allergies":["peanuts"],"max_total_minutes":40})
    response.raise_for_status(); recommendations=response.json()
    match=next(x for x in recommendations["candidates"] if x["item"]["id"]=="iced-matcha")
    assert match["staff_review_required"] and not match["eligible"]
    quote=client.post("/api/preview",json={"item_id":"cold-brew","recommendation_id":recommendations["recommendation_id"],"budget":350,"vegetarian":True,"cold":True,"allergies":["peanuts"],"max_total_minutes":40})
    quote.raise_for_status()
    order=client.post("/api/confirm",json={"proposal":quote.json(),"idempotency_key":f"judge-demo-{run}-confirmation"})
    order.raise_for_status()
    assert any(x["id"]==order.json()["id"] for x in client.get("/api/ops").json()["orders"])
    decision=client.post("/api/ops/decision",json={"recommendation":"Review cross-contact records","decision":"accept"})
    decision.raise_for_status(); assert decision.json()["execution"]=="not performed"
    metrics=client.get("/api/owner").json()["metrics"]
    assert metrics["orders"]==baseline_orders+1 and metrics["recommendation_conversion"]==100 and metrics["safety_escalations"]>=1
    feedback=client.post("/api/feedback",json={"oat_milk":True,"low_sweetness":True,"no_caramel":True,"quiet_seating":True})
    feedback.raise_for_status(); assert feedback.json()["safety_unchanged"]
    repeat=client.post("/api/recommend",json={"allergies":["peanuts"],"budget":350}).json()
    favorite=next(x for x in repeat["candidates"] if x["item"]["id"]=="cold-brew")
    assert favorite["preference_score"]>0
    assert "peanuts" in client.get("/api/preferences").json()["safety"]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="cafemesh-demo-") as folder:
        db.settings.database=str(Path(folder)/"demo.sqlite")
        # Keep the isolated synthetic rehearsal independent from a developer's local OAuth setup.
        db.settings.google_client_id=None
        db.settings.require_google_auth=False
        with TestClient(app) as client:
            run_journey(client,1)
            run_journey(client,2)
    print("judge demo rehearsals: 2/2 passed (synthetic only)")


if __name__ == "__main__":
    main()
