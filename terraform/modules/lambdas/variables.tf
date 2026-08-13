variable "vcs_repo_name" {
  description = "Repo name used for resource tagging and naming"
  type        = string
}

variable "vcs_provider" {
  description = "The VCS provider used for deployment (e.g., github, gitlab)"
  type        = string
}

variable "artifacts_bucket" {
  description = "The artifacts bucket name"
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key used for encryption"
  type        = string
}

variable "vcs_token_name" {
  type        = string
  description = "Parameter Store Variable Name for Git Token"
  default     = ""
}

variable "lambda_exec_role_arn" {
  type        = string
  description = "ARN of the role to execute the lambda function"
  default     = ""
}

variable "vcs_api_endpoint" {
  description = "The API endpoint for VCS integration (e.g., GitLab, GitHub)"
  type        = string
}

variable "webhook_secret_name" {
  description = "The name of the secret used for securing webhooks"
  type        = string
}

variable "ai_api_token_name" {
  description = "The name of the secret storing the AI API token"
  type        = string
}

variable "llm_model" {
  description = "The name or identifier of the LLM (Large Language Model) to be used"
  type        = string
}

variable "ai_api_base_url" {
  description = "The API base URL for the AI service"
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

variable "ai_handler_create" {
  type        = string
  description = "AI handler creation trigger"
}

variable "rag_enable" {
  description = "Whether to turn on RAG for AI handler."
  type        = bool
  default     = false
}

variable "dynamodb_table_name" {
  description = "The name for a dynamodb table"
  type        = string
}

variable "artifacts_path" {
  description = "The path where the corrected Terraform files (artifacts) will be stored."
  type        = string
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

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
}
