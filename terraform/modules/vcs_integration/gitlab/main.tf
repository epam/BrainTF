#======================= GitLab integration with AWS Lambda ===========================#
resource "gitlab_project_variable" "project_variables" {
  for_each    = { for var in var.vcs_variables : var.key => var }
  project     = var.vcs_project_path
  key         = each.value.key
  value       = each.value.value
  description = try(each.value.description, null)
  masked      = try(each.value.masked, false)
  protected   = try(each.value.protected, false)
}

resource "gitlab_project_hook" "webhook" {
  count                   = var.ai_handler_create ? 1 : 0
  name                    = "Webhook for AI Handler"
  project                 = var.vcs_project_path
  url                     = var.function_url
  enable_ssl_verification = true
  note_events             = true
  token                   = var.webhook_secret
}
