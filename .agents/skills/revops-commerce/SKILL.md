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
3. Collect payment with **Checkout Sessions** (`python -m pipefish_mesh checkout <sku> --email …`) or via [openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine) / Moltgate. Card data never touches this repo.
4. Recognize revenue only from **signed Stripe webhooks** (`checkout.session.completed` when `payment_status` is not `unpaid`, plus `checkout.session.async_payment_succeeded`). Never from the success URL.
5. Notify Slack with `deal_blocks()` — only if `SLACK_WEBHOOK_URL` is set via the secret broker.

## Stripe rules

- Restricted API key (`rk_`), stored in the secret broker / AWS Secrets Manager.
- Omit `payment_method_types`. Use Dashboard payment method settings.
- Monthly SKUs → `mode: subscription` + Customer Portal. Do not roll your own renewals.
- Do not set `automatic_tax` until a Tax registration is Collecting.
- Sandboxes for local and CI, not the shared test-mode account.
- Details: `docs/stripe.md`.

## Rules

- No fake invoices, customer names, or “closed-won” metrics.
- Retainers are monthly; do not book them as one-time unless the buyer asked.
- Contact for human close: `adonis-jimenez@outlook.com` / [LinkedIn](https://www.linkedin.com/in/adonisjimenez/).
