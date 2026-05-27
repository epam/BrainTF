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
  default     = "artifacts" # Default path for storing Terraform artifacts
}

variable "log_level" {
  description = "The logging level for AWS Lambda functions. Possible values: DEBUG, INFO, WARN, ERROR."
  type        = string
  default     = "INFO" # Default log level for Lambda functions

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

variable "tfstate_bucket_prefix" {
  description = "The prefix to be used for naming a TFState bucket"
  type        = string
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
  description = "The oidc provider"
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
