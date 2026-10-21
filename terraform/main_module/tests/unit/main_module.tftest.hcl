# Unit tests for the main_module root logic: input validation, feature toggles, resource
# naming and the CI variables handed to the VCS. No AWS or GitHub access, nothing is created.
#
# Run from terraform/main_module:
#   terraform init -backend=false -test-directory=tests/unit
#   terraform test -test-directory=tests/unit
#
# Child modules oidc and ai_lambda are replaced with override_module: they are tested in
# their own directories, and replacing them keeps their external/null providers out of the
# run. A mock_provider only replaces providers declared in this root module; without the
# override, get_thumbprint.sh opens a real TLS connection and the Lambda packaging runs docker.
#
# The last section holds open findings: runs that describe what the code should do and
# fail until the code is fixed. Keep it at the end of the file: a run that ends in an error
# (such as a missing expected failure) makes Terraform skip every run after it.

mock_provider "aws" {
  source = "../tests/mocks/aws"
}

mock_provider "random" {}
mock_provider "github" {}
mock_provider "gitlab" {}

override_module {
  target = module.oidc
  outputs = {
    oidc_role_arn = "arn:aws:iam::123456789012:role/terraform-test-oidc-role"
  }
}

override_module {
  target = module.ai_lambda
  outputs = {
    function_url = "https://terraform-test.lambda-url.eu-west-1.on.aws/"
  }
}

# Inputs of the module under test. Every variable is set here on purpose: terraform test
# also loads terraform.tfvars and *.auto.tfvars from this directory (locally that includes
# secrets.auto.tfvars), and values from the test file take precedence, so local runs behave
# the same as CI where those files do not exist.
variables {
  vcs_hostname            = "github.com"
  vcs_repo_name           = "BrainTF"
  environment             = "test"
  team                    = "test"
  deployed_by             = "terraform-test"
  owner_mail              = "test@example.com"
  vcs_token               = "test-vcs-token"
  ai_token                = "test-ai-token"
  vcs_provider            = "github"
  vcs_project_path        = "epmc-poc/BrainTF"
  artifacts_bucket_prefix = "artifacts"
  llm_model               = "test-model"
  ai_temperature          = 0.2
  ai_api_base_url         = "https://llm.example.com/v1"
  private_subnet_ids      = ["subnet-00000000000000001"]
  security_groups         = ["sg-00000000000000001"]
  job_token               = "test-job-token"
  oidc_provider           = "token.actions.githubusercontent.com"
  ai_handler_create       = true

  # CI variables that only exist when the AI handler is enabled; used by several runs.
  ai_handler_ci_variables = ["ARTIFACTS_BUCKET", "OIDC_ROLE_ARN", "OIDC_AUDIENCE", "VCS_PROVIDER", "AWS_REGION"]
}

# ======================= Feature toggles =======================

run "ai_handler_disabled_creates_only_vcs_integration" {
  command = plan

  variables {
    ai_handler_create = false
  }

  assert {
    condition = alltrue([
      length(module.artifacts_bucket) == 0,
      length(module.oidc) == 0,
      length(module.iam) == 0,
      length(module.ai_dynamodb_table) == 0,
      length(module.ai_lambda) == 0,
      length(random_password.lambda_webhook_secret) == 0,
      length(local.ssm_parameters) == 0,
    ])
    error_message = "No AI handler resources may be planned when ai_handler_create = false."
  }

  assert {
    condition     = length(module.vcs_integration_github) == 1 && length(module.vcs_integration_gitlab) == 0
    error_message = "The GitHub integration must still be created, and only it."
  }

  assert {
    condition     = length(setintersection([for v in local.vcs_variables : v.key], var.ai_handler_ci_variables)) == 0
    error_message = "AI handler CI variables must not be published when the AI handler is disabled."
  }
}

run "ai_handler_enabled_creates_ai_stack" {
  command = plan

  assert {
    condition = alltrue([
      length(module.artifacts_bucket) == 1,
      length(module.oidc) == 1,
      length(module.iam) == 1,
      length(module.ai_dynamodb_table) == 1,
      length(module.ai_lambda) == 1,
      length(random_password.lambda_webhook_secret) == 1,
    ])
    error_message = "Every AI handler component must be planned when ai_handler_create = true."
  }

  assert {
    condition     = toset(var.ai_handler_ci_variables) == setintersection([for v in local.vcs_variables : v.key], var.ai_handler_ci_variables)
    error_message = "Every AI handler CI variable must be published when the AI handler is enabled."
  }

  assert {
    condition     = toset(keys(local.ssm_parameters)) == toset(["vcs_token_parameter", "ai_token_parameter", "webhook_secret_parameter"])
    error_message = "Expected exactly the VCS token, AI token and webhook secret SSM parameters."
  }

  assert {
    condition     = alltrue([for p in values(local.ssm_parameters) : p.type == "SecureString"])
    error_message = "All SSM parameters hold secrets and must be SecureString."
  }
}

