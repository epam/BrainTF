MAIN_TF_FILE = \
    """
terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

""".lstrip().removesuffix("\n")
