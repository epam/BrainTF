#checkov:skip=CKV2_AWS_62:event notifications not required for demo
#checkov:skip=CKV_AWS_144:cross-region replication not required for demo
resource "aws_s3_bucket" "demo_fixed_trivy" {
  bucket = "braintf-demo-fixed-trivy-bucket"

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "demo_fixed_trivy" {
  bucket = aws_s3_bucket.demo_fixed_trivy.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "demo_fixed_trivy" {
  bucket        = aws_s3_bucket.demo_fixed_trivy.id
  target_bucket = aws_s3_bucket.demo_fixed_trivy.id
  target_prefix = "logs/"
}

resource "aws_s3_bucket_public_access_block" "demo_fixed_trivy" {
  bucket                  = aws_s3_bucket.demo_fixed_trivy.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo_fixed_trivy" {
  bucket = aws_s3_bucket.demo_fixed_trivy.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.demo_fixed.arn
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "demo_fixed_trivy" {
  bucket = aws_s3_bucket.demo_fixed_trivy.id

  rule {
    id     = "expire-objects"
    status = "Enabled"

    expiration {
      days = 365
    }
  }
}
