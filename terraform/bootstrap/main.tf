# ======================= Local Variables =======================
locals {
  # Define the S3 bucket name for storing the platform Terraform state
  state_bucket = lower(replace(replace(replace("${var.platform_state_bucket_prefix}-${var.vcs_repo_name}-${var.region}", "_", "-"), " ", "-"), "[^a-z0-9.-]", ""))

  # list of .tf files in the main module to check for existing backend blocks
  main_module_tf_files = fileset("${path.module}/../main_module", "*.tf")
  # Find any existing backend blocks in the main module using regular expressions
  existing_backend_files = [
    for tf_file in local.main_module_tf_files : tf_file
    if length(regexall("(?s)terraform\\s*\\{.*?backend\\s*\"[^\"]+\"\\s*\\{", file("${path.module}/../main_module/${tf_file}"))) > 0
  ]

  # Generate the backend configuration content for the main_module
  backend_config = <<EOT
#======================= The Main module for application infrastructure =======================#
terraform {
  backend "s3" {
    bucket       = "${local.state_bucket}"
    key          = "main-module/terraform.tfstate"
    region       = "${var.region}"
    encrypt      = true
    use_lockfile = true
  }
}
EOT

  # Define tags to apply to resources
  tags = {
    Project     = var.vcs_repo_name
    Environment = var.environment
    Team        = var.team
    DeployedBy  = var.deployed_by
    OwnerEmail  = var.owner_mail
  }
}

# ======================= Generate Backend Configuration for Main Module =======================
resource "local_file" "backend_config" {
  # Skip silently if a backend block already exists in any file other than the generated one
  count = (
    length(local.existing_backend_files) == 0 ||
    (length(local.existing_backend_files) == 1 && contains(local.existing_backend_files, "backend.generated.tf"))
  ) ? 1 : 0

  content  = local.backend_config
  filename = "${path.module}/../main_module/backend.generated.tf"
}

# ======================= Sync terraform.tfvars =======================
data "local_file" "this" {
  filename = "${path.module}/terraform.tfvars"
}

resource "local_file" "this" {
  content  = data.local_file.this.content
  filename = "${path.module}/../main_module/terraform.auto.tfvars"
}

# ======================= Create a KMS Key for Encryption =======================

module "s3_bucket_kms_key" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-kms.git?ref=407e3db34a65b384c20ef718f55d9ceacb97a846"

  description              = "KMS key for encrypting Terraform state and related resources"
  enable_key_rotation      = true
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  deletion_window_in_days  = 7

  key_owners = [
    "arn:aws:iam::${var.account_id}:root"
  ]

  computed_aliases = {
    project_alias = {
      name = "kms_key_${var.vcs_repo_name}_${var.region}"
    }
  }

  key_statements = [
    {
      sid = "AllowRootAccountAccess"
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant",
        "kms:ListAliases",
        "kms:ListKeys",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ]
      effect    = "Allow"
      resources = ["*"]
      principals = [
        {
          type        = "AWS"
          identifiers = ["arn:aws:iam::${var.account_id}:root"]
        }
      ]
    }
  ]

  tags = local.tags
}

# ======================= Create an S3 Bucket for Terraform State =======================
module "s3_state_bucket" {
  source                  = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=6c5e082b5d2fde77cb59c387a7f553dd2ed5da29"
  create_bucket           = true
  bucket                  = local.state_bucket
  force_destroy           = true
  attach_policy           = false
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
        kms_master_key_id = module.s3_bucket_kms_key.key_arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  tags = local.tags
}

# ======================= Attach a Bucket Policy =======================
resource "aws_s3_bucket_policy" "state_bucket_policy" {
  bucket = module.s3_state_bucket.s3_bucket_id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "DenyInsecureTransport",
        Effect    = "Deny",
        Action    = "s3:*",
        Principal = "*",
        Resource = [
          module.s3_state_bucket.s3_bucket_arn,
          "${module.s3_state_bucket.s3_bucket_arn}/*"
        ],
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# ======================= Create IAM Role =======================
resource "aws_iam_role" "terraform_role" {
  name = "Terraform-role-${var.vcs_repo_name}-${var.region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.tags
}

# ======================= IAM Policy for Terraform Role - State Access =======================
resource "aws_iam_role_policy" "terraform_state_access" {
  name = "Terraform-State-Access-${var.vcs_repo_name}-${var.region}"
  role = aws_iam_role.terraform_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "S3StateAccess",
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:ListBucketVersions",
          # Object-level actions
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion",
        ],
        Resource = [
          module.s3_state_bucket.s3_bucket_arn,
          "${module.s3_state_bucket.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}
