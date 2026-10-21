# secret-store

Creates a KMS key, a Secrets Manager secret, and an SSM prefix note for one
PipeFish environment. No secret values are set by this module.

```hcl
module "secrets" {
  source      = "./automation/terraform/modules/secret-store"
  name_prefix = "pipefish"
  environment = "dev"
}
```
