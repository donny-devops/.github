---
name: revops-commerce
description: Price, book, and report PipeFish / OpenClaw commercial work. Use when a user asks to generate revenue, quote a service, wire Stripe/Moltgate, or post a deal to Slack.
---

# RevOps & Agent Commerce

## Catalog

SKUs live in `catalog/services.json`. Do not invent prices in chat — load the catalog.

| SKU | Amount | Cadence |
| --- | --- | --- |
| `mesh.lane.ping` | $25 | one-time |
| `mesh.consult.discovery` | $2,500 | one-time |
| `mesh.audit.security` | $4,500 | one-time |
| `mesh.retain.ops` | $8,000 | monthly |
| `mesh.pqc.migration` | $12,000 | project |

## Booking path

1. Qualify the request (`revenue_intake` DAG or `five-agent-os` intake agent).
2. Price against a real SKU.
3. Collect payment on [openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine) (Moltgate lanes → Stripe). Card data never touches this repo.
4. Recognize the event on `Ledger`.
5. Notify Slack with `deal_blocks()` — only if `SLACK_WEBHOOK_URL` is set via the secret broker.

## Rules

- No fake invoices, customer names, or “closed-won” metrics.
- Retainers are monthly; do not book them as one-time unless the buyer asked.
- Contact for human close: `adonis-jimenez@outlook.com` / [LinkedIn](https://www.linkedin.com/in/adonisjimenez/).
