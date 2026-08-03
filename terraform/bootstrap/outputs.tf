output "state_bucket_name" {
  description = "Name of the S3 state bucket created by bootstrap (can be reused as managed_state_bucket in main_module)"
  value       = module.s3_state_bucket.s3_bucket_id
}

output "state_bucket_arn" {
  description = "ARN of the S3 state bucket created by bootstrap"
  value       = module.s3_state_bucket.s3_bucket_arn
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for bucket encryption"
  value       = module.s3_bucket_kms_key.key_arn
}
