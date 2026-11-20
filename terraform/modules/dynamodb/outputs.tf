output "table_name" {
  description = "Name of the AI chat-history DynamoDB table"
  value       = module.dynamodb_table.dynamodb_table_id
}

output "table_arn" {
  description = "ARN of the AI chat-history DynamoDB table"
  value       = module.dynamodb_table.dynamodb_table_arn
}
