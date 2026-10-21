# Unit tests for bootstrap: state bucket naming, the backend file it generates for
# main_module and the tfvars it copies there. No AWS access, nothing is created.
#
# Run from terraform/bootstrap:
#   terraform init -backend=false -test-directory=tests/unit
#   terraform test -test-directory=tests/unit
#
# The local provider is mocked, so even `command = apply` writes no files into
# ../main_module. fileset()/file() still read the real ../main_module/*.tf, which is what
# decides whether the backend file is generated.
#
# The last section holds open findings: runs that describe what the code should do and
# fail until the code is fixed. Keep it at the end of the file: a run that ends in an error
# (such as a missing expected failure) makes Terraform skip every run after it.

mock_provider "aws" {
  source = "../tests/mocks/aws"
}

mock_provider "local" {
  # Content of terraform.tfvars as bootstrap reads it through data.local_file.this.
  mock_data "local_file" {
    defaults = {
      content = "vcs_repo_name = \"BrainTF\"\n"
    }
  }
}

# The upstream terraform-aws-modules (KMS key, S3 bucket) are black boxes here: these tests
# check bootstrap's own logic, not the modules. Overriding them also keeps their own name
# checks from hiding what bootstrap computes. Override values cannot use variables.
override_module {
  target = module.s3_bucket_kms_key
  outputs = {
    key_arn = "arn:aws:kms:eu-west-1:123456789012:key/00000000-0000-0000-0000-000000000000"
  }
}

override_module {
  target = module.s3_state_bucket
  outputs = {
    s3_bucket_id  = "terraform-test-state-bucket"
    s3_bucket_arn = "arn:aws:s3:::terraform-test-state-bucket"
  }
}

# Inputs of the module under test. Every variable is set here: terraform test also loads
# terraform.tfvars from this directory, and values from the test file take precedence,
# so local runs behave the same as CI.
variables {
  vcs_repo_name = "BrainTF"
  environment   = "test"
  team          = "test"
  deployed_by   = "terraform-test"
  owner_mail    = "test@example.com"

  # Values of the main_module backend contract, used by several runs below.
  main_module_dir       = "../main_module"
  main_module_state_key = "main-module/terraform.tfstate"
}

# ======================= Naming =======================

run "state_bucket_name_is_lowercase_and_regional" {
  command = plan

  assert {
    condition     = local.state_bucket == "${var.platform_state_bucket_prefix}-${lower(var.vcs_repo_name)}-${data.aws_region.current.region}"
    error_message = "State bucket must be <prefix>-<repo in lowercase>-<region>, got ${local.state_bucket}"
  }
}

run "state_bucket_name_replaces_underscores_and_uses_custom_prefix" {
  command = plan

  variables {
    vcs_repo_name                = "Brain_TF"
    platform_state_bucket_prefix = "tfstate"
  }

  assert {
    condition     = local.state_bucket == "${var.platform_state_bucket_prefix}-${replace(lower(var.vcs_repo_name), "_", "-")}-${data.aws_region.current.region}"
    error_message = "Underscores must become dashes and the custom prefix must be used, got ${local.state_bucket}"
  }
}

# ======================= Files generated for main_module =======================

run "backend_file_is_generated_for_main_module" {
  command = plan

  assert {
    condition     = length(local_file.backend_config) == 1
    error_message = "backend.generated.tf must be generated while main_module has no backend block of its own."
  }

  assert {
    condition     = local_file.backend_config[0].filename == "${path.module}/${var.main_module_dir}/backend.generated.tf"
    error_message = "The backend file must be written next to main_module's configuration, got ${local_file.backend_config[0].filename}"
  }

  assert {
    condition = alltrue([
      strcontains(local_file.backend_config[0].content, "bucket       = \"${local.state_bucket}\""),
      strcontains(local_file.backend_config[0].content, "key          = \"${var.main_module_state_key}\""),
      strcontains(local_file.backend_config[0].content, "region       = \"${data.aws_region.current.region}\""),
      strcontains(local_file.backend_config[0].content, "encrypt      = true"),
      strcontains(local_file.backend_config[0].content, "use_lockfile = true"),
    ])
    error_message = "The generated S3 backend must use the state bucket, the main-module key, the current region, encryption and S3 locking."
  }
}

run "tfvars_are_copied_to_main_module" {
  command = plan

  assert {
    condition     = local_file.this.filename == "${path.module}/${var.main_module_dir}/terraform.auto.tfvars"
    error_message = "bootstrap must copy its tfvars into main_module/terraform.auto.tfvars, got ${local_file.this.filename}"
  }

  assert {
    condition     = local_file.this.content == data.local_file.this.content
    error_message = "The copied tfvars must match terraform.tfvars byte for byte."
  }
}

# ======================= State bucket policy =======================

# The bucket policy references the bucket ARN, which is only known after apply.
# With every provider mocked, apply creates nothing and writes no files.
run "state_bucket_denies_insecure_transport" {
  command = apply

  assert {
    condition     = jsondecode(aws_s3_bucket_policy.state_bucket_policy.policy).Statement[0].Effect == "Deny"
    error_message = "The first statement of the state bucket policy must be a Deny."
  }

  assert {
    condition     = jsondecode(aws_s3_bucket_policy.state_bucket_policy.policy).Statement[0].Condition.Bool["aws:SecureTransport"] == "false"
    error_message = "The state bucket must deny requests that are not sent over TLS."
  }

  assert {
    condition = toset(jsondecode(aws_s3_bucket_policy.state_bucket_policy.policy).Statement[0].Resource) == toset([
      module.s3_state_bucket.s3_bucket_arn,
      "${module.s3_state_bucket.s3_bucket_arn}/*",
    ])
    error_message = "The TLS-only rule must cover the bucket and every object in it."
  }
}

# ======================= Open findings: these runs fail until the code is fixed =======================

# local.state_bucket is meant to keep only characters S3 allows, but
# replace(…, "[^a-z0-9.-]", "") matches that text literally; a regular expression needs
# slashes: "/[^a-z0-9.-]/". "+" is valid in IAM names, so only the bucket name breaks.
run "finding_state_bucket_name_keeps_only_s3_characters" {
  command = plan

  variables {
    vcs_repo_name = "Brain+TF"
  }

  assert {
    condition     = can(regex("^[a-z0-9.-]+$", local.state_bucket))
    error_message = "The state bucket name must contain only a-z, 0-9, '.' and '-', got ${local.state_bucket}"
  }
}

# vcs_repo_name has no validation. A 36-character name passes, and the state bucket name
# (<prefix>-<repo>-<region>) is then longer than the 63 characters S3 allows; today the user
# only finds out from the AWS provider. Expected: var.vcs_repo_name rejects it.
run "finding_repo_name_too_long_for_bucket_is_rejected" {
  command = plan

  variables {
    vcs_repo_name = "braintf-repository-name-is-too-long1"
  }

  expect_failures = [var.vcs_repo_name]
}
