terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

variable "name_prefix" {
  type        = string
  description = "Prefix for KMS, secret, and IAM names."
}

variable "environment" {
  type        = string
  description = "dev, preview, or prod."
}

resource "aws_kms_key" "mesh" {
  description             = "PipeFish mesh secrets (${var.environment})"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "mesh" {
  name          = "alias/${var.name_prefix}-${var.environment}"
  target_key_id = aws_kms_key.mesh.key_id
}

resource "aws_secretsmanager_secret" "mesh" {
  name       = "${var.name_prefix}/${var.environment}/control-plane"
  kms_key_id = aws_kms_key.mesh.arn
}

resource "aws_ssm_parameter" "prefix_note" {
  name  = "/pipefish/${var.environment}/README"
  type  = "String"
  value = "Put runtime secrets under this prefix. Do not commit values."
}

output "secret_arn" {
  value = aws_secretsmanager_secret.mesh.arn
}

output "kms_key_arn" {
  value = aws_kms_key.mesh.arn
}
