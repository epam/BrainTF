# Block of VCS variables
vcs_provider     = "<vcs_provider>"                           # The VCS provider used for deployment (github or gitlab)
vcs_hostname     = "<my_vcs.com>"                             # Hostname of the VCS instance (github.com, gitlab.com, or custom variant)
vcs_project_path = "<my_organization_name>/<my_project_name>" # Path to the VCS project

# The Pipeline Stages Activation Block
run_tflint_analysis    = "false" # Stage to run TFLint, a linter for Terraform code to ensure best practices and catch potential issues.
run_terraform_validate = "false" # Stage to validate the Terraform configuration files for syntax and internal consistency.
run_checkov_analysis   = "false" # Stage to run Checkov, a static code analysis tool for infrastructure-as-code to detect security issues.
run_tfsec_analysis     = "false" # Stage to run TFSec, a static analysis security scanner for Terraform code.
run_trivy_analysis     = "false" # Stage to run Trivy, a static analysis security scanner for Terraform code.
run_terraform_plan     = "false" # Stage to generate an execution plan for Terraform to show planned changes without applying them.
run_terraform_apply    = "false" # Stage to apply the Terraform execution plan and provision infrastructure changes.

# Managed workload state backend configuration (code under WORK_DIRS)
managed_state_bucket = ""                           # (Optional) Name of an existing S3 bucket for the managed workload state. Leave empty to reuse the bootstrap platform state bucket.
managed_state_key    = "pipeline/terraform.tfstate" # S3 key (path) for the managed workload state. Must include a directory prefix and end with .tfstate.

# AI Handler block
ai_handler_create       = "false"                                    # Flag to enable or disable AI handler creation
rag_enable              = "false"                                    # Flag to enable or disable RAG for AI handler
artifacts_path          = "artifacts"                                # The path where the corrected Terraform files (artifacts) will be stored in S3 bucket.
log_level               = "INFO"                                     # The logging level for AWS Lambda functions. Possible values: DEBUG, INFO, WARN, ERROR.
ai_api_endpoint         = "<my_ai_api_endpoint>"                     # Endpoint for AI API
llm_model               = "<my_llm_model_name>"                      # Name of the AI model used
oidc_provider           = "<my_oidc_provider>"                       # Audience for OIDC provider (gitlab.com for GitLab, token.actions.githubusercontent.com for GitHub or other for custom variant)
artifacts_bucket_prefix = "ai-handler-artifacts-bucket"              # Prefix for the name of the artifacts S3 bucket
private_subnet_ids      = ["<subnet_a>", "<subnet_b>", "<subnet_c>"] # List of private subnet IDs for Lambda functions
security_groups         = ["<sg_a>"]                                 # List of security groups with inbound rules for 80 and 443 ports for Lambda functions
