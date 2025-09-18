# Getting Started

## Local (Docker Compose)
```bash
docker compose up --build
```

## Kubernetes (Kustomize - dev)
```bash
kubectl apply -k k8s/overlays/dev
```

## Helm (prod-like)
```bash
helm upgrade --install microdemo ./helm/microdemo -f helm/microdemo/values-prod.example.yaml
```

## Helmfile (multi-env)
```bash
cd helmfile
helmfile sync
```
