data "aws_caller_identity" "current" {}

resource "aws_cloudwatch_log_group" "demo_fixed" {
  name              = "/braintf/demo/fixed"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.demo_fixed.arn

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}

resource "aws_kms_key" "demo_fixed" {
  description             = "KMS key for BrainTF demo CloudWatch log group"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowRootAccountAdministration"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowCloudWatchLogs"
        Effect = "Allow"
        Principal = {
          Service = "logs.eu-west-1.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}
