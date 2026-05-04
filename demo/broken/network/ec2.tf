resource "aws_security_group" "demo_broken" {
  name        = "braintf-demo-broken-sg"
  description = "Demo broken security group"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = "Demo"
    ManagedBy   = "Terraform"
  }
}
