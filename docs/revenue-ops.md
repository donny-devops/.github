# Revenue operations

PipeFish makes money when a buyer pays for attention, a workshop, a retainer, or a
migration — not when a README lists more logos.

## Rails

1. **Paid inbox** — [openclaw-revenue-engine](https://github.com/donny-devops/openclaw-revenue-engine) + Moltgate + Stripe.
2. **Human close** — `adonis-jimenez@outlook.com`, [LinkedIn](https://www.linkedin.com/in/adonisjimenez/), [pipefishlabs.io](https://pipefishlabs.io).
3. **Control-plane ledger** — `pipefish_mesh.Ledger` for local recognition and agent bookkeeping.
4. **GitHub Sponsors / custom FUNDING.yml** — inbound from the public profile.

## SKUs

See `catalog/services.json`. Quote those numbers unless a written SOW supersedes them.

## Automation hooks

| Tool | Recipe |
| --- | --- |
| Slack | `deal_blocks()` in `slack_ops.py` |
| n8n | `automation/n8n/revenue-intake.json` |
| Make | `automation/make/revops-sync.json` |
| Zapier | `automation/zapier/lead-to-slack.json` |
| UiPath / Bardeen | outlined in `docs/automation-mesh.md` (human-in-the-loop RPA) |

Card data stays on Stripe. This repo never stores PANs.
