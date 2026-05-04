plugin "aws" {
  enabled = true
  version = "0.47.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "terraform" {
  enabled = true
  version = "0.14.1"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
}

config {
  format     = "default"
  plugin_dir = "~/.tflint.d/plugins"

  force               = true
  disabled_by_default = false
}

rule "terraform_standard_module_structure" {
  enabled = true
}
