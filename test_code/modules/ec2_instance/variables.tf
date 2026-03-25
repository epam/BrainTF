variable "instance_name" {
  description = "The name of the EC2 instance"
  type        = string
}

# variable "instance_type" {
#   description = "The type of the EC2 instance"
#   type        = string
# }
#
# variable "ami_id" {
#   description = "The AMI ID for the EC2 instance"
#   type        = string
# }

# variable "key_name" {
#   description = "The name of the EC2 key pair"
#   type        = string
# }

variable "security_groups" {
  description = "List of security group IDs to associate with the instance"
  type        = list(string)
}
#
# variable "vpc_id" {
#   description = "The VPC ID where the EC2 instance will be deployed"
#   type        = string
# }