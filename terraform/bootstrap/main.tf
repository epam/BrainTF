# ======================= Local Variables =======================
locals {
  # Define the S3 bucket name for storing the Terraform state
  state_bucket  = lower(replace(replace(replace("backend-state-bucket-${var.vcs_repo_name}-${var.region}", "_", "-"), " ", "-"), "[^a-z0-9.-]", ""))
  aws_kms_alias = "alias/kms_key_${var.vcs_repo_name}_${var.region}"

  # Define tags to apply to resources
  tags = {
    Project     = var.vcs_repo_name
    Environment = var.environment
    Team        = var.team
    DeployedBy  = var.deployed_by
    OwnerEmail  = var.owner_mail
  }
}

# ======================= Null Resource to Add or Overwrite Backend and Remote State =======================
resource "null_resource" "add_or_update_backend_and_remote_state" {
  triggers = {
    backend_config = <<EOT
#======================= The Main module for application infrastructure =======================#
terraform {
  backend \"s3\" {
    bucket         = \"${local.state_bucket}\"
    key            = \"terraform.tfstate\"
    region         = \"${var.region}\"
    encrypt        = \"true\"
    use_lockfile   = \"true\"
  }
}
data \"aws_kms_alias\" \"kms_key\" {
  name = \"${local.aws_kms_alias}\"
}
EOT
  }

  provisioner "local-exec" {
    # Append the backend configuration and remote state data to the top of the file
    command = <<EOT
if [ ! -f ../main_module/main.tf ]; then
  echo "Creating main.tf as it does not exist."
  touch ../main_module/main.tf
fi

if ! grep -q 'terraform {' ../main_module/main.tf; then
  echo "${self.triggers.backend_config}" | cat - ../main_module/main.tf > ../main_module/main.tf.tmp && mv ../main_module/main.tf.tmp ../main_module/main.tf
else
  echo "Backend configuration and remote state already exist in main.tf"
fi
EOT
  }
}

