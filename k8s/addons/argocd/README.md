# Argo CD (GitOps) Addon

## Install Argo CD
Use the official install manifest:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
# Wait for pods to be running, then expose Argo CD UI as needed (port-forward/ingress).
```

## Register the Microdemo Application
Edit `application-microdemo.yaml` to point `repoURL` and `targetRevision` to your Git repo/branch.
Then:
```bash
kubectl apply -f k8s/addons/argocd/application-microdemo.yaml
```
Argo CD will sync `helm/microdemo` automatically (automated prune/self-heal enabled).
