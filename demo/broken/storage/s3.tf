resource "aws_s3_bucket" "demo_broken" {
  bucket = "braintf-demo-broken-bucket"

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

# Missing: aws_s3_bucket_versioning — will be caught by Checkov (CKV_AWS_21)
# Missing: aws_s3_bucket_logging — will be caught by Checkov (CKV_AWS_18)
# Missing: aws_s3_bucket_public_access_block — will be caught by Checkov (CKV_AWS_53, CKV_AWS_54, CKV_AWS_55, CKV_AWS_56)
# Missing: aws_s3_bucket_server_side_encryption_configuration — will be caught by Checkov (CKV_AWS_19)

