provider "github" {
  # Only meaningful when vcs_provider == "github"
  token = var.vcs_provider == "github" ? var.vcs_token : null
  owner = var.vcs_provider == "github" ? local.git_owner : null
}

provider "gitlab" {
  # Only meaningful when vcs_provider == "gitlab"
  token            = var.vcs_provider == "gitlab" ? var.vcs_token : "null"
  base_url         = var.vcs_provider == "gitlab" ? local.vcs_api_endpoint : null
  early_auth_check = var.vcs_provider == "gitlab" ? true : false
}

data "aws_kms_alias" "kms_key" {
  name = "alias/kms_key_${var.vcs_repo_name}_${var.region}"
}

locals {

  tags = {
    Project     = var.vcs_repo_name
    Environment = var.environment
    Team        = var.team
    DeployedBy  = var.deployed_by
    OwnerEmail  = var.owner_mail
  }

  # Compute bootstrap state bucket name (same formula as in bootstrap/main.tf)
  bootstrap_state_bucket = lower(replace(replace(replace("${var.platform_state_bucket_prefix}-${var.vcs_repo_name}-${var.region}", "_", "-"), " ", "-"), "[^a-z0-9.-]", ""))

  # Use user-provided bucket if set, otherwise fall back to the bootstrap state bucket
  managed_state_bucket = var.managed_state_bucket != "" ? var.managed_state_bucket : local.bootstrap_state_bucket

  # Conditional variables
  oidc_role_name         = "${var.vcs_repo_name}-oidc-${var.vcs_provider}-${var.region}-role"
  oidc_policy_name       = "${var.vcs_repo_name}-oidc-${var.vcs_provider}-${var.region}-policy"
  artifacts_bucket       = lower(replace(replace(replace("${var.artifacts_bucket_prefix}-${var.vcs_repo_name}-${var.region}", "_", "-"), " ", "-"), "[^a-z0-9.-]", ""))
  ai_dynamodb_table_name = "ai-chat-history-${var.vcs_repo_name}-${var.region}"
  webhook_secret_name    = "/${var.vcs_repo_name}/webhook_secret"
  ai_api_token_name      = "/${var.vcs_repo_name}/ai_token"
  vcs_token_name         = "/${var.vcs_repo_name}/vcs_token"
  vcs_api_endpoint       = (var.vcs_provider == "github" ? "https://api.${var.vcs_hostname}" : "https://${var.vcs_hostname}")
  aud_variable           = "${var.oidc_provider}:aud"
  sub_variable           = "${var.oidc_provider}:sub"
  sub_values             = (var.vcs_provider == "github" ? ["repo:${var.vcs_project_path}:*"] : ["project_path:${var.vcs_project_path}:ref_type:branch:ref:*"])
  client_id_list         = (var.vcs_provider == "github" ? ["sts.amazonaws.com"] : ["https://${var.oidc_provider}"])
  terraform_backend_params = join(" ", [
    "-backend-config=bucket=${local.managed_state_bucket}",
    "-backend-config=key=${var.managed_state_key}",
    "-backend-config=region=${var.region}",
    "-backend-config=kms_key_id=${data.aws_kms_alias.kms_key.arn}",
    "-backend-config=encrypt=true",
    "-backend-config=use_lockfile=true"
  ])

  # VCS variables for GitHub or GitLab
  git_owner = regex("^([^/]+)", var.vcs_project_path)[0]
  vcs_variables = concat(
    var.ai_handler_create ? [
      {
        key         = "ARTIFACTS_BUCKET"
        value       = "${local.artifacts_bucket}/logs"
        description = "Artifacts S3 bucket (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "OIDC_ROLE_ARN"
        value       = module.oidc[0].oidc_role_arn
        description = "OIDC role ARN (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "OIDC_AUDIENCE"
        value       = local.client_id_list[0]
        description = "OIDC token audience (aud claim) for AWS STS validation (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "VCS_PROVIDER"
        value       = var.vcs_provider
        description = "The VCS provider (e.g., github, gitlab) (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "AWS_REGION"
        value       = var.region
        description = "AWS region (Managed by Terraform)"
        masked      = false
        protected   = false
      },
    ] : [],
    [
      {
        key         = "VCS_API_ENDPOINT"
        value       = var.vcs_provider == "gitlab" ? "${local.vcs_api_endpoint}/api/v4" : local.vcs_api_endpoint
        description = "VCS API endpoint (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "JOB_TOKEN"
        value       = var.job_token
        description = "VCS Notes token (Managed by Terraform)"
        masked      = true
        protected   = false
      },
      {
        key         = "AI_HANDLER_CREATE"
        value       = var.ai_handler_create
        description = "The AI Handler creation switch (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TFLINT_ANALYSIS"
        value       = var.run_tflint_analysis
        description = "Enable or disable the TFLint analysis stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TERRAFORM_VALIDATE"
        value       = var.run_terraform_validate
        description = "Enable or disable the Terraform validate stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_CHECKOV_ANALYSIS"
        value       = var.run_checkov_analysis
        description = "Enable or disable the Checkov analysis stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TFSEC_ANALYSIS"
        value       = var.run_tfsec_analysis
        description = "Enable or disable the TFSec analysis stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TRIVY_ANALYSIS"
        value       = var.run_trivy_analysis
        description = "Enable or disable the Trivy analysis stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TERRAFORM_PLAN"
        value       = var.run_terraform_plan
        description = "Enable or disable the Terraform plan stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "RUN_TERRAFORM_APPLY"
        value       = var.run_terraform_apply
        description = "Enable or disable the Terraform apply stage (Managed by Terraform)"
        masked      = false
        protected   = false
      },
      {
        key         = "TERRAFORM_BACKEND_PARAMS"
        value       = local.terraform_backend_params
        description = "Backend configuration parameters for Terraform"
        masked      = false
        protected   = false
      }
    ]
  )
  # Parameter Strings
  ssm_parameters = var.ai_handler_create ? {
    "vcs_token_parameter" = {
      name             = local.vcs_token_name
      type             = "SecureString"
      value            = var.vcs_token
      value_wo_version = parseint(substr(sha256(var.vcs_token), 0, 8), 16)
      tier             = "Standard"
      description      = "VCS Access Token (Managed by Terraform)"
      tags             = local.tags
    }
    "ai_token_parameter" = {
      name             = local.ai_api_token_name
      type             = "SecureString"
      value            = var.ai_token
      value_wo_version = parseint(substr(sha256(var.ai_token), 0, 8), 16)
      tier             = "Standard"
      description      = "AI Access Token (Managed by Terraform)"
      tags             = local.tags
    }
    "webhook_secret_parameter" = {
      name             = local.webhook_secret_name
      type             = "SecureString"
      value            = random_password.lambda_webhook_secret[0].result
      value_wo_version = null
      tier             = "Standard"
      description      = "Webhook secret for AI Handler (Managed by Terraform)"
      tags             = local.tags
    }
  } : {}
}

