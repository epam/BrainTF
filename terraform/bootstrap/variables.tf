variable "vcs_repo_name" {
  description = "The Project name"
  type        = string
}

variable "region" {
  description = "The AWS region for all BrainTF resources (e.g. eu-central-1). Bootstrap copies it to main_module. AWS_REGION, AWS_DEFAULT_REGION and the AWS CLI profile region are not used"
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z]+(-[a-z]+)+-[0-9]+$", var.region))
    error_message = "region must be an AWS region code such as eu-central-1. An empty value is not allowed: the AWS provider would fall back to AWS_REGION or the AWS CLI profile."
  }
}

variable "environment" {
  description = "The Project environment"
  type        = string
}

variable "team" {
  description = "The owner team"
  type        = string
}

variable "deployed_by" {
  description = "The deployment method"
  type        = string
}

variable "owner_mail" {
  description = "The owner e-mail"
  type        = string
}

variable "platform_state_bucket_prefix" {
  description = "Custom prefix for the platform state S3 bucket name (stores state of bootstrap + main_module). Set it here only: main_module receives the full bucket name from bootstrap"
  type        = string
  default     = "backend-state-bucket"
}

variable "state_bucket_force_destroy" {
  description = "Allow Terraform to delete the state bucket together with all its objects and versions. Keep false to protect the state; set true only for demo/dev teardown."
  type        = bool
  default     = false
}
