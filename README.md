# `.github` — Organization Governance & Reusable CI/CD

Central repository for **donny-devops** default community health files, issue/PR templates, and centralized reusable GitHub Actions workflows.

---

## 🚀 Reusable CI/CD Workflows

All workflows are located in [`.github/workflows`](.github/workflows) and can be invoked from any `donny-devops` repository via `uses: donny-devops/.github/.github/workflows/<workflow-name>.yml@main`.

| Workflow | File | Description | Triggers / Usage |
| :--- | :--- | :--- | :--- |
| **CodeQL Analysis** | [`codeql-analysis.yml`](.github/workflows/codeql-analysis.yml) | Multi-language SAST static code analysis & vulnerability alerts | `workflow_call` |
| **Security Scan** | [`security-scan.yml`](.github/workflows/security-scan.yml) | Gitleaks commit history scan, TruffleHog credential scan & Dependency Review | `workflow_call` |
| **Docker Build & Push** | [`docker-build-push.yml`](.github/workflows/docker-build-push.yml) | Multi-arch Docker builds (`amd64`/`arm64`), GHCR publish, SBOM attestation & Trivy scan | `workflow_call` |
| **CI Lint & Test** | [`ci-lint-test.yml`](.github/workflows/ci-lint-test.yml) | Standardized linting, testing, and building for Node.js, Python, and Go | `workflow_call` |
| **Semantic Release** | [`release-please.yml`](.github/workflows/release-please.yml) | Automated semver versioning, changelog generation, and releases | `workflow_call` |
| **Tag Release** | [`tag-release.yml`](.github/workflows/tag-release.yml) | Creates GitHub releases when semantic version tags (`v*`) are pushed | `push` (tags: `v*`) |
| **Community Health** | [`community-health.yml`](.github/workflows/community-health.yml) | Asserts the recommended GitHub community-standards file set is present | `workflow_call`, `push`, `pull_request` |

---

### 📖 Usage Examples

#### 1. CodeQL SAST Analysis
Add `.github/workflows/codeql.yml` to your repository:
```yaml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '30 2 * * 1' # Weekly on Monday

jobs:
  analyze:
    uses: donny-devops/.github/.github/workflows/codeql-analysis.yml@main
    with:
      languages: '["javascript-typescript", "python"]'
```

#### 2. Secrets & Supply Chain Security Scan
Add `.github/workflows/security.yml` to your repository:
```yaml
name: Security Audit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    uses: donny-devops/.github/.github/workflows/security-scan.yml@main
    with:
      enable-gitleaks: true
      enable-trufflehog: true
      enable-dependency-review: true
```

#### 3. Multi-Arch Docker Build & Push (GHCR)
Add `.github/workflows/docker.yml` to your repository:
```yaml
name: Docker

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  docker:
    uses: donny-devops/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: ${{ github.repository }}
      push: ${{ github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v') }}
      enable-trivy: true
```

#### 4. Unified CI Lint & Test
Add `.github/workflows/ci.yml` to your repository:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    uses: donny-devops/.github/.github/workflows/ci-lint-test.yml@main
    with:
      language: 'node'
      node-version: '20'
      lint-command: 'npm run lint'
      test-command: 'npm test'
```

#### 5. Automated Release Please
Add `.github/workflows/release.yml` to your repository:
```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    uses: donny-devops/.github/.github/workflows/release-please.yml@main
```

---

## 📋 Default Community Health Files

GitHub applies these files to every **public** `donny-devops` repository that does not define its own copy. This repository itself must remain public — GitHub does not inherit defaults from a private `.github` repo.

This file set is the recommended [community standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories) checklist (description, README, license, conduct, contributing, security policy, issue templates, pull request template). Repositories that inherit it score **100% / A** on GitHub community health.

| File | Purpose |
| :--- | :--- |
| **[README.md](README.md)** | How to use the reusable workflows and default files |
| **[LICENSE](LICENSE)** | MIT — reuse, modification, and distribution terms |
| **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** | Contributor Covenant v2.1 |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Branch naming (`feat/`, `fix/`, `docs/`, `chore/`), PR checklist |
| **[SECURITY.md](SECURITY.md)** | Private vulnerability reporting (GitHub advisory + email) |
| **[SUPPORT.md](SUPPORT.md)** | Where to file bugs, questions, and security reports |
| **[GOVERNANCE.md](GOVERNANCE.md)** | Maintainer roles and how defaults are overridden |
| **[FUNDING.yml](.github/FUNDING.yml)** | Sponsor / contact links |
| **[CODEOWNERS](.github/CODEOWNERS)** | Default review owner `@donny-devops` |
| **[Issue templates](.github/ISSUE_TEMPLATE/)** | YAML forms + markdown fallbacks for bug, feature, and question |
| **[Pull request template](.github/PULL_REQUEST_TEMPLATE.md)** | Review checklist |

### Notes for individual repositories

- **License does not inherit.** Add a `LICENSE` file to any repository that is missing one (`api-saas-decision-engine`, `post-quantum-studio`, and any new public repo).
- **Description, topics, and a root README** still need to live in each project. Defaults cannot supply those.
- Repositories that already ship their own community files keep those copies. Remove a local file only when you want the default from this repo.
