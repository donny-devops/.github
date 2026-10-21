# `.github` — PipeFish Control Plane

Private control plane for **[Adonis Jimenez](https://github.com/donny-devops)** / **[PipeFish Labs](https://pipefishlabs.io)**.

This repository is three things at once:

1. GitHub **community health files** inherited by other `donny-devops` repos
2. **Reusable GitHub Actions** (CI, CodeQL, container build, IaC, Newman, Ansible, Rust)
3. A working **agentic mesh**: A2A envelopes, an async DAG engine, MCP servers, a commerce ledger, hashed token memory, and a Go gateway

It does **not** replace the public products. Those stay in their own repos. This repo is the contract they share.

---

## Live products (do not link 404s)

| Repo | Role |
| :--- | :--- |
| [donny-devops](https://github.com/donny-devops/donny-devops) | Public GitHub profile |
| [pipefish-labs](https://github.com/donny-devops/pipefish-labs) | Site, enterprise workflow engineering |
| [five-agent-os](https://github.com/donny-devops/five-agent-os) | Autonomous multi-agent OS |
| [openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine) | Paid inbox, Stripe / Moltgate, ledger |
| [pipefish-recon](https://github.com/donny-devops/pipefish-recon) | Rust threat-intel kernel + MCP ACL |
| [post-quantum-studio](https://github.com/donny-devops/post-quantum-studio) | NIST FIPS 203/204/205 studio |
| [terraform-aws-modules](https://github.com/donny-devops/terraform-aws-modules) | AWS GitOps modules |
| [github-actions-templates](https://github.com/donny-devops/github-actions-templates) | Public reusable workflows |
| [infra-monitoring-dashboard](https://github.com/donny-devops/infra-monitoring-dashboard) | Grafana / Prometheus / Alertmanager |
| [docker-hacking-lab](https://github.com/donny-devops/docker-hacking-lab) | Isolated ethical-hacking lab |
| [qwen-core](https://github.com/donny-devops/qwen-core) | TypeScript focus client |
| [api-saas-decision-engine](https://github.com/donny-devops/api-saas-decision-engine) | Decision API (bootstrap) |

Canonical machine list: [`catalog/repos.yaml`](catalog/repos.yaml).

---

## Revenue

Spam is free. Agent attention is not.

| SKU | Price | Close path |
| :--- | :--- | :--- |
| `mesh.lane.ping` | $25 | OpenClaw + Moltgate paid inbox |
| `mesh.consult.discovery` | $2,500 | Workshop |
| `mesh.audit.security` | $4,500 | Agent / OpenClaw hardening |
| `mesh.retain.ops` | $8,000 / mo | GitOps + AgentOps retainer |
| `mesh.pqc.migration` | $12,000 | Post-quantum project |

Book locally:

```bash
python -m pip install -e ".[dev]"
python -m pipefish_mesh catalog
python -m pipefish_mesh intake "Need an OpenClaw security review" --sku mesh.audit.security
```

Collect money in production through
[openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine)
(Stripe via Moltgate). Card data never lands here.

Human close: [adonis-jimenez@outlook.com](mailto:adonis-jimenez@outlook.com) · [LinkedIn](https://www.linkedin.com/in/adonisjimenez/) · [pipefishlabs.io](https://pipefishlabs.io)

---

## Control-plane layout

```
src/pipefish_mesh/     Python package (protocol, DAG, ledger, secrets, MCP)
services/mesh-gateway/ Go HTTP macroservice (health, catalog, envelopes)
mcp/pipefish-mesh/     TypeScript MCP server
catalog/               SKUs + live repo map
.agents/skills/        Cursor / agent skills
automation/            n8n, Make, Zapier, Ansible, Terraform, Postman, Cloudflare
docs/                  Architecture, RevOps, secrets, GitOps, A2A
.github/workflows/     Reusable CI/CD + this repo's CI
```

### MCP

Python: `python -m pipefish_mesh mcp`  
TypeScript: `node --experimental-strip-types mcp/pipefish-mesh/src/index.ts`

Tools: `mesh.ping`, `catalog.list`, `ledger.record`, `dag.revenue_intake`, `memory.search`, `a2a.send`.

---

## Reusable CI/CD workflows

Call from any `donny-devops` repository that can see this private repo via
`uses: donny-devops/.github/.github/workflows/<workflow-name>.yml@main`.
Public repos that cannot should keep using
[`github-actions-templates`](https://github.com/donny-devops/github-actions-templates).

| Workflow | File | Description |
| :--- | :--- | :--- |
| **Control Plane CI** | [`control-plane-ci.yml`](.github/workflows/control-plane-ci.yml) | Tests *this* repo (pytest, Go, Node) |
| **CI Lint & Test** | [`ci-lint-test.yml`](.github/workflows/ci-lint-test.yml) | Node, Python, Go, Rust |
| **CodeQL Analysis** | [`codeql-analysis.yml`](.github/workflows/codeql-analysis.yml) | Multi-language SAST |
| **Security Scan** | [`security-scan.yml`](.github/workflows/security-scan.yml) | Gitleaks, TruffleHog, Dependency Review |
| **Docker Build & Push** | [`docker-build-push.yml`](.github/workflows/docker-build-push.yml) | Multi-arch GHCR, SBOM, Trivy |
| **IaC Plan** | [`iac-plan.yml`](.github/workflows/iac-plan.yml) | Terraform fmt + validate (no apply) |
| **Rust CI** | [`rust-ci.yml`](.github/workflows/rust-ci.yml) | fmt, clippy, test |
| **Newman** | [`newman.yml`](.github/workflows/newman.yml) | Postman collections |
| **Ansible Lint** | [`ansible-lint.yml`](.github/workflows/ansible-lint.yml) | Playbook lint |
| **Semantic Release** | [`release-please.yml`](.github/workflows/release-please.yml) | Conventional-commit releases |
| **Tag Release** | [`tag-release.yml`](.github/workflows/tag-release.yml) | Release on `v*` tags |

### Usage examples

#### 1. CodeQL SAST Analysis

```yaml
name: CodeQL
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
  schedule:
    - cron: "30 2 * * 1"
jobs:
  analyze:
    uses: donny-devops/.github/.github/workflows/codeql-analysis.yml@main
    with:
      languages: '["javascript-typescript", "python"]'
```

#### 2. Secrets & supply-chain scan

```yaml
name: Security Audit
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  security:
    uses: donny-devops/.github/.github/workflows/security-scan.yml@main
    with:
      enable-gitleaks: true
      enable-trufflehog: true
      enable-dependency-review: true
```

#### 3. Multi-arch Docker build & push (GHCR)

```yaml
name: Docker
on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request: { branches: [main] }
jobs:
  docker:
    uses: donny-devops/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: ${{ github.repository }}
      push: ${{ github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v') }}
      enable-trivy: true
```

#### 4. Unified CI lint & test

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  ci:
    uses: donny-devops/.github/.github/workflows/ci-lint-test.yml@main
    with:
      language: "node"
      node-version: "20"
      lint-command: "npm run lint"
      test-command: "npm test"
```

#### 5. Terraform validate

```yaml
jobs:
  iac:
    uses: donny-devops/.github/.github/workflows/iac-plan.yml@main
    with:
      working-directory: terraform
```

---

## Default community health files

GitHub applies these to `donny-devops` repositories that do not define their own:

- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Support](SUPPORT.md)
- [Funding](.github/FUNDING.yml)
- Issue templates: bug, feature, [paid engagement](.github/ISSUE_TEMPLATE/engagement.yml)
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)

---

## Docs & skills

- [Architecture](docs/architecture.md)
- [Revenue operations](docs/revenue-ops.md)
- [A2A protocol](docs/a2a-protocol.md)
- [Secrets](docs/secrets.md)
- [Operations](docs/operations.md)
- [Automation mesh](docs/automation-mesh.md)
- Skills under [`.agents/skills/`](.agents/skills/)
