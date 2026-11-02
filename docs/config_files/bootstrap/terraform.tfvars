# Do not edit: change the bootstrap inputs and re-run terraform apply in terraform/bootstrap.
# Tag block
environment = "<my_environment>"      # Environment name (e.g., Production, Staging, Development)
team        = "<my_team>"             # Team responsible for the infrastructure
deployed_by = "Terraform"             # Tool for deploying the infrastructure
owner_mail  = "<my_mail@example.com>" # Email address of the infrastructure owner

# Block of common variables
vcs_repo_name = "<my_project>" # Name of the project (gitlab or github)

# State bucket protection
state_bucket_force_destroy = false # Keep false to protect the state bucket from deletion. Set true only for demo/dev teardown (deletes the bucket with all its state files).
