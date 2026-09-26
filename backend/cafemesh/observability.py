"""Derived operational and agent-activity indicators for the reviewer dashboard."""
import json
from collections import Counter
from statistics import median

from .db import now


def build_observability(db) -> dict:
    """Summarize persisted records since the last synthetic demo reset.

    These are internal application events, not Cloud Monitoring/SLO metrics.
    Their scope and denominators are returned with the values for UI clarity.
    """
    activities = [dict(row) for row in db.execute(
        "SELECT agent,tool,evidence,latency_ms,status,summary,created_at FROM activity ORDER BY id DESC"
    )]
    events = [dict(row) for row in db.execute("SELECT kind FROM events")]
    decisions = [dict(row) for row in db.execute("SELECT decision FROM decisions")]
    observations = [dict(row) for row in db.execute(
        "SELECT predicted_minutes,actual_minutes,source FROM prep_observations"
    )]
    feedback_count = db.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    preference_row = db.execute("SELECT data FROM preferences WHERE customer_id='demo-customer'").fetchone()

    status_counts = Counter(row.get("status") or "unknown" for row in activities)
    provider_rows = [row for row in activities if row.get("status") in {"live", "error"}]
    provider_successes = sum(row["status"] == "live" for row in provider_rows)
    latencies = [int(row["latency_ms"]) for row in provider_rows if row.get("latency_ms") and int(row["latency_ms"]) > 0]
    events_by_kind = Counter(row["kind"] for row in events)
    measured = [row for row in observations if row["source"] == "measured"]
    seeded = [row for row in observations if row["source"] != "measured"]
    absolute_errors = [abs(float(row["actual_minutes"]) - float(row["predicted_minutes"])) for row in measured]
    candidates = [
        {key: row[key] for key in ("agent", "tool", "summary", "status", "created_at")}
        for row in activities if row.get("status") in {"error", "review"}
    ][:8]

    return {
        "updated_at": now(),
        "scope": "Persisted synthetic-demo events since the last reset; not a production SLO window.",
        "activity": {
            "rows": len(activities),
            "live_rows": status_counts["live"],
            "demo_rows": status_counts["demo"],
            "error_rows": status_counts["error"],
            "review_rows": status_counts["review"],
            "live_or_error_rows": len(provider_rows),
            "success_pct": round(provider_successes / len(provider_rows) * 100, 1) if provider_rows else None,
            "median_latency_ms": round(median(latencies)) if latencies else None,
            "recent": activities[:8],
            "review_candidates": candidates,
        },
        "events": {
            "recommendations": events_by_kind["recommendation"],
            "confirmed_orders": events_by_kind["order_confirmed"],
            "safety_escalations": events_by_kind["safety_escalation"],
            "feedback_updates": events_by_kind["feedback"],
            "manager_decisions": len(decisions),
            "manager_accepts": sum(row["decision"] == "accept" for row in decisions),
            "manager_rejects": sum(row["decision"] == "reject" for row in decisions),
        },
        "learning": {
            "feedback_records": feedback_count,
            "explicit_taste_preferences": len(json.loads(preference_row[0]).get("explicit", [])) if preference_row else 0,
            "measured_prep_samples": len(measured),
            "seeded_prep_samples": len(seeded),
            "mean_absolute_prep_error_minutes": round(sum(absolute_errors) / len(absolute_errors), 1) if absolute_errors else None,
        },
    }
