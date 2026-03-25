terraform {
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

# Generate a random suffix for globally unique names
resource "random_id" "unique_suffix" {
  byte_length = 4
}

# Generate an RSA key pair
resource "tls_private_key" "generated_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Save the private key locally
resource "local_file" "private_key" {
  filename        = "${path.module}/terraform-demo-key-${random_id.unique_suffix.hex}.pem"
  content         = tls_private_key.generated_key.private_key_pem
  file_permission = "0400"
}

# Key Pair Module
module "key_pair" {
  source     = "./modules/ec2_instance"
  key_name   = "terraform-demo-key-${random_id.unique_suffix.hex}"
  public_key = tls_private_key.generated_key.public_key_openssh
}

# S3 Bucket Module
module "s3_bucket" {
  source      = "./modules/s3_bucket"
  bucket_name = "terraform-demo-bucket-${random_id.unique_suffix.hex}"
}

# DynamoDB Module
module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = "terraform-state-locks-${random_id.unique_suffix.hex}"
}

# EC2 Instance Module
module "ec2_instance" {
  source        = "./modules/ec2_instance"
  instance_name = "terraform-demo-instance"
  instance_type = var.instance_type
  ami_id        = var.ami_id
  # key_name        = module.key_pair.key_name
  security_groups = [module.ec2_instance.security_group_id]
  vpc_id          = "vpc_id"
}
