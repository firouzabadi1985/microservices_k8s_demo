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


---

## Helm Chart (with Ingress + TLS)

```bash
# Package or install directly from the local chart
helm upgrade --install microdemo ./helm/microdemo   --namespace microdemo --create-namespace   --set image.registry=ghcr.io/$GHCR_USERNAME/microdemo   --set image.api.tag=v1.0.0   --set image.worker.tag=v1.0.0   --set ingress.enabled=true   --set ingress.host=api.microdemo.example.com   --set ingress.tls.enabled=true   --set ingress.tls.secretName=microdemo-tls   --set ingress.annotations.cert-manager\.io/cluster-issuer=letsencrypt
```

> Requires an Ingress controller (e.g., nginx) and **cert-manager** installed in the cluster.

## Push Images to GHCR (GitHub Container Registry)

1. In your GitHub repo **Settings → Secrets and variables → Actions**, add:
   - `GHCR_USERNAME` = your GitHub username or org
   - `GHCR_PAT` = a personal access token with `write:packages`, `read:packages`

2. Trigger the **Release & Push to GHCR** workflow:
   - **Manually**: Actions → *Release & Push to GHCR* → *Run workflow* (provide `version`, e.g., `v1.0.0`)
   - **Or by tag**: `git tag v1.0.0 && git push --tags`

3. Update `values.yaml` or the Helm command `--set image.registry=ghcr.io/<your>/microdemo` and tags.



---

## Dev Ingress (nginx) & Hosts Entry

Apply the dev overlay (includes an Ingress):
```bash
kubectl apply -k k8s/overlays/dev
# If using kind/minikube, add to /etc/hosts:
# 127.0.0.1 dev.microdemo.local
kubectl -n microdemo port-forward svc/api 8000:8000  # alternative if no ingress
```

Open: http://dev.microdemo.local/health

## Prometheus Metrics & ServiceMonitor

- API exposes **/metrics** (Prometheus text format).  
- `k8s/base/servicemonitor-api.yaml` targets the `api` Service (port name `http`).  
- Requires **Prometheus Operator** (label selector `release=prometheus` by default). Adjust labels to match your installation.

## Private Registry Pull (GHCR) — ImagePullSecrets

Create a Docker config JSON and secret:
```bash
echo -n '<YOUR_GHCR_PAT>' | base64 -w0  # create token if needed
# Or generate ~/.docker/config.json by `docker login ghcr.io` and base64 it fully.
kubectl -n microdemo create secret docker-registry ghcr-pull   --docker-server=ghcr.io   --docker-username=<your-gh-username-or-org>   --docker-password=<your-ghcr-pat>   --docker-email=<you@example.com>
```

The overlays include a patch `patch-imagepullsecrets.yaml` that adds:
```yaml
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ghcr-pull
```


---

## Grafana Dashboard

A ConfigMap `grafana-dashboard-microdemo` is provided under `k8s/base/grafana-dashboard-configmap.yaml` with a sample panel for `api_requests_total`.  
If Grafana sidecar (e.g., in kube-prometheus-stack) watches for `grafana_dashboard=1` labels, it will automatically load this dashboard.

## Worker Metrics & ServiceMonitor

- Worker service exposes port `8080` with `/metrics`.  
- `k8s/base/servicemonitor-worker.yaml` registers it for scraping.

## Prod Ingress (with TLS)

Prod overlay includes `k8s/overlays/prod/ingress.yaml` for host `api.microdemo.example.com`.  
Requires nginx ingress + cert-manager with a ClusterIssuer `letsencrypt`.  
Certificate stored in secret `microdemo-tls`.


---

## Grafana Dashboards

Dashboard JSONs are under `grafana/dashboards/`:
- `api.json` shows **API requests rate** by endpoint from `api_requests_total`
- `worker.json` shows **processed/error jobs rates** from `worker_jobs_processed_total` and `worker_jobs_errors_total`

Import them into Grafana (Dashboards → Import → Upload JSON).

## Worker Metrics & ServiceMonitor

- Worker exposes metrics on **:9000/metrics**.
- `k8s/base/service-worker.yaml` + `servicemonitor-worker.yaml` are provided (Prometheus Operator required).

## Prod Ingress (TLS)

The prod overlay includes an Ingress at `api.microdemo.example.com` with TLS via **cert-manager**:
```bash
kubectl apply -k k8s/overlays/prod
# Ensure cert-manager + nginx ingress are installed and DNS points to your LB IP.
```


---

## Addons

### Grafana (auto-provision dashboards + Prometheus datasource)
```bash
kubectl apply -k k8s/addons/grafana
# Open via ingress:
# http://grafana.microdemo.local (default admin/admin)
```

*Provisioning:* mounts `dashboards/` & `provisioning/` ConfigMaps into Grafana so dashboards auto-load and a Prometheus datasource points to `prometheus-operated:9090` (adjust as needed).

### Loki + Promtail (logs demo)
```bash
kubectl apply -k k8s/addons/loki
# Add Loki datasource in Grafana: URL http://loki.microdemo.svc.cluster.local:3100
# Explore logs from /var/log/containers
```

## Helm — prod values example
```bash
helm upgrade --install microdemo ./helm/microdemo -f helm/microdemo/values-prod.example.yaml
```


---

## Cert-Manager Issuer

