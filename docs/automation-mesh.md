# Automation mesh

These recipes are **adapters**, not hosted accounts. Import them into your own
n8n, Make, Zapier, Jenkins, or UiPath tenant.

## n8n / Make / Zapier

Webhook in → validate envelope → optional Stripe/Moltgate lookup → Slack out.
JSON graphs live under `automation/`.

## Ansible

`automation/ansible/playbooks/mesh-bootstrap.yml` installs Python deps and the
gateway binary layout on a Linux box. It never writes secrets into templates.

## Jenkins

Root `Jenkinsfile` runs pytest, Go tests, and Newman against a local gateway.

## Postman / Newman

`automation/postman/pipefish-mesh.postman_collection.json` covers `/health`,
`/v1/catalog`, and `/v1/envelopes`.

## Cloudflare

`automation/cloudflare/wrangler.toml` is a Pages + tunnel stub. Put the tunnel
token in SSM, not git. Pair with Tailscale or XPipe for break-glass SSH.

## Tailscale / XPipe

Use Tailscale ACLs so the mesh gateway is only reachable from your tailnet.
XPipe can bookmark that node; do not commit connection passwords.

## UiPath / Bardeen

Keep RPA at the edge (browser clicks, CRM updates). The mesh owns decisions and
money. A Bardeen or UiPath job should POST an envelope, not fork the ledger.
