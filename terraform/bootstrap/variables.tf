variable "region" {
  description = "The region where AWS resources will be created"
  type        = string
}

variable "vcs_repo_name" {
  description = "The name of the project"
  type        = string
}

variable "account_id" {
  description = "The account ID for the project"
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