Example ACME ClusterIssuer is in `k8s/addons/cert-manager/clusterissuer-letsencrypt.yaml`.  
Edit the email and apply:
```bash
kubectl apply -f k8s/addons/cert-manager/clusterissuer-letsencrypt.yaml
```

## Grafana Admin Secret

Default admin credentials come from `grafana-admin` Secret (user=admin, password=supersecret).  
Change before deploying to production.

## Loki Datasource (auto-provisioned)

Grafana provisioning now includes a Loki datasource pointing to `loki.microdemo.svc.cluster.local:3100`.

## GitHub Actions — CD with Helm

Workflow `.github/workflows/cd-helm.yml`:
- Requires secrets:
  - `KUBECONFIG_CONTENT` (base64 kubeconfig or plaintext)
  - `GHCR_USERNAME`
- On tag push (e.g. `v1.0.1`) or manual dispatch, runs `helm upgrade --install` using chart in repo.



---

## cert-manager Issuers (Let's Encrypt)

Apply the example **ClusterIssuers** (staging + prod):
```bash
kubectl apply -k k8s/addons/cert-manager
# Then set your Ingress annotation:
#   cert-manager.io/cluster-issuer: letsencrypt
```

## Grafana admin + Loki datasource (auto-provision)

- `k8s/addons/grafana/secret-admin.yaml` sets admin credentials (default admin/admin — change before prod).
- `grafana-provisioning` CM now includes a **Loki datasource** pointing to `loki.microdemo.svc.cluster.local:3100`.
- Dashboards auto-load from ConfigMap.

## GitHub Actions — Continuous Deployment

A CD workflow deploys the Helm chart **on new tags** (e.g., `v1.0.1`):
1. In repo **Settings → Secrets and variables → Actions**, add:
   - `KUBECONFIG_B64` → base64 of your kubeconfig
   - `GHCR_USERNAME` → your GH username/org (matches pushed images)
   - `PROD_HOST` → your production domain (e.g., `api.your-real-domain.com`)

2. Tag & push:
```bash
git tag v1.0.1 && git push --tags
```
CI (release) builds images to GHCR, then CD deploys Helm to your cluster with the new tag.



---

## GitHub Environments & Protected Deploys

This repo's CD uses a **`production` environment**. In GitHub:
1. Go to **Settings → Environments → New environment → `production`**.
2. Add **required reviewers** (optional) and **secrets** used by workflows:
   - `KUBECONFIG_B64` (base64 of kubeconfig)
   - `GHCR_USERNAME` (must match pushed images)
   - `PROD_HOST` (your prod domain, e.g., `api.your-real-domain.com`)
3. Deploys will pause for approval (if reviewers configured), and the Environment page will show deployment history & URL.

## Rollbacks

- **Automatic rollback on failure**: the CD workflow attempts to roll back to the last deployed revision if a deploy fails.
- **Manual rollback**: trigger the **“Manual Helm Rollback”** workflow:
  - Input the revision from `helm history microdemo -n microdemo` (e.g., `5`).

List revisions:
```bash
helm history microdemo -n microdemo
```


---

## GitOps with Argo CD

Install Argo CD and apply the Application manifest pointing to this repo:
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f k8s/addons/argocd/application-microdemo.yaml
```
Edit `repoURL`, `targetRevision`, images/tags, and domain in `application-microdemo.yaml`.

## Terraform (EKS)
See `infra/terraform/eks` for a quick-start EKS cluster suitable for demos.


## Multi-env with Argo CD ApplicationSet
`k8s/addons/argocd/applicationset-microdemo.yaml` generates dev/prod Applications with different domains & tags.

## Terraform — Multi-cloud
- `infra/terraform/eks` — AWS EKS
- `infra/terraform/gke` — GCP GKE
- `infra/terraform/aks` — Azure AKS

## Auto-bump Helm values on tag
The workflow `.github/workflows/bump-helm.yaml` updates Helm `values.yaml` tags and opens a PR when you push a new git tag.


---

## Multi-env GitOps (Argo CD ApplicationSet)
Apply `k8s/addons/argocd/applicationset-envs.yaml` after installing Argo CD to manage **dev/prod** from a single template.
Edit the generator list to add more environments or change domains/tags.

## Terraform — GKE & AKS
- **infra/terraform/gke** — basic Google Kubernetes Engine cluster
- **infra/terraform/aks** — basic Azure Kubernetes Service cluster

## CI utility — Bump Helm values & open PR on tag
On every release tag (e.g., `v1.2.3`), the workflow updates `helm/microdemo/values-prod.example.yaml` image tags, pushes a branch, and opens a PR.


---

## Helmfile CI
Use **Helmfile Deploy** workflow to sync `dev` or `prod` using a kubeconfig provided as `KUBECONFIG_B64` secret.

## Terraform EKS OIDC
Add repo secrets:
- `AWS_TF_ROLE_ARN` — IAM Role ARN trusted for GitHub OIDC
- `AWS_REGION` — e.g., `eu-central-1`

## One-click Bootstrap
```bash
scripts/bootstrap_cluster.sh
```
Installs **ingress**, **cert-manager** (+ClusterIssuers), **Prometheus Operator CRDs**, **Grafana + Loki/Promtail**, and **Argo CD**; then applies **ApplicationSet** (dev/prod).
