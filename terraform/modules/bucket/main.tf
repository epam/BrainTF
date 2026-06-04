# ======================= Create S3 Bucket =======================
module "s3_bucket" {
  source                  = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=2dd4364b67d89cb9c881be465e5e4196ef8dea8f"
  bucket                  = var.bucket_name
  force_destroy           = var.force_destroy
  attach_policy           = false # Bucket policy will be added manually
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  versioning = {
    enabled = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = var.kms_key_arn
        sse_algorithm     = "aws:kms"
      }

      bucket_key_enabled = true
    }
  }

  tags = var.tags
}

# ======================= Create Lifecycle Rules =======================
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  count  = length(var.lifecycle_rules) > 0 ? 1 : 0
  bucket = var.bucket_name

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.enabled ? "Enabled" : "Disabled"
      filter {
        prefix = try(rule.value.prefix, null)
      }

      # Expiration block (only one set)
      dynamic "expiration" {
        for_each = (
          rule.value.expiration_date != null ? [rule.value] :
          rule.value.expiration_days != null ? [rule.value] :
          rule.value.expired_object_delete_marker != null ? [rule.value] : []
        )
        content {
          date                         = try(rule.value.expiration_date, null)
          days                         = try(rule.value.expiration_days, null)
          expired_object_delete_marker = try(rule.value.expired_object_delete_marker, null)
        }
      }

      # Noncurrent version expiration
      dynamic "noncurrent_version_expiration" {
        for_each = rule.value.noncurrent_version_expiration_days != null ? [rule.value] : []
        content {
          noncurrent_days = try(rule.value.noncurrent_version_expiration_days, null)
        }
      }

      # Ensure abort_incomplete_multipart_upload block is present and days set to 7 or less
      abort_incomplete_multipart_upload {
        days_after_initiation = coalesce(
          try(rule.value.abort_incomplete_multipart_upload_days, null),
          7
        )
      }
    }
    #checkov:skip=CKV_AWS_300: Ensure S3 lifecycle configuration sets period for aborting failed uploads; false positive
  }
}

# ======================= Generate Custom IAM Policy =======================
data "aws_iam_policy_document" "s3_bucket_policy" {
  statement {
    sid     = "denyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${var.bucket_name}",
      "arn:aws:s3:::${var.bucket_name}/*"
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
  statement {
    sid    = "ForAccountsRoles"
    effect = "Allow"
    principals {
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
      type        = "AWS"
    }
    actions = [
      "s3:PutObjectRetention",
      "s3:BypassGovernanceRetention",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::${var.bucket_name}",
      "arn:aws:s3:::${var.bucket_name}/*"
    ]
  }
}

# ======================= Attach Custom IAM Policy =======================
resource "aws_s3_bucket_policy" "custom_policy" {
  bucket = module.s3_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.s3_bucket_policy.json
}

# ======================= Create Directories in S3 Bucket =======================
resource "aws_s3_object" "directory" {
  count   = var.create_directories && length(var.directories) > 0 ? length(var.directories) : 0
  bucket  = module.s3_bucket.s3_bucket_id
  key     = var.directories[count.index]
  content = ""
  tags    = var.tags
}
