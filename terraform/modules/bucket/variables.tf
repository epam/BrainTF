variable "bucket_name" {
  description = "The name for a bucket"
  type        = string
}

variable "force_destroy" {
  description = "Whether to force destroy the bucket"
  type        = bool
  default     = true
}

variable "account_id" {
  description = "The AWS account ID where the infrastructure will be deployed"
  type        = string
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules for the S3 bucket"
  type = list(object({
    id                                     = string
    enabled                                = bool
    prefix                                 = optional(string)
    expiration_date                        = optional(string) # Date for expiration (RFC3339 format)
    expiration_days                        = optional(number) # Days for expiration
    expired_object_delete_marker           = optional(bool)   # Flag for delete marker expiration
    noncurrent_version_expiration_days     = optional(number) # Days for noncurrent version expiration
    abort_incomplete_multipart_upload_days = optional(number) # Days to abort incomplete multipart uploads
  }))
  default = []
  validation {
    condition = alltrue([
      for rule in var.lifecycle_rules : (
        rule.abort_incomplete_multipart_upload_days == null ||
        (rule.abort_incomplete_multipart_upload_days >= 1 && rule.abort_incomplete_multipart_upload_days <= 7)
      )
    ])
    error_message = "abort_incomplete_multipart_upload_days must be between 1 and 7 if set."
  }
}

variable "create_directories" {
  description = "Whether to create directories in the bucket"
  type        = bool
  default     = false
}

variable "directories" {
  description = "List of directories to create in the bucket"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key used for bucket encryption"
  type        = string
}
