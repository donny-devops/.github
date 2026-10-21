# Secret management

## Local

```bash
cp .env.example .env
# or
export PIPEFISH_SECRET_FILE=$HOME/.config/pipefish/secrets.env
```

## AWS

Terraform module: `automation/terraform/modules/secret-store`.

Creates:

- KMS key for SSM / Secrets Manager
- prefix `/pipefish/<env>/`
- IAM read policy for the mesh gateway role

Apply only from an account you own, with a remote state backend. CI in this repo
runs `terraform fmt -check` / `validate`, not `apply`.

## GitHub

Repository Actions secrets and OIDC. Reusable workflows do not hard-code credentials.

## DBeaver / SQL

Point DBeaver at `PIPEFISH_LEDGER_PATH` or a local Postgres/Supabase URL stored in
the secret file. Connection strings are secrets.
