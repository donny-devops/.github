# Stripe integration (Checkout, Billing, webhooks)

Latest API version: **2026-09-30.endive**. Use a [restricted API key](https://docs.stripe.com/keys.md#manage-your-api-keys) (`rk_`) and a dedicated [sandbox](https://docs.stripe.com/sandboxes.md) for local work and another sandbox for CI — not the account’s shared test mode.

## What to charge with

| SKU cadence | Stripe surface |
| --- | --- |
| `one_time` / `project` | Checkout Sessions `mode: payment` |
| `monthly` (`mesh.retain.ops`) | Checkout Sessions `mode: subscription` + Billing webhooks |
| Agent ping via Moltgate | Keep card data on Stripe / Moltgate; this repo never sees PANs |

Do **not** use the Charges API, Sources API, Tokens API, or the legacy Card Element.

Each SKU is its own Product name. Monthly vs one-time is a Price on that product, not a deprecated `plan`.

## Checkout payload

`pipefish_mesh.stripe_checkout.build_checkout_session` always:

- omits `payment_method_types` (dynamic payment methods from the Dashboard)
- sets `integration_identifier` (`pipefish-` + 8 random letters)
- writes a **pending** ledger row and puts that id on `client_reference_id`
- leaves `automatic_tax` off unless a Tax registration is already **Collecting**

```bash
python -m pipefish_mesh checkout mesh.audit.security --email buyer@example.com
```

Instantiate `StripeClient` from the optional `stripe>=16` extra. Do not set a global `stripe.api_key`.

Self-serve retainer changes (upgrade, cancel, payment method) go through the [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md), not a custom card form.

## Webhooks are required

Fulfillment belongs in `pipefish_mesh.stripe_webhooks.handle_webhook`, not the success page.

| Event | Action |
| --- | --- |
| `checkout.session.completed` | Recognize **only if** `payment_status != unpaid` |
| `checkout.session.async_payment_succeeded` | Recognize when delayed methods settle |
| `checkout.session.async_payment_failed` | Mark the pending row failed |
| `customer.subscription.*` | Sync retainer state |
| `invoice.paid` / `invoice.payment_failed` | Recurring recognize / dunning |
| `charge.dispute.created`, `charge.refunded`, `radar.early_fraud_warning.created` | Risk review |

Verify `Stripe-Signature` before parsing JSON. Store `STRIPE_WEBHOOK_SECRET` in the secret broker (SSM / Secrets Manager on AWS), same as the RAK.

## Tax

Do not enable `automatic_tax` until Dashboard → Tax → Registrations shows **Collecting** for the buyer’s jurisdiction. Enabling the flag with no registration collects **zero tax and returns no error**.

If you charge US or EU customers, plan Stripe Tax alongside Billing. See [Collect taxes for recurring payments](https://docs.stripe.com/billing/taxes/collect-taxes.md). Confirm the product tax code from the [Tax Codes API](https://docs.stripe.com/api/tax_codes.md) — do not guess a `txcd_`.

## Keys and environments

- Prefer `STRIPE_RESTRICTED_KEY` (`rk_test_` / `rk_live_`) with least privilege (Checkout Sessions write, Customers read, Webhooks none on the API key — webhooks use the endpoint secret).
- Never commit keys. Gitleaks in reusable CI is the backstop.
- Production live keys stay in AWS Secrets Manager (`automation/terraform/modules/secret-store`).
- Rotate on personnel change. Roll immediately if a key leaks.

## Apply the same rules in `openclaw-revenue-engine`

That service already verifies webhook signatures and creates Checkout Sessions. Remaining gaps versus current Stripe guidance:

- Pin API version `2026-09-30.endive` and `stripe` Node SDK 23
- Handle `checkout.session.async_payment_succeeded` / `async_payment_failed` and skip unpaid `completed` events
- Add `integration_identifier`
- Use `mode: subscription` for retainers; add Customer Portal
- Default new keys to RAKs; keep CI on a sandbox, not shared test mode
