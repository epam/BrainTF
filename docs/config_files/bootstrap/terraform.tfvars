# Tag block
environment = "<my_environment>"      # Environment name (e.g., Production, Staging, Development)
team        = "<my_team>"             # Team responsible for the infrastructure
deployed_by = "Terraform"             # Tool for deploying the infrastructure
owner_mail  = "<my_mail@example.com>" # Email address of the infrastructure owner

# Block of common variables
vcs_repo_name = "<my_project>" # Name of the project (gitlab or github)

# Bootstrap-only settings (not passed to main_module)
platform_state_bucket_prefix = "<my-platform-state-bucket-prefix>" # Prefix for the platform state S3 bucket name (stores bootstrap + main_module state). Optional: this is the default.
state_bucket_force_destroy   = "<false>"                           # Keep false to protect the state bucket from deletion. Set true only for demo/dev teardown (deletes the bucket with all its state files).
