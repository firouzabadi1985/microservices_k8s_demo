# Microservices on Kubernetes — FastAPI + Worker + Redis

A production-style demo showing **two microservices** (FastAPI + Worker) backed by **Redis**, with:
- Docker images for each service
- Local run via **docker-compose**
- **Kubernetes manifests** with **Kustomize** overlays (dev/prod)
- **Horizontal Pod Autoscaler** for the API
- **GitHub Actions** CI (tests + Docker build)
- Basic **pytest** tests

> Goal: a clean portfolio-ready repo to demonstrate microservices, containers, and GitOps-friendly K8s manifests.

---

## Architecture

```
[ client ] → [ FastAPI ] → enqueue job → [ Redis ]
                                 ↑                  
                            fetch result ← [ Worker ] (processes jobs, writes results to Redis)
```

- **/enqueue**: submits a number to process → returns a `job_id`
- **/result/{job_id}**: fetches the processed result
- **/health**: liveness/readiness check

Processing = simple function (e.g., `f(x) = x^2`) — easy to verify in tests.

---

## Quick Start (Local with Docker Compose)

```bash
# Build & run
docker compose up --build

# In another terminal
curl -X POST localhost:8000/enqueue -H "Content-Type: application/json" -d '{"value": 7}'
# → {"job_id":"..."} 

curl localhost:8000/result/<job_id>
# → {"job_id":"...", "status":"done", "result":49}
```

---

## Kubernetes (Kustomize)

- **Base** manifests in `k8s/base/`
- **Overlays** in `k8s/overlays/dev` and `k8s/overlays/prod`

```bash
# Apply dev
kubectl apply -k k8s/overlays/dev

# Check
kubectl -n microdemo get pods,svc,hpa

# Port-forward API (if no Ingress):
kubectl -n microdemo port-forward svc/api 8000:8000
```

> Adjust image names/tags as needed (default uses local build tags).

---

## Makefile

```bash
make test          # run pytest
make compose-up    # docker compose up --build
make compose-down  # docker compose down -v
make k8s-apply     # kubectl apply -k k8s/overlays/dev
```

---

## CI (GitHub Actions)

- Runs `pytest`
- Builds both Docker images (without pushing; you can add registry credentials later)

---

## Repo Structure

```
microservices_k8s_demo/
  ├── services/
  │   ├── api/           # FastAPI service
  │   └── worker/        # Worker service
  ├── k8s/
  │   ├── base/          # base manifests
  │   └── overlays/
  │       ├── dev/
  │       └── prod/
  ├── tests/
  ├── .github/workflows/ci.yml
  ├── docker-compose.yml
  ├── Makefile
  ├── requirements.txt
  └── README.md
```

---

## Notes

- For a real deployment add: logging, metrics, tracing, ingress w/ TLS, image registry + pull secrets, and a Helm chart (optional).
