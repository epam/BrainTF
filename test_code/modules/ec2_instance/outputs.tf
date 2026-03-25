output "public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.this.public_ip
}

output "security_group_id" {
  description = "The ID of the security group"
  value       = aws_security_group.this.id
}