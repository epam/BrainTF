#checkov:skip=CKV2_AWS_62:event notifications not required for demo
#checkov:skip=CKV_AWS_144:cross-region replication not required for demo
resource "aws_s3_bucket" "demo_validate" {
  bucket = "braintf-demo-validate-bucket"

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

resource "aws_kms_key" "demo_validate_kms" {
  description         = "KMS key for demo validate S3 bucket"
  enable_key_rotation = true
}

resource "aws_s3_bucket_versioning" "demo_validate" {
  bucket = aws_s3_bucket.demo_validate.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "demo_validate" {
  bucket        = aws_s3_bucket.demo_validate.id
  target_bucket = aws_s3_bucket.demo_validate.id
  target_prefix = "logs/"
}

resource "aws_s3_bucket_public_access_block" "demo_validate" {
  bucket                  = aws_s3_bucket.demo_validate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo_validate" {
  bucket = aws_s3_bucket.demo_validate.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.demo_validate_kms.arn
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "demo_validate" {
  bucket = aws_s3_bucket.demo_validate.id

  rule {
    id     = "expire-objects"
    status = "Enabled"

    expiration {
      days = 365
    }
  }
}
