resource "aws_cloudwatch_log_group" "demo_broken" {
  name              = "/braintf/demo/broken"
  retention_in_days = 7

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

# Missing: retention_in_days >= 365 — will be caught by Checkov (CKV_AWS_338)
# Missing: kms_key_id — will be caught by Checkov (CKV_AWS_158)

