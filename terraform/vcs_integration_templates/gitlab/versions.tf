terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "~> 18.1.1"
    }
  }
}
