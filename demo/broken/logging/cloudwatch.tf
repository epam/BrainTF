resource "aws_cloudwatch_log_group" "demo_broken" {
  name              = "/braintf/demo/broken"
  retention_in_days = 7

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}
