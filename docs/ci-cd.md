# CI / CD

- **CI**: tests and image builds to GHCR
- **Release**: tag-based push to GHCR; Helm deploy via CD workflow
- **CD protections**: GitHub Environments (production), approvals, rollback steps
- **Terraform OIDC**: GKE/AKS workflows that `plan` on PRs & `apply` on main
