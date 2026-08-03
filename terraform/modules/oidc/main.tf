# Fetch thumbprint using an external script
data "external" "get_thumbprint" {
  program = ["bash", "${path.module}/get_thumbprint.sh", var.oidc_provider]
}

# Create the OIDC provider
resource "aws_iam_openid_connect_provider" "vcs_oidc_provider" {
  url             = "https://${var.oidc_provider}"
  client_id_list  = var.client_id_list
  thumbprint_list = [data.external.get_thumbprint.result.thumbprint]
  tags            = var.tags
}

# IAM AssumeRole policy for OIDC
data "aws_iam_policy_document" "vcs_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.vcs_oidc_provider.arn]
    }

    # 'aud' condition
    condition {
      test     = "StringEquals"
      variable = var.aud_variable
      values   = var.client_id_list
    }

    # 'sub' condition
    condition {
      test     = "StringLike"
      variable = var.sub_variable
      values   = var.sub_values
    }
  }
}

# Create IAM role for OIDC
resource "aws_iam_role" "vcs_oidc_role" {
  name               = var.oidc_role_name
  assume_role_policy = data.aws_iam_policy_document.vcs_assume_role_policy.json
  tags               = var.tags
}

# Define IAM policy for OIDC integration
data "aws_iam_policy_document" "oidc_policy" {

  statement {
    sid    = "ArtifactsBucketAccess"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "arn:aws:s3:::${var.artifacts_bucket}",
      "arn:aws:s3:::${var.artifacts_bucket}/*"
    ]
  }

  statement {
    sid    = "ManagedStateBucketAccess"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketVersioning",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:GetObjectVersion"
    ]
    resources = [
      "arn:aws:s3:::${var.managed_state_bucket}",
      "arn:aws:s3:::${var.managed_state_bucket}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    resources = [aws_iam_role.vcs_oidc_role.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:GenerateDataKey",
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:DescribeKey"
    ]
    resources = [var.kms_key_arn]
  }
}

# Create IAM policy for the OIDC role
resource "aws_iam_policy" "oidc_policy" {
  name        = var.oidc_policy_name
  description = "IAM policy for ${var.vcs_provider} OIDC integration"
  policy      = data.aws_iam_policy_document.oidc_policy.json
  tags        = var.tags
}

# Attach the IAM policy to the role
resource "aws_iam_role_policy_attachment" "vcs_oidc_policy_attachment" {
  role       = aws_iam_role.vcs_oidc_role.name
  policy_arn = aws_iam_policy.oidc_policy.arn
}
