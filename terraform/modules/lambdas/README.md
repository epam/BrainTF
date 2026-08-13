# lambdas

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.7, < 2.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | >=3.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_null"></a> [null](#provider\_null) | >=3.0 |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_ai_lambda_vcs"></a> [ai\_lambda\_vcs](#module\_ai\_lambda\_vcs) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | 4cfa5b42d1928afbc8946393e36eeee77eca0851 |
| <a name="module_process_comment_lambda_vcs"></a> [process\_comment\_lambda\_vcs](#module\_process\_comment\_lambda\_vcs) | git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git | 4cfa5b42d1928afbc8946393e36eeee77eca0851 |

## Resources

| Name | Type |
| ---- | ---- |
| [aws_lambda_function_url.webhook_url_vcs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function_url) | resource |
| [aws_lambda_layer_version.layer](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_layer_version) | resource |
| [aws_lambda_permission.allow_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [null_resource.lambda_layer](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_ai_api_base_url"></a> [ai\_api\_base\_url](#input\_ai\_api\_base\_url) | The API base URL for the AI service | `string` | n/a | yes |
| <a name="input_ai_api_token_name"></a> [ai\_api\_token\_name](#input\_ai\_api\_token\_name) | The name of the secret storing the AI API token | `string` | n/a | yes |
| <a name="input_ai_handler_create"></a> [ai\_handler\_create](#input\_ai\_handler\_create) | AI handler creation trigger | `string` | n/a | yes |
| <a name="input_artifacts_bucket"></a> [artifacts\_bucket](#input\_artifacts\_bucket) | The artifacts bucket name | `string` | n/a | yes |
| <a name="input_artifacts_path"></a> [artifacts\_path](#input\_artifacts\_path) | The path where the corrected Terraform files (artifacts) will be stored. | `string` | n/a | yes |
| <a name="input_dynamodb_table_name"></a> [dynamodb\_table\_name](#input\_dynamodb\_table\_name) | The name for a dynamodb table | `string` | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | The ARN of the KMS key used for encryption | `string` | n/a | yes |
| <a name="input_lambda_exec_role_arn"></a> [lambda\_exec\_role\_arn](#input\_lambda\_exec\_role\_arn) | ARN of the role to execute the lambda function | `string` | `""` | no |
| <a name="input_llm_model"></a> [llm\_model](#input\_llm\_model) | The name or identifier of the LLM (Large Language Model) to be used | `string` | n/a | yes |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | The logging level for AWS Lambda functions. Possible values: DEBUG, INFO, WARN, ERROR. | `string` | `"INFO"` | no |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | VPC Private Subnet IDs | `list(string)` | n/a | yes |
| <a name="input_rag_enable"></a> [rag\_enable](#input\_rag\_enable) | Whether to turn on RAG for AI handler. | `bool` | `false` | no |
| <a name="input_security_groups"></a> [security\_groups](#input\_security\_groups) | Security Groups for Lambda-Git Connection | `list(string)` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | n/a | yes |
| <a name="input_vcs_api_endpoint"></a> [vcs\_api\_endpoint](#input\_vcs\_api\_endpoint) | The API endpoint for VCS integration (e.g., GitLab, GitHub) | `string` | n/a | yes |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | The VCS provider used for deployment (e.g., github, gitlab) | `string` | n/a | yes |
| <a name="input_vcs_repo_name"></a> [vcs\_repo\_name](#input\_vcs\_repo\_name) | Repo name used for resource tagging and naming | `string` | n/a | yes |
| <a name="input_vcs_token_name"></a> [vcs\_token\_name](#input\_vcs\_token\_name) | Parameter Store Variable Name for Git Token | `string` | `""` | no |
| <a name="input_webhook_secret_name"></a> [webhook\_secret\_name](#input\_webhook\_secret\_name) | The name of the secret used for securing webhooks | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_function_url"></a> [function\_url](#output\_function\_url) | Lambda function to be triggered if PR Comment is updated |
<!-- END_TF_DOCS -->
