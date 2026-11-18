variable "vcs_hostname" {
  description = "The VCS hostname for the project"
  type        = string
}

variable "vcs_repo_name" {
  description = "The Project name"
  type        = string
}

variable "environment" {
  description = "The Project environment. Only used as the Environment tag; it never affects resource names."
  type        = string
}

variable "instance_id" {
  description = "ID of an additional BrainTF instance in the same AWS account (set by the deploy workflow for per-branch instances). It is appended to resource names, and such an instance reuses the primary instance's OIDC provider/role and repo-level CI variables. Leave empty for the primary (single or prod) instance, which keeps the un-suffixed names and owns those shared resources."
  type        = string
  default     = ""

  validation {
    # Max 14 chars: the artifacts bucket name is "<stem>-<instance_id>" and S3 caps it at 63.
    condition     = var.instance_id == "" || (can(regex("^[a-z0-9]([a-z0-9-]{0,12}[a-z0-9])?$", var.instance_id)) && var.instance_id != "prod")
    error_message = "instance_id must be empty (primary instance) or 1-14 chars of lowercase letters, digits and '-', not starting or ending with '-', and not 'prod'."
  }
}

variable "github_deploy_environment" {
  description = "GitHub Environment the prod deploy job runs in (deploy-braintf.yml). Jobs in an environment present an 'environment:<name>' OIDC sub claim, so it is added to the role trust, and the environment is created and restricted to the main branch. Empty = no environment. GitHub only."
  type        = string
  default     = "braintf-prod"
}

variable "deploy_branch_prefix" {
  description = "Branch-name prefix whose branches may deploy their own ephemeral BrainTF instance. The shared OIDC role trusts 'refs/heads/<prefix>*' as a single wildcard, so new branches under this prefix need no prod re-apply. Must match the gate prefix in deploy-braintf.yml (env DEPLOY_BRANCH_PREFIX). Empty disables the wildcard (trust falls back to the explicit deploy-branches.txt list only). GitHub only."
  type        = string
  default     = "feature/"
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

variable "owner_github" {
  description = "GitHub login of whoever deployed this instance. Set by the deploy workflow (github.actor); recorded as the OwnerGithub tag. Empty = no tag."
  type        = string
  default     = ""
}

variable "target_branch" {
  description = "Git branch this instance serves. When set, the comment lambda ignores comments on pull/merge requests from any other branch, and the Branch tag is added. Empty (prod) = handle every branch."
  type        = string
  default     = ""
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

  validation {
    condition     = contains(["github", "gitlab"], var.vcs_provider)
    error_message = "vcs_provider must be github or gitlab"
  }
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

variable "platform_state_bucket" {
  description = "Name of the bootstrap (platform) state S3 bucket. Bootstrap writes it to terraform.auto.tfvars on apply; set it by hand only if bootstrap cannot be applied on this machine (value: terraform output state_bucket_name in terraform/bootstrap)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.platform_state_bucket))
    error_message = "platform_state_bucket must be a valid S3 bucket name. Run terraform apply in terraform/bootstrap to regenerate terraform.auto.tfvars."
  }
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

variable "ai_temperature" {
  description = "The sampling temperature for the AI model. Must be between 0 and 2."
  type        = number

  validation {
    condition     = var.ai_temperature >= 0 && var.ai_temperature <= 2
    error_message = "AI temperature must be between 0 and 2."
  }
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
