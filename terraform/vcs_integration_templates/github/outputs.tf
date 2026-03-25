output "webhook_id" {
  description = "The ID of the created GitLab webhook"
  value       = length(github_repository_webhook.webhook) > 0 ? github_repository_webhook.webhook[0].id : null
}
