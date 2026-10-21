# Security Policy

## Supported versions

Only the latest release / `main` branch is actively supported with security
updates. Pinned older versions should be updated to the latest release.

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Report them privately to: **adonis-jimenez@outlook.com**

Include:
- Affected repository and version
- Steps to reproduce
- Potential impact

We will acknowledge within 48 hours and aim to publish a fix and advisory
within 90 days, with coordinated disclosure.

## Secrets

This control plane resolves secrets through `pipefish_mesh.SecretBroker`
(environment → local file → optional AWS SSM). Capability tokens on A2A
envelopes are scopes, not credentials. Never commit `.env` files, tunnel
tokens, Stripe keys, or webhook URLs.

## Disclosure expectations

We follow responsible (coordinated) disclosure. Please give us a reasonable
window to patch before publishing details, and we will credit reporters in
the advisory unless you request anonymity.
