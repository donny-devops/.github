---
name: secret-hygiene
description: Resolve and rotate secrets for donny-devops repos without committing credentials. Use when adding env vars, AWS SSM, GitHub Actions secrets, or debugging auth failures.
---

# Secret Hygiene

## Resolution order

`SecretBroker` checks, in order:

1. Process environment
2. `PIPEFISH_SECRET_FILE` (JSON or `KEY=VALUE`)
3. AWS SSM under `PIPEFISH_SSM_PREFIX` (optional, needs boto3)

Never log the value. `source_of(name)` only returns the backend label.

## GitHub Actions

- Prefer OIDC to cloud roles over long-lived keys.
- Reusable workflows accept `secrets: inherit` from the caller.
- This repo’s security workflow scans with Gitleaks, TruffleHog, and Dependency Review.

## Forbidden

- Real API keys, tokens, or private keys in git
- `.env` files (use `.env.example`)
- Pasting secrets into issue templates or Slack payloads
