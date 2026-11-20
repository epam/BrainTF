# ======================= Instance summary =======================
# Everything needed to find and wire up the deployed instance. All module
# lookups use try() because every module is count-gated (ai_handler_create /
# is_primary / vcs_provider).

output "instance_id" {
  description = "This instance's ID — the resource-name suffix and state-key segment (empty for the primary instance)."
  value       = var.instance_id
}

output "ssm_parameter_prefix" {
  description = "SSM path prefix holding this instance's tokens and webhook secret."
  value       = local.ssm_prefix
}

# ======================= S3 artifacts bucket =======================

output "artifacts_bucket_name" {
  description = "Name of the S3 artifacts bucket."
  value       = try(module.artifacts_bucket[0].artifacts_bucket_name, null)
}

output "artifacts_bucket_arn" {
  description = "ARN of the S3 artifacts bucket."
  value       = try(module.artifacts_bucket[0].artifacts_bucket_arn, null)
}

# ======================= Lambda functions =======================

output "comment_lambda_function_name" {
  description = "Name of the PR/MR comment handler Lambda."
  value       = try(module.ai_lambda[0].comment_lambda_function_name, null)
}

output "comment_lambda_function_arn" {
  description = "ARN of the PR/MR comment handler Lambda."
  value       = try(module.ai_lambda[0].comment_lambda_function_arn, null)
}

output "comment_lambda_function_url" {
  description = "Public function URL the repo webhook invokes on every PR comment."
  value       = try(module.ai_lambda[0].function_url, null)
}

output "tf_errors_lambda_function_name" {
  description = "Name of the Terraform-errors handler Lambda (S3 logs trigger)."
  value       = try(module.ai_lambda[0].tf_errors_lambda_function_name, null)
}

output "tf_errors_lambda_function_arn" {
  description = "ARN of the Terraform-errors handler Lambda (S3 logs trigger)."
  value       = try(module.ai_lambda[0].tf_errors_lambda_function_arn, null)
}

# ======================= IAM =======================

output "lambda_exec_role_arn" {
  description = "ARN of this instance's Lambda execution role."
  value       = try(module.iam[0].lambda_exec_role_arn, null)
}

output "oidc_role_arn" {
  description = "ARN of the shared VCS-OIDC role CI assumes. Set only on the primary instance (which owns it); other instances reuse the same role."
  value       = try(module.oidc[0].oidc_role_arn, null)
}

# ======================= DynamoDB =======================

output "dynamodb_table_name" {
  description = "Name of the AI chat-history DynamoDB table."
  value       = try(module.ai_dynamodb_table[0].table_name, null)
}

output "dynamodb_table_arn" {
  description = "ARN of the AI chat-history DynamoDB table."
  value       = try(module.ai_dynamodb_table[0].table_arn, null)
}

# ======================= VCS integration =======================

output "github_webhook_id" {
  description = "ID of the GitHub repository webhook pointing at this instance's comment Lambda."
  value       = try(module.vcs_integration_github[0].webhook_id, null)
}

# ======================= Consolidated =======================

output "instance" {
  description = "Consolidated view of the deployed instance (handy with 'terraform output -json instance')."
  value = {
    instance_id   = var.instance_id
    environment   = var.environment
    owner_github  = var.owner_github
    target_branch = var.target_branch
    region        = local.region

    artifacts_bucket_name = try(module.artifacts_bucket[0].artifacts_bucket_name, null)
    artifacts_bucket_arn  = try(module.artifacts_bucket[0].artifacts_bucket_arn, null)

    comment_lambda_function_name   = try(module.ai_lambda[0].comment_lambda_function_name, null)
    comment_lambda_function_url    = try(module.ai_lambda[0].function_url, null)
    tf_errors_lambda_function_name = try(module.ai_lambda[0].tf_errors_lambda_function_name, null)

    lambda_exec_role_arn = try(module.iam[0].lambda_exec_role_arn, null)
    oidc_role_arn        = try(module.oidc[0].oidc_role_arn, null)

    dynamodb_table_name = try(module.ai_dynamodb_table[0].table_name, null)

    ssm_parameter_prefix = local.ssm_prefix
    github_webhook_id    = try(module.vcs_integration_github[0].webhook_id, null)
  }
}
