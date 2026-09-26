import pytest

from cafemesh import db


class Snapshot:
    def __init__(self, value, version):
        self._value = value
        self.update_time = version
        self.exists = value is not None

    def to_dict(self):
        return self._value


class FakeFirestore:
    def __init__(self):
        self.value = None
        self.version = 0

    def collection(self, _name):
        return self

    def document(self, _name):
        return self

    def get(self, transaction=None):
        return Snapshot(self.value, self.version)

    def set(self, value):
        self.value = value
        self.version += 1

    def transaction(self):
        return FakeTransaction(self)


class FakeTransaction:
    def __init__(self, remote):
        self.remote = remote

    def set(self, _ref, value):
        self.remote.set(value)


def test_firestore_snapshot_round_trips_and_rejects_lost_update(monkeypatch):
    from google.cloud import firestore

    remote = FakeFirestore()
    monkeypatch.setattr(firestore, "Client", lambda project: remote)
    monkeypatch.setattr(firestore, "transactional", lambda function: lambda txn: function(txn))
    monkeypatch.setattr(db.settings, "google_cloud_project", "test-project")
    monkeypatch.setattr(db.settings, "firestore_collection", "state")
    monkeypatch.setattr(db.settings, "firestore_document", "demo")
    monkeypatch.setattr(db.settings, "storage_backend", "firestore")

    initial = db.connect()
    initial.execute("CREATE TABLE notes (value TEXT NOT NULL)")
    initial.execute("INSERT INTO notes VALUES (?)", ("persisted",))
    initial.commit()
    initial.close()

    stale = db.connect()
    current = db.connect()
    assert current.execute("SELECT value FROM notes").fetchone()[0] == "persisted"
    current.execute("INSERT INTO notes VALUES (?)", ("latest",))
    current.commit()
    current.close()

    stale.execute("INSERT INTO notes VALUES (?)", ("stale",))
    with pytest.raises(RuntimeError, match="Concurrent Firestore update"):
        stale.commit()
    stale.close()

    reloaded = db.connect()
    assert [row[0] for row in reloaded.execute("SELECT value FROM notes")]
    reloaded.close()


def test_firestore_backend_requires_project(monkeypatch):
    monkeypatch.setattr(db.settings, "storage_backend", "firestore")
    monkeypatch.setattr(db.settings, "google_cloud_project", None)
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_PROJECT"):
        db.connect()
