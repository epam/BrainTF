variable "vcs_project_path" {
  description = "The vcs project path or ID"
  type        = string
}

variable "vcs_variables" {
  description = "List of variables to create in the vcs project"
  type = list(object({
    key         = string                # The variable key
    value       = string                # The variable value
    description = optional(string)      # The description of the variable
    masked      = optional(bool, false) # If true, the variable will be masked in CI/CD logs
    protected   = optional(bool, false) # If true, the variable will only be used in protected branches
  }))
}

variable "manage_repo_config" {
  description = "Whether this instance manages the repo-level GitHub Actions variables and secrets. Only one instance (prod) should; the others only register their own webhook."
  type        = bool
  default     = true
}

variable "deploy_environment" {
  description = "GitHub Environment to create and restrict to the main branch (the environment the prod deploy job runs in). Only managed together with the repo config (manage_repo_config). Empty = none."
  type        = string
  default     = ""
}

variable "function_url" {
  description = "The URL for the webhook function."
  type        = string
}

variable "ai_handler_create" {
  description = "Whether to create AI handler webhooks."
  type        = bool
  default     = false
}

variable "webhook_secret" {
  description = "The webhook secret"
  type        = string
}
