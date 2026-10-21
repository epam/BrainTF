# Shared mock data for the AWS provider in BrainTF unit tests.
#
# A test file loads it with:
#   mock_provider "aws" {
#     source = "<path from the configuration directory to this directory>"
#   }
#
# Terraform does not allow variables inside mock data, so the fake account, region and KMS
# key are written here once. Tests read them back through the data sources
# (data.aws_region.current.region, data.aws_kms_alias.kms_key.arn, ...) instead of
# repeating the values.

mock_data "aws_region" {
  defaults = {
    region = "eu-west-1"
  }
}

mock_data "aws_caller_identity" {
  defaults = {
    account_id = "123456789012"
    arn        = "arn:aws:iam::123456789012:user/terraform-test"
  }
}

# A mocked policy document would otherwise get a random 8-character string as its JSON,
# which the provider rejects wherever a policy is expected.
mock_data "aws_iam_policy_document" {
  defaults = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
  }
}

mock_data "aws_kms_alias" {
  defaults = {
    arn            = "arn:aws:kms:eu-west-1:123456789012:alias/terraform-test"
    target_key_arn = "arn:aws:kms:eu-west-1:123456789012:key/00000000-0000-0000-0000-000000000000"
  }
}
