resource "aws_s3_bucket" "demo_broken_trivy" {
  bucket = "braintf-demo-broken-trivy-bucket"

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo_broken_trivy" {
  bucket = aws_s3_bucket.demo_broken_trivy.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Issues caught by Trivy (trivy config):
# - Missing aws_s3_bucket_public_access_block (AVD-AWS-0094)
# - KMS encryption not used, only AES256 (AVD-AWS-0132)
# - Missing aws_s3_bucket_versioning (AVD-AWS-0090)

