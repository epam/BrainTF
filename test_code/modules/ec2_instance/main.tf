resource "aws_instance" "this" {
  ami           = var.ami_id
  instance_type = var.instance_type
  # key_name      = var.key_name

  tags = {
    Name        = var.instance_name
    Environment = "Test"
  }

  vpc_security_group_ids = var.security_groups
}

# Security Group for the EC2 instance
resource "aws_security_group" "this" {
  name        = "ec2-sg-${var.instance_name}"
  description = "Allow SSH and HTTP access"
  vpc_id      = var.vpc_id

  # ingress {
  #   from_port   = 22
  #   to_port     = 22
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }
  #
  # ingress {
  #   from_port   = 80
  #   to_port     = 80
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
