---
name: pipefish-control-plane
description: Operate the donny-devops / PipeFish Labs agentic mesh — A2A envelopes, DAG intake, MCP tools, and the live repo catalog. Use when routing work across repos, adding agents, or changing control-plane contracts.
---

# PipeFish Control Plane

This repository is the private control plane for [PipeFish Labs](https://pipefishlabs.io).

## When to use

- A request spans more than one `donny-devops` repo
- You need an A2A envelope, DAG, MCP tool, or SKU
- You are about to add a GitHub profile link (check `catalog/repos.yaml` first)

## Invariants

1. Do not advertise repositories that are not in `catalog/repos.yaml`.
2. Never commit secrets. Resolve them with `SecretBroker` (`env` → file → AWS SSM).
3. Capability tokens in envelopes are scopes (`commerce:write`), not API keys.
4. Revenue events go through `Ledger` and, in production, [openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine).
5. Public profile copy lives in `donny-devops/donny-devops`, not only here.

## Fast commands

```bash
python -m pipefish_mesh catalog
python -m pipefish_mesh intake "Need an OpenClaw security review" --sku mesh.audit.security
python -m pipefish_mesh mcp
```

## Repo map

| Need | Repo |
| --- | --- |
| Multi-agent runtime | `five-agent-os` |
| Paid inbox / Stripe / Moltgate | `openclaw-revenue-engine` |
| Threat intel + MCP ACL | `pipefish-recon` |
| Public site | `pipefish-labs` |
| AWS GitOps | `terraform-aws-modules` |
| Public reusable Actions | `github-actions-templates` |
| Observability | `infra-monitoring-dashboard` |
| PQC reference | `post-quantum-studio` |
