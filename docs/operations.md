# Operations (GitOps, DevOps, LLMOps, MLOps, FintechOps)

| Lane | What we run | Where |
| --- | --- | --- |
| **DevOps / GitOps** | Reusable Actions, Terraform, Ansible, Jenkins | this repo + `github-actions-templates` + `terraform-aws-modules` |
| **LLMOps** | Prompt/tool ACL, MCP servers, eval hooks | `pipefish-recon` POLICY.md, `five-agent-os`, MCP here |
| **MLOps** | Deterministic token vectors now; hosted models later | `pipefish_mesh.vectors` |
| **FintechOps** | Ledger, Stripe/Moltgate, webhook reconciliation | `openclaw-revenue-engine` |
| **RevOps** | SKUs, Slack deals, retainers | `catalog/services.json` |
| **Operational intelligence** | Grafana / Prometheus / Alertmanager | `infra-monitoring-dashboard` |

## Environments

`dev` → `preview` → `prod`. Same DAG, different secret prefixes
(`/pipefish/dev/`, `/pipefish/prod/`).

## Change control

Conventional commits. `feat/`, `fix/`, `docs/`, `chore/`, `security/` branches.
No direct secret changes on `main`.
