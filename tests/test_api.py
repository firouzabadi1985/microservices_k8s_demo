import pytest, time, httpx, subprocess, os, signal, sys

# Basic smoke test for API enqueue/result logic (without Docker/Redis).
# We simulate the FastAPI app using TestClient if available.
from fastapi.testclient import TestClient
from services.api.main import app, r

@pytest.fixture(autouse=True)
def flush_redis():
    r.flushdb()
    yield
    r.flushdb()

def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_enqueue_and_result_without_worker():
    client = TestClient(app)
    out = client.post("/enqueue", json={"value": 3}).json()
    job_id = out["job_id"]
    # No worker → status should be queued
    res = client.get(f"/result/{job_id}").json()
    assert res["status"] == "queued"
