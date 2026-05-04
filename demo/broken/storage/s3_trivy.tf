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
