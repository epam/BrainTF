resource "aws_s3_bucket" "demo_broken" {
  bucket = "braintf-demo-broken-bucket"

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}
