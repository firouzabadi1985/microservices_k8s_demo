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
            print(f"Processed job {job_id} -> {res}")
        except Exception as e:
            r.hset(f"job:{job_id}", mapping={"status":"error", "error": str(e)})
            print(f"Error on job {job_id}: {e}")

if __name__ == "__main__":
    run()
