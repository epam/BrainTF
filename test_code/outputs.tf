output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = module.s3_bucket.bucket_name
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = module.dynamodb.table_name
}

# output "ec2_instance_public_ip" {
#   description = "The public IP address of the EC2 instance"
#   value       = module.ec2_instance.public_ip
# }

output "private_key_path" {
  description = "The path to the generated private key"
  value       = local_file.private_key.filename
}