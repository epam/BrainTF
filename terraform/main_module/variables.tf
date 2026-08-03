variable "region" {
  description = "The region where AWS resources will be created"
  type        = string
}

variable "vcs_hostname" {
  description = "The VCS hostname for the project"
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

variable "vcs_token" {
  description = "The VCS token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "ai_token" {
  description = "The AI token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "vcs_provider" {
  description = "The VCS provider used for deployment (e.g., github, gitlab)"
  type        = string
}

variable "vcs_project_path" {
  description = "The path to the VCS project"
  type        = string
}

variable "artifacts_path" {
  description = "The path where the corrected Terraform files (artifacts) will be stored."
  type        = string
  default     = "artifacts"
}

variable "log_level" {
  description = "The logging level for AWS Lambda functions. Possible values: DEBUG, INFO, WARN, ERROR."
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARN", "ERROR"], var.log_level)
    error_message = "Log level must be one of DEBUG, INFO, WARN, or ERROR."
  }
}

variable "ai_handler_create" {
  description = "Whether to create AI handler webhooks."
  type        = bool
  default     = false
}

variable "rag_enable" {
  description = "Whether to turn on RAG for AI handler."
  type        = bool
  default     = false
}

variable "artifacts_bucket_prefix" {
  description = "The prefix to be used for naming an artifacts bucket"
  type        = string
}

variable "platform_state_bucket_prefix" {
  description = "Prefix for the bootstrap (platform) state S3 bucket name. Must match the value used in the bootstrap module."
  type        = string
  default     = "backend-state-bucket"
}

variable "managed_state_bucket" {
  description = "Name of an existing S3 bucket to store Terraform state for the code under WORK_DIRS (the workload managed by this pipeline). If empty, the bootstrap platform state bucket will be used with a separate prefix directory."
  type        = string
  default     = ""
}

variable "managed_state_key" {
  description = "S3 key (path) for the Terraform state file used by the managed workload (code under WORK_DIRS). Must include a directory prefix, e.g. 'pipeline/terraform.tfstate'."
  type        = string
  default     = "pipeline/terraform.tfstate"

  validation {
    condition     = can(regex("^[^/].*/.+\\.tfstate$", var.managed_state_key))
    error_message = "managed_state_key must include a directory prefix and end with .tfstate (e.g. 'pipeline/terraform.tfstate'). Leading slash is not allowed."
  }
}

variable "llm_model" {
  description = "The name or identifier of the LLM (Large Language Model) to be used"
  type        = string
}

variable "ai_api_endpoint" {
  description = "The API endpoint for the AI service"
  type        = string
}

variable "private_subnet_ids" {
  description = "VPC Private Subnet IDs"
  type        = list(string)
}

variable "security_groups" {
  description = "Security Groups for Lambda-Git Connection"
  type        = list(string)
}

variable "job_token" {
  description = "Git Notes token used for GitLab integration"
  type        = string
}

variable "oidc_provider" {
  description = "OIDC identity provider domain (issuer). Used to construct IAM trust policy condition keys (e.g. <provider>:aud, <provider>:sub) and the OIDC provider URL. Use 'token.actions.githubusercontent.com' for GitHub or 'gitlab.com' for GitLab."
  type        = string
}

variable "run_tflint_analysis" {
  description = "Enable or disable the TFLint analysis stage. Default is false."
  type        = bool
  default     = false
}

variable "run_terraform_validate" {
  description = "Enable or disable the Terraform validate stage. Default is false."
  type        = bool
  default     = false
}

variable "run_checkov_analysis" {
  description = "Enable or disable the Checkov analysis stage. Default is false."
  type        = bool
  default     = false
}

variable "run_tfsec_analysis" {
  description = "Enable or disable the TFSec analysis stage. Default is false."
  type        = bool
  default     = false
}

variable "run_trivy_analysis" {
  description = "Enable or disable the Trivy analysis stage. Default is false."
  type        = bool
  default     = false
}

variable "run_terraform_plan" {
  description = "Enable or disable the Terraform plan stage. Default is false."
  type        = bool
  default     = false
}

variable "run_terraform_apply" {
  description = "Enable or disable the Terraform apply stage. Default is false."
  type        = bool
  default     = false
}
