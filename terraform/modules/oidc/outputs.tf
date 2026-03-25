output "oidc_role_arn" {
  description = "The oidc role arn"
  value       = aws_iam_role.vcs_oidc_role.arn
}
