output "function_url" {
  description = "Lambda function to be triggered if PR Comment is updated"
  value       = aws_lambda_function_url.webhook_url_vcs[0].function_url
}

output "comment_lambda_function_name" {
  description = "Name of the PR/MR comment handler Lambda function"
  value       = module.process_comment_lambda_vcs[0].lambda_function_name
}

output "comment_lambda_function_arn" {
  description = "ARN of the PR/MR comment handler Lambda function"
  value       = module.process_comment_lambda_vcs[0].lambda_function_arn
}

output "tf_errors_lambda_function_name" {
  description = "Name of the Terraform-errors handler Lambda function"
  value       = module.ai_lambda_vcs[0].lambda_function_name
}

output "tf_errors_lambda_function_arn" {
  description = "ARN of the Terraform-errors handler Lambda function"
  value       = module.ai_lambda_vcs[0].lambda_function_arn
}
