# Terraform — AKS (Quick Start)

## Prereqs
- Azure subscription + `az login`
- Terraform >= 1.5

## Apply
```bash
cd infra/terraform/aks
terraform init
terraform apply -auto-approve
# Extract kubeconfig:
terraform output -raw kube_config > kubeconfig
export KUBECONFIG=$(pwd)/kubeconfig
kubectl get nodes
```
