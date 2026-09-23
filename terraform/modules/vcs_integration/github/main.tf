#======================= GitHub integration with AWS Lambda ===========================#
locals {
  repository_name = regex("([^/]+)$", var.vcs_project_path)[0]
}

# Create GitHub Actions secrets
resource "github_actions_secret" "secrets" {
  for_each = { for var in var.vcs_variables : var.key => var if var.masked }

  repository  = local.repository_name
  secret_name = each.value.key
  value       = each.value.value
}

# Create GitHub Actions variables
resource "github_actions_variable" "variables" {
  for_each = { for var in var.vcs_variables : var.key => var if !var.masked }

  repository    = local.repository_name
  variable_name = each.value.key
  value         = each.value.value
}

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
