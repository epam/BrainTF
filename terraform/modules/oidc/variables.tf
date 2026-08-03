variable "vcs_provider" {
  description = "The VCS provider (e.g., github, gitlab)"
  type        = string
}

variable "oidc_role_name" {
  description = "The name of the IAM role to create"
  type        = string
}

variable "oidc_policy_name" {
  description = "The name of the IAM policy to create"
  type        = string
}

variable "oidc_provider" {
  description = "The oidc provider"
  type        = string
}

variable "artifacts_bucket" {
  description = "The name of the S3 bucket for artifacts"
  type        = string
}

variable "managed_state_bucket" {
  description = "The name of the S3 bucket used for the managed workload Terraform state"
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key for encryption"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "client_id_list" {
  description = "List of client IDs for the OIDC provider"
  type        = list(string)
}

variable "aud_variable" {
  description = "The audience variable for the OIDC provider"
  type        = string
}

variable "sub_variable" {
  description = "The subject variable for the OIDC provider"
  type        = string
}

variable "sub_values" {
  description = "The subject values for the OIDC provider"
  type        = list(string)
}
