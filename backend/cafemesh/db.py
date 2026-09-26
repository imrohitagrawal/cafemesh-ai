import json
import os
import sqlite3
import base64
from datetime import UTC, datetime
from datetime import timedelta
from pathlib import Path

from .config import settings


def now() -> str:
    return datetime.now(UTC).isoformat()


class FirestoreSnapshotConnection:
    """SQLite-compatible demo store persisted as one bounded Firestore snapshot.

    This keeps the hackathon repository's existing SQL service layer intact.
    Cloud Run is deliberately constrained to one instance/concurrent request;
    compare-and-set prevents silently overwriting a concurrent revision.
    This is durable demo storage, not a production multi-tenant database.
    """
    MAX_SNAPSHOT_BYTES = 700_000

    def __init__(self):
        from google.cloud import firestore

        self._firestore = firestore
        self._client = firestore.Client(project=settings.google_cloud_project)
        self._ref = self._client.collection(settings.firestore_collection).document(settings.firestore_document)
        snapshot = self._ref.get()
        self._update_time = snapshot.update_time if snapshot.exists else None
        self._db = sqlite3.connect(":memory:", check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        if snapshot.exists:
            raw = base64.b64decode(snapshot.to_dict()["sqlite_snapshot"], validate=True)
            if len(raw) > self.MAX_SNAPSHOT_BYTES:
                raise RuntimeError("Firestore demo snapshot exceeds the configured storage ceiling")
            self._db.deserialize(raw)

    def __getattr__(self, name):
        return getattr(self._db, name)

    def commit(self):
        self._db.commit()
        raw = self._db.serialize()
        if len(raw) > self.MAX_SNAPSHOT_BYTES:
            raise RuntimeError("Firestore demo snapshot exceeds the configured storage ceiling")
        encoded = base64.b64encode(raw).decode("ascii")
        expected_update_time = self._update_time
        transaction = self._client.transaction()

        @self._firestore.transactional
        def persist(txn):
            current = self._ref.get(transaction=txn)
            if expected_update_time is None:
                if current.exists:
                    raise RuntimeError("Concurrent Firestore initialization; retry the request")
            elif not current.exists or current.update_time != expected_update_time:
                raise RuntimeError("Concurrent Firestore update; retry the request")
            txn.set(self._ref, {"sqlite_snapshot": encoded, "updated_at": now(), "format_version": 1})

        persist(transaction)
        self._update_time = self._ref.get().update_time

    def close(self):
        self._db.close()


def connect() -> sqlite3.Connection | FirestoreSnapshotConnection:
    if settings.storage_backend == "firestore":
        if not settings.google_cloud_project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is required for Firestore storage")
        return FirestoreSnapshotConnection()
    path = Path(settings.database)
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize(reset: bool = False, seed_history: bool = False) -> None:
    db = connect()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS preferences (customer_id TEXT PRIMARY KEY, data TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, item_id TEXT NOT NULL, item_name TEXT NOT NULL, quantity INTEGER NOT NULL, unit_price REAL NOT NULL, modifications TEXT NOT NULL, status TEXT NOT NULL, predicted_minutes REAL NOT NULL, actual_minutes REAL, customer_id TEXT NOT NULL, created_at TEXT NOT NULL, idempotency_key TEXT UNIQUE NOT NULL);
    CREATE TABLE IF NOT EXISTS proposals (id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, confirmed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS prep_observations (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT NOT NULL, predicted_minutes REAL NOT NULL, actual_minutes REAL NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT, data TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, recommendation TEXT NOT NULL, decision TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, tool TEXT, evidence TEXT, latency_ms INTEGER, status TEXT, summary TEXT, created_at TEXT);
    """)
    if reset:
        for table in ("events", "orders", "proposals", "prep_observations", "feedback", "preferences", "decisions", "activity"):
            db.execute(f"DELETE FROM {table}")
    new_database=db.execute("SELECT COUNT(*) FROM preferences").fetchone()[0] == 0
    if reset or new_database:
        db.execute("INSERT OR REPLACE INTO preferences VALUES (?,?)", ("demo-customer", json.dumps({"oat_milk": 0, "sweetness": 0, "caramel": 0, "quiet_seating": 0, "explicit": [], "safety": ["peanuts"]})))
    if seed_history or (new_database and not reset):
        history=[("seeded-history-001","Iced Matcha Oat Latte","iced-matcha",290,7,14,9),("seeded-history-002","Vanilla Cold Brew","cold-brew",240,5,12,6),("seeded-history-003","Vanilla Cold Brew","cold-brew",240,5,13,4)]
        for oid,name,item_id,price,predicted,actual,days_ago in history:
            created=(datetime.now(UTC)-timedelta(days=days_ago)).isoformat()
            db.execute("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(oid,item_id,name,1,price,"[]","completed",predicted,actual,"demo-customer",created,f"seed-key-{oid}"))
            db.execute("INSERT INTO prep_observations(item_id,predicted_minutes,actual_minutes,source,created_at) VALUES (?,?,?,?,?)",(item_id,predicted,actual,"seeded_history",created))
            db.execute("INSERT INTO events(kind,data,created_at) VALUES (?,?,?)",("order_confirmed",json.dumps({"order_id":oid,"amount":price,"origin":"seeded_history"}),created))
        active_time=now()
        db.execute("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",("seeded-active-001","cold-brew","Vanilla Cold Brew",1,240,"[]","preparing",13,None,"demo-customer",active_time,"seed-active-001"))
        db.execute("INSERT INTO events(kind,data,created_at) VALUES (?,?,?)",("order_confirmed",json.dumps({"order_id":"seeded-active-001","amount":240,"origin":"seeded_history"}),active_time))
        for item_id,minutes in (("cold-brew",12),("cold-brew",13),("iced-matcha",14)):
            db.execute("INSERT INTO prep_observations(item_id,predicted_minutes,actual_minutes,source,created_at) VALUES (?,?,?,?,?)",(item_id,minutes-1,minutes,"seeded_history",now()))
        for data in ({"oat_milk":True,"low_sweetness":True},{"quiet_seating":True}):
            encoded=json.dumps(data); db.execute("INSERT INTO feedback(customer_id,data,created_at) VALUES (?,?,?)",("demo-customer",encoded,now())); db.execute("INSERT INTO events(kind,data,created_at) VALUES (?,?,?)",("feedback",encoded,now()))
    db.commit()
    db.close()


def emit(db: sqlite3.Connection, kind: str, data: dict) -> None:
    db.execute("INSERT INTO events(kind,data,created_at) VALUES (?,?,?)", (kind, json.dumps(data), now()))
