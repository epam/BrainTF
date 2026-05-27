output "webhook_id" {
  description = "The ID of the created GitLab webhook"
  value       = length(gitlab_project_hook.webhook) > 0 ? gitlab_project_hook.webhook[0].id : null
}
