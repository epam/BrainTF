output "lambda_exec_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = length(aws_iam_role.lambda_exec_role) > 0 ? aws_iam_role.lambda_exec_role[0].arn : null
}
