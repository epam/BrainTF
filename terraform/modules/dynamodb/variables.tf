variable "name" {
  description = "The name of the DynamoDB table"
  type        = string
}

variable "hash_key" {
  description = "The primary key of the DynamoDB table"
  type        = string
}

variable "range_key" {
  description = "The range key of the DynamoDB table (optional)"
  type        = string
  default     = null
}

variable "attributes" {
  description = "Attributes for the DynamoDB table"
  type = list(object({
    name = string
    type = string
  }))
}

variable "billing_mode" {
  description = "The billing mode for the DynamoDB table"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "server_side_encryption_enabled" {
  description = "Whether server-side encryption is enabled"
  type        = bool
  default     = true
}

variable "server_side_encryption_kms_key_arn" {
  description = "KMS key ARN for server-side encryption"
  type        = string
}

variable "point_in_time_recovery_enabled" {
  description = "Whether point-in-time recovery is enabled"
  type        = bool
  default     = false
}

variable "ttl_attribute_name" {
  description = "The name of the TTL attribute"
  type        = string
  default     = null
}

variable "ttl_enabled" {
  description = "Whether TTL is enabled"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to the DynamoDB table"
  type        = map(string)
  default     = {}
}
