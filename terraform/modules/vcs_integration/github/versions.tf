terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.5"
    }
  }
}
