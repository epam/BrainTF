# main_module

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.11 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_github"></a> [github](#requirement\_github) | ~> 6.2 |
| <a name="requirement_gitlab"></a> [gitlab](#requirement\_gitlab) | ~> 18.1.1 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 3.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 3.0 |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_ai_dynamodb_table"></a> [ai\_dynamodb\_table](#module\_ai\_dynamodb\_table) | ../modules/dynamodb | n/a |
| <a name="module_ai_lambda"></a> [ai\_lambda](#module\_ai\_lambda) | ../modules/lambdas | n/a |
| <a name="module_artifacts_bucket"></a> [artifacts\_bucket](#module\_artifacts\_bucket) | ../modules/bucket | n/a |
| <a name="module_iam"></a> [iam](#module\_iam) | ../modules/iam | n/a |
| <a name="module_oidc"></a> [oidc](#module\_oidc) | ../modules/oidc | n/a |
| <a name="module_ssm_parameters"></a> [ssm\_parameters](#module\_ssm\_parameters) | git::https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter.git | c0456aa1960c2b13080f3968be9a7cdc687f2c8c |
| <a name="module_vcs_integration_github"></a> [vcs\_integration\_github](#module\_vcs\_integration\_github) | ../modules/vcs_integration/github | n/a |
| <a name="module_vcs_integration_gitlab"></a> [vcs\_integration\_gitlab](#module\_vcs\_integration\_gitlab) | ../modules/vcs_integration/gitlab | n/a |

## Resources

| Name | Type |
| ---- | ---- |
| [random_password.lambda_webhook_secret](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [aws_kms_alias.kms_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/kms_alias) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | AWS account ID | `string` | n/a | yes |
| <a name="input_ai_api_endpoint"></a> [ai\_api\_endpoint](#input\_ai\_api\_endpoint) | The API endpoint for the AI service | `string` | n/a | yes |
| <a name="input_ai_handler_create"></a> [ai\_handler\_create](#input\_ai\_handler\_create) | Whether to create AI handler webhooks. | `bool` | `false` | no |
| <a name="input_ai_token"></a> [ai\_token](#input\_ai\_token) | The AI token | `string` | `""` | no |
| <a name="input_artifacts_bucket_prefix"></a> [artifacts\_bucket\_prefix](#input\_artifacts\_bucket\_prefix) | The prefix to be used for naming an artifacts bucket | `string` | n/a | yes |
| <a name="input_artifacts_path"></a> [artifacts\_path](#input\_artifacts\_path) | The path where the corrected Terraform files (artifacts) will be stored. | `string` | `"artifacts"` | no |
| <a name="input_deployed_by"></a> [deployed\_by](#input\_deployed\_by) | The deployment method | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The Project environment | `string` | n/a | yes |
| <a name="input_job_token"></a> [job\_token](#input\_job\_token) | Git Notes token used for GitLab integration | `string` | n/a | yes |
| <a name="input_llm_model"></a> [llm\_model](#input\_llm\_model) | The name or identifier of the LLM (Large Language Model) to be used | `string` | n/a | yes |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | The logging level for AWS Lambda functions. Possible values: DEBUG, INFO, WARN, ERROR. | `string` | `"INFO"` | no |
| <a name="input_managed_state_bucket"></a> [managed\_state\_bucket](#input\_managed\_state\_bucket) | Name of an existing S3 bucket to store Terraform state for the code under WORK\_DIRS (the workload managed by this pipeline). If empty, the bootstrap platform state bucket will be used with a separate prefix directory. | `string` | `""` | no |
| <a name="input_managed_state_key"></a> [managed\_state\_key](#input\_managed\_state\_key) | S3 key (path) for the Terraform state file used by the managed workload (code under WORK\_DIRS). Must include a directory prefix, e.g. 'pipeline/terraform.tfstate'. | `string` | `"pipeline/terraform.tfstate"` | no |
| <a name="input_oidc_provider"></a> [oidc\_provider](#input\_oidc\_provider) | OIDC identity provider domain (issuer). Used to construct IAM trust policy condition keys (e.g. <provider>:aud, <provider>:sub) and the OIDC provider URL. Use 'token.actions.githubusercontent.com' for GitHub or 'gitlab.com' for GitLab. | `string` | n/a | yes |
| <a name="input_owner_mail"></a> [owner\_mail](#input\_owner\_mail) | The owner e-mail | `string` | n/a | yes |
| <a name="input_platform_state_bucket_prefix"></a> [platform\_state\_bucket\_prefix](#input\_platform\_state\_bucket\_prefix) | Prefix for the bootstrap (platform) state S3 bucket name. Must match the value used in the bootstrap module. | `string` | `"backend-state-bucket"` | no |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | VPC Private Subnet IDs | `list(string)` | n/a | yes |
| <a name="input_rag_enable"></a> [rag\_enable](#input\_rag\_enable) | Whether to turn on RAG for AI handler. | `bool` | `false` | no |
| <a name="input_region"></a> [region](#input\_region) | The region where AWS resources will be created | `string` | n/a | yes |
| <a name="input_run_checkov_analysis"></a> [run\_checkov\_analysis](#input\_run\_checkov\_analysis) | Enable or disable the Checkov analysis stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_terraform_apply"></a> [run\_terraform\_apply](#input\_run\_terraform\_apply) | Enable or disable the Terraform apply stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_terraform_plan"></a> [run\_terraform\_plan](#input\_run\_terraform\_plan) | Enable or disable the Terraform plan stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_terraform_validate"></a> [run\_terraform\_validate](#input\_run\_terraform\_validate) | Enable or disable the Terraform validate stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_tflint_analysis"></a> [run\_tflint\_analysis](#input\_run\_tflint\_analysis) | Enable or disable the TFLint analysis stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_tfsec_analysis"></a> [run\_tfsec\_analysis](#input\_run\_tfsec\_analysis) | Enable or disable the TFSec analysis stage. Default is false. | `bool` | `false` | no |
| <a name="input_run_trivy_analysis"></a> [run\_trivy\_analysis](#input\_run\_trivy\_analysis) | Enable or disable the Trivy analysis stage. Default is false. | `bool` | `false` | no |
| <a name="input_security_groups"></a> [security\_groups](#input\_security\_groups) | Security Groups for Lambda-Git Connection | `list(string)` | n/a | yes |
| <a name="input_team"></a> [team](#input\_team) | The owner team | `string` | n/a | yes |
| <a name="input_vcs_hostname"></a> [vcs\_hostname](#input\_vcs\_hostname) | The VCS hostname for the project | `string` | n/a | yes |
| <a name="input_vcs_project_path"></a> [vcs\_project\_path](#input\_vcs\_project\_path) | The path to the VCS project | `string` | n/a | yes |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | The VCS provider used for deployment (e.g., github, gitlab) | `string` | n/a | yes |
| <a name="input_vcs_repo_name"></a> [vcs\_repo\_name](#input\_vcs\_repo\_name) | The Project name | `string` | n/a | yes |
| <a name="input_vcs_token"></a> [vcs\_token](#input\_vcs\_token) | The VCS token | `string` | `""` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
