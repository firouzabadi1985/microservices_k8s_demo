import os, time
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

def process(x: float) -> float:
    # placeholder: heavy compute, ML inference, etc.
    return float(x) ** 2

def run():
    print("Worker running...")
    while True:
        item = r.blpop("jobs", timeout=5)
        if not item:
            continue
        _, payload = item
        try:
            job_id, val = payload.split(":", 1)
            res = process(float(val))
            r.hset(f"job:{job_id}", mapping={"status":"done", "result": str(res)})
            WORKER_JOBS_PROCESSED.inc(); print(f"Processed job {job_id} -> {res}")
        except Exception as e:
            r.hset(f"job:{job_id}", mapping={"status":"error", "error": str(e)})
            WORKER_JOBS_ERRORS.inc(); print(f"Error on job {job_id}: {e}")

if __name__ == "__main__":
    run()


# --- Prometheus metrics ---
from prometheus_client import Counter, start_http_server
WORKER_JOBS_PROCESSED = Counter("worker_jobs_processed_total", "Jobs processed successfully")
WORKER_JOBS_ERRORS = Counter("worker_jobs_errors_total", "Jobs processed with error")

# start metrics server
start_http_server(9000)
