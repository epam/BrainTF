#======================= GitHub integration with AWS Lambda ===========================#
locals {
  repository_name = regex("([^/]+)$", var.vcs_project_path)[0]
}

# Create GitHub Actions secrets (repo-level, shared: only the instance that owns
# the repo config - prod - manages them)
resource "github_actions_secret" "secrets" {
  for_each = var.manage_repo_config ? { for var in var.vcs_variables : var.key => var if var.masked } : {}

  repository  = local.repository_name
  secret_name = each.value.key
  value       = each.value.value
}

# Create GitHub Actions variables (repo-level, shared: see above)
resource "github_actions_variable" "variables" {
  for_each = var.manage_repo_config ? { for var in var.vcs_variables : var.key => var if !var.masked } : {}

  repository    = local.repository_name
  variable_name = each.value.key
  value         = each.value.value
}

# One webhook per instance, pointing at that instance's own function URL.
resource "github_repository_webhook" "webhook" {
  count      = var.ai_handler_create ? 1 : 0
  repository = local.repository_name

  configuration {
    url          = var.function_url
    content_type = "json"
    insecure_ssl = false
    secret       = var.webhook_secret
  }

  events = [
    "issue_comment"
  ]
}

# GitHub Environment the prod deploy job runs in. A job in an environment presents
# "environment:<name>" as its OIDC sub claim, whatever branch it runs from, and the
# AWS role trusts that claim. Restricting the environment to main is what keeps a
# workflow on any other branch from assuming the role through it.
resource "github_repository_environment" "deploy" {
  count       = var.manage_repo_config && var.deploy_environment != "" ? 1 : 0
  repository  = local.repository_name
  environment = var.deploy_environment

  deployment_branch_policy {
    protected_branches     = false
    custom_branch_policies = true
  }

  # Reviewers and timers are set by hand in the repository settings.
  lifecycle {
    ignore_changes = [reviewers, wait_timer, prevent_self_review, can_admins_bypass]
  }
}

resource "github_repository_environment_deployment_policy" "deploy_main" {
  count          = var.manage_repo_config && var.deploy_environment != "" ? 1 : 0
  repository     = local.repository_name
  environment    = github_repository_environment.deploy[0].environment
  branch_pattern = "main"
}