# ======================= Naming =======================
# Only names that something outside main_module depends on: the bucket names (bootstrap computes
# the state bucket name on its own) and the SSM parameter names the Lambdas read.

run "shared_resource_names_follow_convention" {
  command = plan

  assert {
    condition     = local.artifacts_bucket == "${var.artifacts_bucket_prefix}-${lower(var.vcs_repo_name)}-${data.aws_region.current.region}"
    error_message = "Artifacts bucket must be <prefix>-<repo in lowercase>-<region>, got ${local.artifacts_bucket}"
  }

  assert {
    condition     = local.bootstrap_state_bucket == "${var.platform_state_bucket_prefix}-${lower(var.vcs_repo_name)}-${data.aws_region.current.region}"
    error_message = "main_module must compute the same state bucket name as bootstrap, got ${local.bootstrap_state_bucket}"
  }

  assert {
    condition = alltrue([
      local.ssm_parameters["vcs_token_parameter"].name == "/${var.vcs_repo_name}/vcs_token",
      local.ssm_parameters["ai_token_parameter"].name == "/${var.vcs_repo_name}/ai_token",
      local.ssm_parameters["webhook_secret_parameter"].name == "/${var.vcs_repo_name}/webhook_secret",
    ])
    error_message = "SSM parameter names must be /<repo>/<name>; the Lambdas read them by these names."
  }
}

# ======================= CI variables handed to the VCS =======================

run "only_job_token_is_secret" {
  command = plan

  assert {
    condition     = [for v in local.vcs_variables : v.key if v.masked] == ["JOB_TOKEN"]
    error_message = "Only JOB_TOKEN may be stored as a GitHub secret; every other value is a plain variable."
  }
}

run "ci_variables_point_to_this_deployment" {
  command = plan

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["ARTIFACTS_BUCKET"] == "${local.artifacts_bucket}/logs"
    error_message = "ARTIFACTS_BUCKET must point to the logs/ prefix of the artifacts bucket (the Lambda trigger listens there)."
  }

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["OIDC_ROLE_ARN"] == module.oidc[0].oidc_role_arn
    error_message = "OIDC_ROLE_ARN must come from the oidc module output."
  }

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["VCS_API_ENDPOINT"] == "https://api.${var.vcs_hostname}"
    error_message = "GitHub API endpoint must be https://api.<vcs_hostname>."
  }

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["OIDC_AUDIENCE"] == "sts.amazonaws.com"
    error_message = "GitHub OIDC audience must be sts.amazonaws.com."
  }

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["AWS_REGION"] == data.aws_region.current.region
    error_message = "AWS_REGION must be the region main_module is deployed to."
  }
}

run "backend_params_use_bootstrap_bucket_by_default" {
  command = plan

  assert {
    condition = local.terraform_backend_params == join(" ", [
      "-backend-config=bucket=${local.bootstrap_state_bucket}",
      "-backend-config=key=${var.managed_state_key}",
      "-backend-config=region=${data.aws_region.current.region}",
      "-backend-config=kms_key_id=${data.aws_kms_alias.kms_key.arn}",
      "-backend-config=encrypt=true",
      "-backend-config=use_lockfile=true",
    ])
    error_message = "Unexpected TERRAFORM_BACKEND_PARAMS: ${local.terraform_backend_params}"
  }
}

run "backend_params_use_managed_bucket_when_set" {
  command = plan

  variables {
    managed_state_bucket = "team-owned-state"
    managed_state_key    = "workloads/demo.tfstate"
  }

  assert {
    condition = alltrue([
      strcontains(local.terraform_backend_params, "-backend-config=bucket=${var.managed_state_bucket} "),
      strcontains(local.terraform_backend_params, "-backend-config=key=${var.managed_state_key} "),
    ])
    error_message = "managed_state_bucket and managed_state_key must override the defaults: ${local.terraform_backend_params}"
  }
}

# ======================= OIDC trust scope =======================

