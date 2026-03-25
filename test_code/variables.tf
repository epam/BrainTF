variable "aws_region" {
  description = "The AWS region where resources will be deployed"
  type        = string
  default     = "eu-west-1"
}

variable "ami_id" {
  description = "The AMI ID for the EC2 instance"
  type        = string
  default     = "ami-0c02fb55956c7d316" # Amazon Linux 2 (Free Tier eligible)
}

variable "instance_type" {
  description = "The type of the EC2 instance"
  type        = string
  default     = "t2.micro" # Free Tier eligible
}

variable "vpc_id" {
  description = "The VPC ID where the EC2 instance will be deployed"
  type        = string
  default     = "vpc-123456" # Replace with your VPC ID
}
