from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, uuid
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="Microdemo API")

class EnqueuePayload(BaseModel):
    value: float

@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enqueue")
def enqueue(payload: EnqueuePayload):
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", mapping={"status":"queued"})
    r.rpush("jobs", f"{job_id}:{payload.value}")
    return {"job_id": job_id}

@app.get("/result/{job_id}")
def result(job_id: str):
    key = f"job:{job_id}"
    if not r.exists(key):
        raise HTTPException(status_code=404, detail="job not found")
    data = r.hgetall(key)
    return {"job_id": job_id, **data}


# --- Prometheus metrics ---
from fastapi import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUESTS_TOTAL = Counter("api_requests_total", "Total API requests", ["endpoint"])

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health_instrumented():
    REQUESTS_TOTAL.labels(endpoint="/health").inc()
    try:
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enqueue")
def enqueue_instrumented(payload: EnqueuePayload):
    REQUESTS_TOTAL.labels(endpoint="/enqueue").inc()
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", mapping={"status":"queued"})
    r.rpush("jobs", f"{job_id}:{payload.value}")
    return {"job_id": job_id}

@app.get("/result/{job_id}")
def result_instrumented(job_id: str):
    REQUESTS_TOTAL.labels(endpoint="/result").inc()
    key = f"job:{job_id}"
    if not r.exists(key):
        raise HTTPException(status_code=404, detail="job not found")
    data = r.hgetall(key)
    return {"job_id": job_id, **data}
