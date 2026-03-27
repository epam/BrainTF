resource "aws_s3_bucket" "demo_validate" {
  bucket        = "braintf-demo-validate-bucket"
  unknown_field = "this-argument-does-not-exist"
}

# Issues caught by Terraform Validate:
# - unknown_field: An argument named "unknown_field" is not expected here
