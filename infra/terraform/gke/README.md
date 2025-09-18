# Terraform — GKE (Quick Start)

## Prereqs
- Google Cloud project + credentials (`gcloud auth application-default login`)
- Terraform >= 1.5

## Apply
```bash
cd infra/terraform/gke
terraform init
terraform apply -auto-approve -var='project=<your-project-id>'
```
