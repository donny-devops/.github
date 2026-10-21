---
name: gitops-deploy
description: Apply donny-devops GitOps, LLMOps, and CI/CD conventions. Use when adding Actions, Terraform, Ansible, Jenkins, Newman, or Cloudflare deploys.
---

# GitOps Deploy

## Call reusable workflows from this repo

```yaml
jobs:
  ci:
    uses: donny-devops/.github/.github/workflows/ci-lint-test.yml@main
    with:
      language: node
  security:
    uses: donny-devops/.github/.github/workflows/security-scan.yml@main
  iac:
    uses: donny-devops/.github/.github/workflows/iac-plan.yml@main
```

Public callers that cannot see this private repo should use
`donny-devops/github-actions-templates` instead.

## Tooling map

| Lane | Tool |
| --- | --- |
| GitOps | Terraform modules in `terraform-aws-modules` + `automation/terraform` |
| Config | Ansible in `automation/ansible` |
| HTTP tests | Postman/Newman in `automation/postman` |
| Classic CI | `Jenkinsfile` |
| Edge | `automation/cloudflare` |
| Agent automation | n8n / Make / Zapier recipes under `automation/` |

Do not apply Terraform or Ansible against real accounts from this repository’s CI.
