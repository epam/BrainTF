output "artifacts_bucket_name" {
  description = "Name of the S3 artifacts bucket"
  value       = module.s3_bucket.s3_bucket_id
}

output "artifacts_bucket_arn" {
  description = "ARN of the S3 artifacts bucket"
  value       = module.s3_bucket.s3_bucket_arn
}