# ======================= Generate Webhook Secret =======================
resource "random_password" "lambda_webhook_secret" {
  count   = var.ai_handler_create ? 1 : 0
  length  = 32
  special = false
}

# ======================= Artifacts Bucket =======================
module "artifacts_bucket" {
  source        = "../modules/bucket"
  count         = var.ai_handler_create ? 1 : 0
  bucket_name   = local.artifacts_bucket
  kms_key_arn   = data.aws_kms_alias.kms_key.target_key_arn
  force_destroy = true
  lifecycle_rules = [
    {
      id                                     = "artifacts-retention"
      enabled                                = true
      prefix                                 = "artifacts/*"
      expiration_date                        = null # Date for expiration (RFC3339 format)
      expiration_days                        = 3    # Days for expiration
      expired_object_delete_marker           = null # Flag for delete marker expiration
      noncurrent_version_expiration_days     = 1    # Days for noncurrent version expiration
      abort_incomplete_multipart_upload_days = 7    # Days to abort incomplete multipart uploads
    }
  ]
  account_id         = var.account_id
  tags               = local.tags
  create_directories = true # Create directories
  directories        = ["logs/", "artifacts/"]
}

# ======================= SSM Parameters =======================
module "ssm_parameters" {
  source           = "git::https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter.git?ref=c0456aa1960c2b13080f3968be9a7cdc687f2c8c"
  for_each         = local.ssm_parameters
  name             = try(each.value.name, each.key)
  value            = try(each.value.value, null)
  value_wo_version = try(each.value.value_wo_version, null)
  type             = try(each.value.type, null)
  description      = try(each.value.description, null)
  tier             = try(each.value.tier, null)
}

