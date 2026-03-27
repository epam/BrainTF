#checkov:skip=CKV2_AWS_5:demo resource, not attached to instance
resource "aws_security_group" "demo_fixed" {
  name        = "braintf-demo-fixed-sg"
  description = "Demo fixed security group"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Allow HTTPS from internal network only"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Allow HTTPS outbound to internal network only"
  }

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}
