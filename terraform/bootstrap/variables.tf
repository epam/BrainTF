variable "region" {
  description = "The region where AWS resources will be created"
  type        = string
}

variable "vcs_repo_name" {
  description = "The Project name"
  type        = string
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

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "platform_state_bucket_prefix" {
  description = "Custom prefix for the platform state S3 bucket name (stores state of bootstrap + main_module)"
  type        = string
  default     = "backend-state-bucket"
}
