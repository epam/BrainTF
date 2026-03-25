# main_module

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 3.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_ai_lambda"></a> [ai\_lambda](#module\_ai\_lambda) | ../modules/lambdas | n/a |
| <a name="module_artifacts_bucket"></a> [artifacts\_bucket](#module\_artifacts\_bucket) | ../modules/bucket | n/a |
| <a name="module_dynamodb_table"></a> [dynamodb\_table](#module\_dynamodb\_table) | ../modules/dynamodb | n/a |
| <a name="module_github_integration"></a> [github\_integration](#module\_github\_integration) | ../modules/vcs_integration | n/a |
| <a name="module_iam"></a> [iam](#module\_iam) | ../modules/iam | n/a |
| <a name="module_oidc"></a> [oidc](#module\_oidc) | ../modules/oidc | n/a |
| <a name="module_ssm_parameters"></a> [ssm\_parameters](#module\_ssm\_parameters) | git::https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter.git | 25083ba701549cfe4eb0d57c3fa659fb381f53ac |

## Resources

| Name | Type |
|------|------|
| [random_password.lambda_webhook_secret](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [aws_kms_alias.kms_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/kms_alias) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | AWS account ID | `string` | n/a | yes |
| <a name="input_ai_api_endpoint"></a> [ai\_api\_endpoint](#input\_ai\_api\_endpoint) | The API endpoint for the AI service | `string` | n/a | yes |
| <a name="input_ai_handler_create"></a> [ai\_handler\_create](#input\_ai\_handler\_create) | Whether to create AI handler webhooks. | `bool` | `false` | no |
| <a name="input_ai_token"></a> [ai\_token](#input\_ai\_token) | The AI token | `string` | `""` | no |
| <a name="input_artifacts_bucket_prefix"></a> [artifacts\_bucket\_prefix](#input\_artifacts\_bucket\_prefix) | The prefix to be used for naming an artifacts bucket | `string` | n/a | yes |
| <a name="input_deployed_by"></a> [deployed\_by](#input\_deployed\_by) | The deployment method | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The Project environment | `string` | n/a | yes |
| <a name="input_job_token"></a> [job\_token](#input\_job\_token) | Git Notes token used for GitLab integration | `string` | n/a | yes |
| <a name="input_llm_model"></a> [llm\_model](#input\_llm\_model) | The name or identifier of the LLM (Large Language Model) to be used | `string` | n/a | yes |
| <a name="input_oidc_provider"></a> [oidc\_provider](#input\_oidc\_provider) | The oidc provider | `string` | n/a | yes |
| <a name="input_owner_mail"></a> [owner\_mail](#input\_owner\_mail) | The owner e-mail | `string` | n/a | yes |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | VPC Private Subnet IDs | `list(string)` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | The region where AWS resources will be created | `string` | n/a | yes |
| <a name="input_security_groups"></a> [security\_groups](#input\_security\_groups) | Security Groups for Lambda-Git Connection | `list(string)` | n/a | yes |
| <a name="input_team"></a> [team](#input\_team) | The owner team | `string` | n/a | yes |
| <a name="input_vcs_hostname"></a> [vcs\_hostname](#input\_vcs\_hostname) | The GitLab url for the project | `string` | n/a | yes |
| <a name="input_vcs_project_path"></a> [vcs\_project\_path](#input\_vcs\_project\_path) | The path to the GitLab project | `string` | n/a | yes |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | The VCS provider used for deployment (e.g., github, gitlab) | `string` | n/a | yes |
| <a name="input_vcs_repo_name"></a> [vcs\_repo\_name](#input\_vcs\_repo\_name) | The Project name | `string` | n/a | yes |
| <a name="input_vcs_token"></a> [vcs\_token](#input\_vcs\_token) | The GitLab token | `string` | `""` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
