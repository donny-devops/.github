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

GitHub automatically applies these files across all repositories under `donny-devops` that do not define their own:

- **[Contributing Guide](CONTRIBUTING.md)**: Standard git branching model (`feat/`, `fix/`, `docs/`, `chore/`), PR checklist, and contribution guidelines.
- **[Code of Conduct](CODE_OF_CONDUCT.md)**: Contributor Covenant v2.1.
- **[Security Policy](SECURITY.md)**: Coordinated vulnerability disclosure protocol.
- **[Issue Templates](.github/ISSUE_TEMPLATE/)**:
  - `bug_report.yml`: Structured form for reporting bugs and reproduction steps.
  - `feature_request.yml`: Structured form for proposing features.
- **[Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)**: Standard PR review checklist.
