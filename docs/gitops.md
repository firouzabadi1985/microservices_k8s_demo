# GitOps

Install Argo CD, then apply:
```bash
kubectl apply -f k8s/addons/argocd/applicationset-envs.yaml
```

- Dev and Prod Apps are generated from one template.
- Enable auto-sync (prune + self-heal) for continuous reconciliation.
