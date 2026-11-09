# OpenClaw revenue-engine patch (blocked 403)

This agent cannot push `donny-devops/openclaw-revenue-engine` (`cursor[bot]` 403). The implementation is committed locally as `donny-devops/stripe-checkout-hardening-dc36` (`c054751`) and exported here so you can apply it after granting write access.

## Apply

```bash
git clone git@github.com:donny-devops/openclaw-revenue-engine.git
cd openclaw-revenue-engine
git checkout -b donny-devops/stripe-checkout-hardening-dc36
git am --3way ../.github/patches/openclaw-revenue-engine-stripe-checkout-hardening.patch
npm test
git push -u origin donny-devops/stripe-checkout-hardening-dc36
```

If `git am` conflicts, use `git apply --3way patches/openclaw-revenue-engine-stripe-checkout-hardening.patch` from a checkout of `openclaw-revenue-engine` `main`.

## What the patch contains

- `stripe@23` / API `2026-09-30.endive`
- RAK-first keys (`STRIPE_RESTRICTED_KEY`, production requires `rk_live_*`)
- Checkout Sessions without `payment_method_types`, with `integration_identifier`
- `$8,000/mo` `gitops-retainer` subscription + Customer Portal
- `async_payment_*` webhooks, unpaid `completed` skip, invoice/subscription/risk handlers
- AES-256-GCM PII sealing, audit log, metrics, `/ready`, intrusion windows
- Async billing DAG that emits PipeFish A2A envelopes
