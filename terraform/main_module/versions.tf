terraform {
  required_version = ">= 1.11"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.9"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.13"
    }
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "~> 18.1.1"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    # OwnerGithub / Branch are only added when set: AWS tag values should not be
    # empty, and prod (main) has no single owning branch. Tag values only allow
    # letters, digits, spaces and _ . : / = + - @ (max 256), so sanitize them.
    tags = merge(
      {
        Project     = var.vcs_repo_name
        Environment = var.environment
        Team        = var.team
        DeployedBy  = var.deployed_by
        OwnerEmail  = var.owner_mail
      },
      var.owner_github != "" ? { OwnerGithub = substr(replace(var.owner_github, "/[^A-Za-z0-9 _.:\\/=+@-]/", "-"), 0, 256) } : {},
      var.target_branch != "" ? { Branch = substr(replace(var.target_branch, "/[^A-Za-z0-9 _.:\\/=+@-]/", "-"), 0, 256) } : {},
    )
  }
}
