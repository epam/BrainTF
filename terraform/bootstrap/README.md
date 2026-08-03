# state_bucket

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.7, < 2.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | ~> 2.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_local"></a> [local](#provider\_local) | ~> 2.0 |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_s3_bucket_kms_key"></a> [s3\_bucket\_kms\_key](#module\_s3\_bucket\_kms\_key) | git::https://github.com/terraform-aws-modules/terraform-aws-kms.git | 407e3db34a65b384c20ef718f55d9ceacb97a846 |
| <a name="module_s3_state_bucket"></a> [s3\_state\_bucket](#module\_s3\_state\_bucket) | git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git | 6c5e082b5d2fde77cb59c387a7f553dd2ed5da29 |

## Resources

| Name | Type |
| ---- | ---- |
| [aws_iam_role.terraform_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.terraform_state_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_s3_bucket_policy.state_bucket_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy) | resource |
| [local_file.backend_config](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.this](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.this](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | AWS account ID | `string` | n/a | yes |
| <a name="input_deployed_by"></a> [deployed\_by](#input\_deployed\_by) | The deployment method | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The Project environment | `string` | n/a | yes |
| <a name="input_owner_mail"></a> [owner\_mail](#input\_owner\_mail) | The owner e-mail | `string` | n/a | yes |
| <a name="input_platform_state_bucket_prefix"></a> [platform\_state\_bucket\_prefix](#input\_platform\_state\_bucket\_prefix) | Custom prefix for the platform state S3 bucket name (stores state of bootstrap + main\_module) | `string` | `"backend-state-bucket"` | no |
| <a name="input_region"></a> [region](#input\_region) | The region where AWS resources will be created | `string` | n/a | yes |
| <a name="input_team"></a> [team](#input\_team) | The owner team | `string` | n/a | yes |
| <a name="input_vcs_repo_name"></a> [vcs\_repo\_name](#input\_vcs\_repo\_name) | The Project name | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_kms_key_arn"></a> [kms\_key\_arn](#output\_kms\_key\_arn) | ARN of the KMS key used for bucket encryption |
| <a name="output_state_bucket_arn"></a> [state\_bucket\_arn](#output\_state\_bucket\_arn) | ARN of the S3 state bucket created by bootstrap |
| <a name="output_state_bucket_name"></a> [state\_bucket\_name](#output\_state\_bucket\_name) | Name of the S3 state bucket created by bootstrap (can be reused as managed\_state\_bucket in main\_module) |
<!-- END_TF_DOCS -->