# ======================= Null Resource to Add or Update Outputs in outputs.tf =======================
resource "null_resource" "sync_tfvars" {
  triggers = {
    # Read the content of the source terraform.tfvars file
    source_file = file("${path.module}/terraform.tfvars")
  }

  provisioner "local-exec" {
    command     = <<EOT
#!/bin/bash
set -euo pipefail

# Define the destination file path
DEST_FILE="../main_module/terraform.tfvars"

# Ensure the destination file exists
if [ ! -f "$DEST_FILE" ]; then
  echo "Creating $DEST_FILE as it does not exist."
  touch "$DEST_FILE"
fi

# Read the content of the source file
SOURCE_CONTENT="${self.triggers.source_file}"

# Temporary files to store updated content
TEMP_FILE=$(mktemp)
PROCESSED_VARS_FILE=$(mktemp)
PROCESSED_COMMENTS_FILE=$(mktemp)

# Function to extract the exact formatting of a line
extract_formatting() {
  local line="$1"
  local var_name=$(echo "$line" | awk -F '=' '{print $1}' | sed 's/[[:space:]]*$//')
  local rest=$(echo "$line" | awk -F '=' '{print $2}')
  local var_value=$(echo "$rest" | awk -F '#' '{print $1}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  local comment=$(echo "$rest" | awk -F '#' '{if (NF > 1) print $2}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

  echo "$var_name" "$var_value" "$comment"
}

# Process each line in the source file
while IFS= read -r line; do
  # Check if the line is a comment
  if [[ "$line" =~ ^# ]]; then
    # Avoid duplicate comments
    if grep -Fxq "$line" "$PROCESSED_COMMENTS_FILE"; then
      continue
    fi
    echo "$line" >> "$PROCESSED_COMMENTS_FILE"
    echo "$line" >> "$TEMP_FILE"
    continue
  fi

  # Extract the variable name, value, and comment
  read -r VAR_NAME VAR_VALUE VAR_COMMENT <<< $(extract_formatting "$line")

  # Skip lines that don't look like valid variable assignments
  if [[ -z "$VAR_NAME" || -z "$VAR_VALUE" ]]; then
    echo "$line" >> "$TEMP_FILE" # Keep comments or empty lines intact
    continue
  fi

  # Wrap the value in quotes if necessary
  VAR_VALUE="\"$VAR_VALUE\""

  # Mark the variable as processed
  echo "$VAR_NAME" >> "$PROCESSED_VARS_FILE"

  # Add the variable and its comment to the temporary file
  if [[ -n "$VAR_COMMENT" ]]; then
    printf "%-24s = %-24s   # %s\n" "$VAR_NAME" "$VAR_VALUE" "$VAR_COMMENT" >> "$TEMP_FILE"
  else
    printf "%-24s = %-24s\n" "$VAR_NAME" "$VAR_VALUE" >> "$TEMP_FILE"
  fi
done <<< "$SOURCE_CONTENT"

# Process the destination file and merge with the source
while IFS= read -r line; do
  VAR_NAME=$(echo "$line" | awk -F '=' '{print $1}' | xargs)

  # If the variable was already processed, skip it
  if grep -Fxq "$VAR_NAME" "$PROCESSED_VARS_FILE"; then
    continue
  fi

  # If the comment was already processed, skip it
  if [[ "$line" =~ ^# ]] && grep -Fxq "$line" "$PROCESSED_COMMENTS_FILE"; then
    continue
  fi

  # Keep the variable or comment as is
  echo "$line" >> "$TEMP_FILE"
done < "$DEST_FILE"

# Remove trailing empty lines from the temporary file
awk 'NF || last {print} {last=NF}' "$TEMP_FILE" > "$TEMP_FILE.cleaned"
mv "$TEMP_FILE.cleaned" "$TEMP_FILE"

# Replace the destination file with the updated content
mv "$TEMP_FILE" "$DEST_FILE"

# Clean up temporary files
rm -f "$PROCESSED_VARS_FILE" "$PROCESSED_COMMENTS_FILE"

echo "File updated successfully: $DEST_FILE"
EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

# ======================= Null Resource for Selecting VCS Module =======================
resource "null_resource" "select_vcs_module" {
  triggers = {
    vcs_provider = var.vcs_provider
  }

  provisioner "local-exec" {
    command = <<EOT
if [ "${var.vcs_provider}" = "github" ]; then
  if [ -d "../vcs_integration_templates/github" ]; then
    rm -rf ../modules/vcs_integration && mkdir -p ../modules/vcs_integration && cp -r ../vcs_integration_templates/github/* ../modules/vcs_integration/
  else
    echo "Error: Directory ./vcs_integration_templates/github does not exist." >&2
    exit 1
  fi
else
  if [ -d "../vcs_integration_templates/gitlab" ]; then
    rm -rf ../modules/vcs_integration && mkdir -p ../modules/vcs_integration && cp -r ../vcs_integration_templates/gitlab/* ../modules/vcs_integration/
  else
    echo "Error: Directory ../vcs_integration_templates/gitlab does not exist." >&2
    exit 1
  fi
fi
EOT
  }
}

# ======================= Create a KMS Key for Encryption =======================
data "aws_caller_identity" "current" {}

module "s3_bucket_kms_key" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-kms.git?ref=407e3db34a65b384c20ef718f55d9ceacb97a846"

  description              = "KMS key for encrypting resources"
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
    },
    {
      sid = "AllowTerraformRoleAccess"
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:ListAliases",
        "kms:ListKeys",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ]
      effect = "Allow"
      principals = [
        {
          type        = "AWS"
          identifiers = [data.aws_caller_identity.current.arn]
        }
      ]
    }
  ]

  tags = local.tags
}

# ======================= Create an S3 Bucket for Terraform State =======================
module "s3_state_bucket" {
  source                                = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=6c5e082b5d2fde77cb59c387a7f553dd2ed5da29"
  create_bucket                         = true
  bucket                                = local.state_bucket
  force_destroy                         = true
  attach_policy                         = true
  block_public_acls                     = true
  block_public_policy                   = true
  ignore_public_acls                    = true
  restrict_public_buckets               = true
  attach_deny_insecure_transport_policy = true

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
        Sid    = "AllowRootAccountAccess",
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:PutObjectAcl",
          "s3:GetObjectAcl",
          "s3:DeleteObjectVersion",
          "s3:ListBucketVersions",
          "s3:ListBucketMultipartUploads",
          "s3:AbortMultipartUpload"
        ],
        Resource = [
          module.s3_state_bucket.s3_bucket_arn,
          "${module.s3_state_bucket.s3_bucket_arn}/*"
        ],
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        }
      },
      {
        Sid    = "AllowRoleAccess",
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = [
          module.s3_state_bucket.s3_bucket_arn,
          "${module.s3_state_bucket.s3_bucket_arn}/*"
        ],
        Principal = {
          AWS = data.aws_caller_identity.current.arn
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

  tags = {
    Name = "TerraformRole"
  }
}
