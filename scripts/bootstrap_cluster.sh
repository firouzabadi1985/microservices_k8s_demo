#!/usr/bin/env bash
set -euo pipefail

# One-click bootstrap for a fresh cluster:
# - nginx ingress
# - cert-manager + ClusterIssuers
# - Prometheus Operator (kube-prometheus-stack light)
# - Grafana/Loki/Promtail addons (from this repo)
# - Argo CD + ApplicationSet (dev/prod)
# - Helm install of microdemo (optional)

NS_PROM="monitoring"

echo "👉 Ensuring namespaces..."
kubectl get ns microdemo >/dev/null 2>&1 || kubectl create ns microdemo
kubectl get ns ${NS_PROM} >/dev/null 2>&1 || kubectl create ns ${NS_PROM}

echo "👉 Installing nginx ingress (ingress-nginx)"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller

echo "👉 Installing cert-manager"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl -n cert-manager rollout status deployment/cert-manager-webhook

echo "👉 Applying ClusterIssuers from repo"
kubectl apply -k k8s/addons/cert-manager

echo "👉 Installing Prometheus Operator (kube-prometheus-stack CRDs)"
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

echo "👉 Deploying Grafana (with provisioning)"
kubectl apply -k k8s/addons/grafana

echo "👉 Deploying Loki + Promtail"
kubectl apply -k k8s/addons/loki

echo "👉 Installing Argo CD"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd rollout status deployment/argocd-server

echo "👉 Applying Argo CD ApplicationSet (dev/prod)"
kubectl apply -f k8s/addons/argocd/applicationset-envs.yaml

echo "✅ Bootstrap complete."
echo "Next:"
echo " - Add DNS A record to your Ingress LB for dev/prod hosts"
echo " - For Grafana dev ingress: add /etc/hosts entry: 127.0.0.1 grafana.microdemo.local (if using kind/minikube)"
