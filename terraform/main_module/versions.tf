terraform {
  required_version = ">= 1.11"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.2"
    }
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "~> 18.1.1"
    }
  }
}
