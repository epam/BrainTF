output "function_url" {
  description = "Lambda function to be triggered if PR Comment is updated"
  value       = aws_lambda_function_url.webhook_url_vcs[0].function_url
}
