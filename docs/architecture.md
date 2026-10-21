# PipeFish mesh architecture

```
                 ┌────────────────────────────┐
   Buyer / Slack │  pipefish-labs (site)      │
   Moltgate lane │  openclaw-revenue-engine   │
                 └─────────────┬──────────────┘
                               │ A2A envelope
                 ┌─────────────▼──────────────┐
                 │  .github control plane     │
                 │  DAG · MCP · catalog       │
                 └───────┬───────────┬────────┘
           ┌─────────────┤           ├──────────────┐
           ▼             ▼           ▼              ▼
     five-agent-os  pipefish-recon  terraform-aws   infra-monitoring
     (workers)      (kernel/ACL)    (GitOps)        (ops intel)
```

## Contracts

- **Envelope** — `source`, `target`, `intent`, `payload`, `trace_id`, capability `tokens`.
- **DAG** — named nodes, explicit deps, skip-on-failure.
- **Catalog** — SKUs in `catalog/services.json`.
- **Memory** — hashed bag-of-tokens vectors in SQLite (no hosted embedding API required).
- **Secrets** — env → file → SSM. Values never enter git or logs.

## Why this is not twelve new microservices

Existing public repos already cover agents, revenue, recon, IaC, and observability.
This control plane is the shared contract and the private reusable CI/CD home.
New work should extend a live repo or this contract — not invent a 404.