# ======================= OIDC Provider =======================
module "oidc" {
  source               = "../modules/oidc"
  count                = var.ai_handler_create ? 1 : 0
  vcs_provider         = var.vcs_provider
  oidc_role_name       = local.oidc_role_name
  oidc_policy_name     = local.oidc_policy_name
  oidc_provider        = var.oidc_provider
  artifacts_bucket     = local.artifacts_bucket
  managed_state_bucket = local.managed_state_bucket
  kms_key_arn          = data.aws_kms_alias.kms_key.target_key_arn
  client_id_list       = local.client_id_list
  aud_variable         = local.aud_variable
  sub_values           = local.sub_values
  sub_variable         = local.sub_variable
  tags                 = local.tags
}

# ======================= IAM Roles and Policies for Lambda =======================
module "iam" {
  source            = "../modules/iam"
  count             = var.ai_handler_create ? 1 : 0
  region            = var.region
  account_id        = var.account_id
  artifacts_bucket  = local.artifacts_bucket
  ai_handler_create = var.ai_handler_create
  kms_key_arn       = data.aws_kms_alias.kms_key.target_key_arn
  tags              = local.tags
  vcs_repo_name     = var.vcs_repo_name
}

# ======================= DynamoDB tables =======================
module "ai_dynamodb_table" {
  source    = "../modules/dynamodb"
  count     = var.ai_handler_create ? 1 : 0
  name      = local.ai_dynamodb_table_name
  hash_key  = "pk"
  range_key = "sk"
  attributes = [
    {
      name = "pk"
      type = "S"
    },
    {
      name = "sk"
      type = "N"
    }
  ]
  billing_mode                       = "PAY_PER_REQUEST"
  server_side_encryption_kms_key_arn = data.aws_kms_alias.kms_key.target_key_arn
  server_side_encryption_enabled     = true
  point_in_time_recovery_enabled     = false
  ttl_attribute_name                 = "ttl"
  ttl_enabled                        = true
  tags                               = local.tags
}

# ======================= AI Handler Lambda Functions =======================
module "ai_lambda" {
  source               = "../modules/lambdas"
  count                = var.ai_handler_create ? 1 : 0
  vcs_repo_name        = var.vcs_repo_name
  vcs_provider         = var.vcs_provider
  artifacts_bucket     = local.artifacts_bucket
  vcs_token_name       = local.vcs_token_name
  private_subnet_ids   = var.private_subnet_ids
  security_groups      = var.security_groups
  lambda_exec_role_arn = try(module.iam[0].lambda_exec_role_arn, null)
  ai_handler_create    = var.ai_handler_create
  rag_enable           = var.rag_enable
  ai_api_endpoint      = var.ai_api_endpoint
  ai_api_token_name    = local.ai_api_token_name
  vcs_api_endpoint     = local.vcs_api_endpoint
  llm_model            = var.llm_model
  webhook_secret_name  = local.webhook_secret_name
  kms_key_arn          = data.aws_kms_alias.kms_key.target_key_arn
  dynamodb_table_name  = local.ai_dynamodb_table_name
  log_level            = var.log_level
  artifacts_path       = var.artifacts_path
  tags                 = local.tags
}

# ======================= VCS Integration =======================
module "vcs_integration_github" {
  count             = var.vcs_provider == "github" ? 1 : 0
  source            = "../modules/vcs_integration/github"
  vcs_project_path  = var.vcs_project_path
  vcs_variables     = local.vcs_variables
  webhook_secret    = try(random_password.lambda_webhook_secret[0].result, null)
  function_url      = try(module.ai_lambda[0].function_url, null)
  ai_handler_create = var.ai_handler_create
}
module "vcs_integration_gitlab" {
  count             = var.vcs_provider == "gitlab" ? 1 : 0
  source            = "../modules/vcs_integration/gitlab"
  vcs_project_path  = var.vcs_project_path
  vcs_variables     = local.vcs_variables
  webhook_secret    = try(random_password.lambda_webhook_secret[0].result, null)
  function_url      = try(module.ai_lambda[0].function_url, null)
  ai_handler_create = var.ai_handler_create
}