run "github_oidc_trust_limited_to_main_and_pull_requests" {
  command = plan

  assert {
    condition = local.sub_values == tolist([
      "repo:${var.vcs_project_path}:ref:refs/heads/main",
      "repo:${var.vcs_project_path}:pull_request",
      "repo:${split("/", var.vcs_project_path)[0]}@*/${split("/", var.vcs_project_path)[1]}@*:ref:refs/heads/main",
      "repo:${split("/", var.vcs_project_path)[0]}@*/${split("/", var.vcs_project_path)[1]}@*:pull_request",
    ])
    error_message = "The pipeline role may only be assumed from main pushes and pull requests of this repository: ${jsonencode(local.sub_values)}"
  }
}

run "gitlab_uses_gitlab_integration_and_claims" {
  command = plan

  variables {
    vcs_provider     = "gitlab"
    vcs_hostname     = "gitlab.com"
    vcs_project_path = "epmc-poc/braintf"
    oidc_provider    = "gitlab.com"
  }

  assert {
    condition     = length(module.vcs_integration_gitlab) == 1 && length(module.vcs_integration_github) == 0
    error_message = "Only the GitLab integration may be created for vcs_provider = gitlab."
  }

  assert {
    condition     = local.sub_values == tolist(["project_path:${var.vcs_project_path}:ref_type:branch:ref:*"])
    error_message = "Unexpected GitLab sub claim: ${jsonencode(local.sub_values)}"
  }

  assert {
    condition     = tolist(local.client_id_list) == tolist(["https://${var.oidc_provider}"])
    error_message = "GitLab OIDC audience must be the issuer URL."
  }

  assert {
    condition     = { for v in local.vcs_variables : v.key => v.value }["VCS_API_ENDPOINT"] == "https://${var.vcs_hostname}/api/v4"
    error_message = "GitLab API endpoint must be https://<vcs_hostname>/api/v4."
  }
}

# ======================= Input validation =======================

run "rejects_unknown_vcs_provider" {
  command = plan

  variables {
    vcs_provider = "bitbucket"
  }

  expect_failures = [var.vcs_provider]
}

run "rejects_unknown_log_level" {
  command = plan

  variables {
    log_level = "TRACE"
  }

  expect_failures = [var.log_level]
}

run "rejects_temperature_above_two" {
  command = plan

  variables {
    ai_temperature = 2.5
  }

  expect_failures = [var.ai_temperature]
}

run "rejects_state_key_without_directory" {
  command = plan

  variables {
    managed_state_key = "terraform.tfstate"
  }

  expect_failures = [var.managed_state_key]
}

run "rejects_state_key_with_leading_slash" {
  command = plan

  variables {
    managed_state_key = "/pipeline/terraform.tfstate"
  }

  expect_failures = [var.managed_state_key]
}

# ======================= Open findings: these runs fail until the code is fixed =======================

# local.artifacts_bucket is meant to keep only characters S3 allows, but
# replace(…, "[^a-z0-9.-]", "") matches that text literally; a regular expression needs
# slashes: "/[^a-z0-9.-]/". The repo name uses "/": the KMS alias lookup in this module
# accepts it, S3 does not. The modules that create resources from the name are replaced,
# so their own name checks do not hide what main_module computes.
run "finding_artifacts_bucket_name_keeps_only_s3_characters" {
  command = plan

  variables {
    vcs_repo_name = "Brain/TF"
  }

  override_module {
    target = module.artifacts_bucket
  }

  override_module {
    target = module.iam
  }

  override_module {
    target = module.ai_dynamodb_table
  }

  override_module {
    target = module.ssm_parameters
  }

  assert {
    condition     = can(regex("^[a-z0-9.-]+$", local.artifacts_bucket))
    error_message = "The artifacts bucket name must contain only a-z, 0-9, '.' and '-', got ${local.artifacts_bucket}"
  }
}

# vcs_repo_name has no validation. A 36-character name passes, and names built from it are
# then longer than AWS allows (for example the Lambda IAM role
# Terraform-AI-Handler-Role-<repo>-<region>, limit 64); today the user only finds out from
# the AWS provider. Expected: var.vcs_repo_name rejects it.
run "finding_repo_name_too_long_is_rejected" {
  command = plan

  variables {
    vcs_repo_name = "braintf-repository-name-is-too-long1"
  }

  override_module {
    target = module.iam
  }

  expect_failures = [var.vcs_repo_name]
}
