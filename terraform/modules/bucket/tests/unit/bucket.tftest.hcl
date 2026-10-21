# Unit tests for the bucket module's lifecycle rules: how the dynamic blocks are rendered from
# var.lifecycle_rules and how the input is validated. No AWS access, nothing is created.
#
# Run from terraform/modules/bucket:
#   terraform init -backend=false -test-directory=tests/unit
#   terraform test -test-directory=tests/unit
#
# The last section holds open findings: runs that describe what the code should do and
# fail until the code is fixed. Keep it at the end of the file: a run that ends in an error
# (such as a missing expected failure) makes Terraform skip every run after it.

mock_provider "aws" {
  source = "../../tests/mocks/aws"
}

variables {
  # Inputs of the module under test.
  bucket_name = "artifacts-braintf-eu-west-1"
  account_id  = "123456789012"
  kms_key_arn = "arn:aws:kms:eu-west-1:123456789012:key/00000000-0000-0000-0000-000000000000"

  # Multipart abort period the module applies when a rule does not set one.
  default_abort_days = 7
}

run "lifecycle_rule_is_rendered" {
  command = plan

  variables {
    lifecycle_rules = [
      {
        id                                 = "artifacts-retention"
        enabled                            = true
        prefix                             = "artifacts/"
        expiration_days                    = 3
        noncurrent_version_expiration_days = 1
      },
      {
        id      = "paused"
        enabled = false
      },
    ]
  }

  assert {
    condition     = [for r in aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule : r.status] == ["Enabled", "Disabled"]
    error_message = "enabled = true/false must map to status Enabled/Disabled."
  }

  assert {
    condition     = aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule[0].filter[0].prefix == var.lifecycle_rules[0].prefix
    error_message = "The rule prefix must be passed through."
  }

  assert {
    condition     = aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule[0].expiration[0].days == var.lifecycle_rules[0].expiration_days
    error_message = "expiration_days must become expiration.days."
  }

  assert {
    condition     = aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule[0].noncurrent_version_expiration[0].noncurrent_days == var.lifecycle_rules[0].noncurrent_version_expiration_days
    error_message = "noncurrent_version_expiration_days must become noncurrent_version_expiration.noncurrent_days."
  }

  assert {
    condition     = length(aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule[1].expiration) == 0 && length(aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule[1].noncurrent_version_expiration) == 0
    error_message = "A rule without expiration settings must not get expiration blocks."
  }

  assert {
    condition     = alltrue([for r in aws_s3_bucket_lifecycle_configuration.lifecycle[0].rule : r.abort_incomplete_multipart_upload[0].days_after_initiation == var.default_abort_days])
    error_message = "Incomplete multipart uploads must be aborted after ${var.default_abort_days} days by default."
  }
}

run "rejects_abort_days_above_seven" {
  command = plan

  variables {
    lifecycle_rules = [
      {
        id                                     = "too-long"
        enabled                                = true
        abort_incomplete_multipart_upload_days = 30
      },
    ]
  }

  expect_failures = [var.lifecycle_rules]
}

# ======================= Open findings: these runs fail until the code is fixed =======================

# S3 lifecycle prefixes are literal: "artifacts/*" only matches keys that start with the
# characters "artifacts/*", so the rule never applies to objects under artifacts/. The
# module accepts such a prefix without a word, and main_module passes exactly this value
# for the artifacts bucket (3-day retention). Expected: var.lifecycle_rules rejects it.
run "finding_wildcard_lifecycle_prefix_is_rejected" {
  command = plan

  variables {
    lifecycle_rules = [
      {
        id              = "artifacts-retention"
        enabled         = true
        prefix          = "artifacts/*"
        expiration_days = 3
      },
    ]
  }

  expect_failures = [var.lifecycle_rules]
}
