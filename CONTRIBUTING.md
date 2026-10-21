# Contributing

Thank you for contributing! This guide applies to all `donny-devops` repositories.

## Getting started

1. **Fork** the repository and clone it locally.
2. Create a branch from `main`: `git checkout -b feat/your-change`.
3. Make your changes with clear, focused commits.

## Branch naming

- `feat/<name>` — new features
- `fix/<name>` — bug fixes
- `docs/<name>` — documentation only
- `chore/<name>` — maintenance, CI, dependencies
- `security/<name>` — security-sensitive changes

## This repository

`donny-devops/.github` is the private control plane. Python lives in
`src/pipefish_mesh`, the Go gateway in `services/mesh-gateway`, and the
TypeScript MCP server in `mcp/pipefish-mesh`.

```bash
python -m pip install -e ".[dev]"
ruff check src tests
pytest
(cd services/mesh-gateway && go test ./...)
(cd mcp/pipefish-mesh && npm test)
```

Do not add profile links to repositories that are missing from `catalog/repos.yaml`.
Do not commit secrets — use `.env.example` and the secret broker.

## Before you open a PR

- Run the repo's linters and tests locally.
- Follow the existing code style.
- Update documentation and tests to match your change.
- Write a clear PR title and description (link any related issue).

## Pull requests

- Target the `main` branch.
- Keep PRs small and focused on one change.
- A maintainer will review; address feedback promptly.

## Security issues

Do **not** open a public issue for security vulnerabilities. See
[`SECURITY.md`](SECURITY.md) for the responsible disclosure process.

## License

By contributing, you agree that your contributions will be licensed under the
same license as the repository.
