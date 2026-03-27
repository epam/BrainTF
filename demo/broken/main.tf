terraform {
  # Missing required_version — will be caught by TFLint (terraform_required_version)
  # Missing required_providers — will be caught by TFLint (terraform_required_providers)
}

provider "aws" {
  region = "eu-west-1"
}
