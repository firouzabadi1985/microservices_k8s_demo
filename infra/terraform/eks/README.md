# Terraform — EKS (Quick Start)

> Minimal EKS cluster using default VPC/subnets (for demos). For production, create a dedicated VPC with private subnets and proper IAM.

## Prereqs
- Terraform >= 1.5
- AWS credentials configured (e.g., `aws configure`)

## Apply
```bash
cd infra/terraform/eks
terraform init
terraform apply -auto-approve
# Kubeconfig will be written to: infra/terraform/eks/kubeconfig
export KUBECONFIG=$(pwd)/kubeconfig
kubectl get nodes
```

## Next
- Install **nginx ingress**, **cert-manager**, **Prometheus Operator** (if using ServiceMonitors)
- Apply repo resources or use **Helm**/**Argo CD** from this project
