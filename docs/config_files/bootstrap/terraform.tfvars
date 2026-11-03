# Do not edit: change the bootstrap inputs and re-run terraform apply in terraform/bootstrap.
# Tag block
environment = "<my_environment>"      # Environment name (e.g., Production, Staging, Development)
team        = "<my_team>"             # Team responsible for the infrastructure
deployed_by = "Terraform"             # Tool for deploying the infrastructure
owner_mail  = "<my_mail@example.com>" # Email address of the infrastructure owner

# Block of common variables
vcs_repo_name = "<my_project>" # Name of the project (gitlab or github)

# State backend configuration
platform_state_bucket_prefix = "<my_platform_state_bucket_prefix>" # Prefix for the platform state S3 bucket name (stores bootstrap + main_module state). Synced to main_module via terraform.auto.tfvars.
state_bucket_force_destroy   = "<false>"                           # Allow Terraform to delete the state bucket together with all its objects and versions. Keep false to protect the state; set true only for demo/dev teardown.
