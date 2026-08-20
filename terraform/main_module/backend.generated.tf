#======================= The Main module for application infrastructure =======================#
terraform {
  backend "s3" {
    bucket       = "backend-state-bucket-braintf-eu-central-1"
    key          = "main-module/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}
