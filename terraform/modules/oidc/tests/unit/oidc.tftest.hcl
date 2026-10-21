# Unit tests for the OIDC module: who may assume the pipeline role and what the role may touch.
# No AWS access, nothing is created.
#
# Run from terraform/modules/oidc:
#   terraform init -backend=false -test-directory=tests/unit
#   terraform test -test-directory=tests/unit
#
# The last section holds open findings: runs that describe what the code should do and fail
# until the code is fixed. Keep it at the end of the file.
#
# The AWS provider here is the real one, but with fake credentials and no account lookup,
# so it never reaches AWS. It renders aws_iam_policy_document locally, which gives the real
# policy JSON to assert on; a mock would return an empty placeholder instead. Every resource
# and the thumbprint script are overridden, so `command = apply` (the default) creates
# nothing. A resource added to the module without an override fails these tests on the fake
# credentials instead of creating anything.

variables {
  # Settings of the fake provider below.
  test_aws_region = "eu-west-1"

  # Inputs of the module under test, as main_module passes them for GitHub.
  vcs_provider         = "github"
  oidc_role_name       = "BrainTF-oidc-github-eu-west-1-role"
  oidc_policy_name     = "BrainTF-oidc-github-eu-west-1-policy"
  oidc_provider        = "token.actions.githubusercontent.com"
  artifacts_bucket     = "artifacts-braintf-eu-west-1"
  managed_state_bucket = "backend-state-bucket-braintf-eu-west-1"
  kms_key_arn          = "arn:aws:kms:eu-west-1:123456789012:key/00000000-0000-0000-0000-000000000000"
  client_id_list       = ["sts.amazonaws.com"]
  aud_variable         = "token.actions.githubusercontent.com:aud"
  sub_variable         = "token.actions.githubusercontent.com:sub"
  sub_values = [
    "repo:epmc-poc/BrainTF:ref:refs/heads/main",
    "repo:epmc-poc/BrainTF:pull_request",
  ]
}

provider "aws" {
  region                      = var.test_aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}

# get_thumbprint.sh opens a TLS connection to the issuer; never run it in unit tests.
# Override values cannot use variables.
override_data {
  target = data.external.get_thumbprint
  values = {
    result = {
      thumbprint = "0000000000000000000000000000000000000000"
    }
  }
}

override_resource {
  target = aws_iam_openid_connect_provider.vcs_oidc_provider
  values = {
    arn = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
  }
}

override_resource {
  target = aws_iam_role.vcs_oidc_role
  values = {
    arn = "arn:aws:iam::123456789012:role/terraform-test-oidc-role"
  }
}

override_resource {
  target = aws_iam_policy.oidc_policy
  values = {
    arn = "arn:aws:iam::123456789012:policy/terraform-test-oidc-policy"
  }
}

override_resource {
  target = aws_iam_role_policy_attachment.vcs_oidc_policy_attachment
}

run "trust_policy_is_scoped_to_repository" {
  assert {
    condition     = jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Action == "sts:AssumeRoleWithWebIdentity"
    error_message = "The role may only be assumed through web identity federation."
  }

  assert {
    condition     = jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Principal.Federated == aws_iam_openid_connect_provider.vcs_oidc_provider.arn
    error_message = "The trust policy must name this module's OIDC provider as the principal."
  }

  # Policy JSON renders one value as a string and several as a list; flatten() reads both.
  assert {
    condition     = tolist(flatten([jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Condition.StringEquals[var.aud_variable]])) == var.client_id_list
    error_message = "The trust policy must pin the token audience."
  }

  assert {
    condition     = tolist(flatten([jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Condition.StringLike[var.sub_variable]])) == var.sub_values
    error_message = "The trust policy must allow exactly the given sub claims."
  }
}

run "role_policy_has_no_wildcard_resources" {
  assert {
    condition     = alltrue([for s in jsondecode(data.aws_iam_policy_document.oidc_policy.json).Statement : !contains(flatten([s.Resource]), "*")])
    error_message = "The pipeline role policy must not grant any action on Resource = \"*\"."
  }

  assert {
    condition = toset(flatten([
      for s in jsondecode(data.aws_iam_policy_document.oidc_policy.json).Statement : s.Resource if startswith(flatten([s.Action])[0], "s3:")
      ])) == toset([
      "arn:aws:s3:::${var.artifacts_bucket}",
      "arn:aws:s3:::${var.artifacts_bucket}/*",
      "arn:aws:s3:::${var.managed_state_bucket}",
      "arn:aws:s3:::${var.managed_state_bucket}/*",
    ])
    error_message = "S3 access must be limited to the artifacts bucket and the managed state bucket."
  }

  assert {
    condition     = [for s in jsondecode(data.aws_iam_policy_document.oidc_policy.json).Statement : s.Resource if startswith(flatten([s.Action])[0], "kms:")] == [var.kms_key_arn]
    error_message = "KMS access must be limited to the given key."
  }

  assert {
    condition     = [for s in jsondecode(data.aws_iam_policy_document.oidc_policy.json).Statement : s.Resource if flatten([s.Action])[0] == "sts:AssumeRoleWithWebIdentity"] == [aws_iam_role.vcs_oidc_role.arn]
    error_message = "The role may only assume itself through web identity."
  }
}

run "gitlab_audience_and_claims" {
  variables {
    vcs_provider   = "gitlab"
    oidc_provider  = "gitlab.com"
    client_id_list = ["https://gitlab.com"]
    aud_variable   = "gitlab.com:aud"
    sub_variable   = "gitlab.com:sub"
    sub_values     = ["project_path:epmc-poc/braintf:ref_type:branch:ref:*"]
  }

  assert {
    condition     = tolist(flatten([jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Condition.StringEquals[var.aud_variable]])) == var.client_id_list
    error_message = "GitLab tokens must be checked against the issuer URL audience."
  }

  assert {
    condition     = tolist(flatten([jsondecode(data.aws_iam_policy_document.vcs_assume_role_policy.json).Statement[0].Condition.StringLike[var.sub_variable]])) == var.sub_values
    error_message = "The GitLab sub claim must be limited to the project."
  }
}

# ======================= Open findings: these runs fail until the code is fixed =======================

# get_thumbprint.sh returns the openssl fingerprint in uppercase, and the module passes it on
# unchanged. AWS stores thumbprints in lowercase, so every plan shows a change to
# thumbprint_list. The override returns what the script really prints for this issuer.
run "finding_thumbprint_is_passed_in_lowercase" {
  override_data {
    target = data.external.get_thumbprint
    values = {
      result = {
        thumbprint = "06D927FECD0A84AEBA28AAD1D808139470FE95C3"
      }
    }
  }

  assert {
    condition     = alltrue([for t in aws_iam_openid_connect_provider.vcs_oidc_provider.thumbprint_list : t == lower(t)])
    error_message = "Thumbprints must be lowercase as AWS stores them, otherwise every plan shows a change: ${jsonencode(aws_iam_openid_connect_provider.vcs_oidc_provider.thumbprint_list)}"
  }
}
