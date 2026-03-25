# state_bucket

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.7, < 2.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | ~> 3.2 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_null"></a> [null](#provider\_null) | ~> 3.2 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_s3_bucket_kms_key"></a> [s3\_bucket\_kms\_key](#module\_s3\_bucket\_kms\_key) | git::https://github.com/terraform-aws-modules/terraform-aws-kms.git | e0171db13c467d93e79e2bd82981ba3b207dfe6d |
| <a name="module_s3_state_bucket"></a> [s3\_state\_bucket](#module\_s3\_state\_bucket) | git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git | 2dd4364b67d89cb9c881be465e5e4196ef8dea8f |

## Resources

| Name | Type |
|------|------|
| [aws_iam_role.terraform_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_s3_bucket_policy.state_bucket_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy) | resource |
| [null_resource.add_or_update_backend_and_remote_state](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.select_vcs_module](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.sync_tfvars](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The account ID for the project | `string` | n/a | yes |
| <a name="input_deployed_by"></a> [deployed\_by](#input\_deployed\_by) | The deployment method | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The Project environment | `string` | n/a | yes |
| <a name="input_owner_mail"></a> [owner\_mail](#input\_owner\_mail) | The owner e-mail | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | The region where AWS resources will be created | `string` | n/a | yes |
| <a name="input_team"></a> [team](#input\_team) | The owner team | `string` | n/a | yes |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | The VCS provider used for deployment (e.g., github, gitlab) | `string` | n/a | yes |
| <a name="input_vcs_repo_name"></a> [vcs\_repo\_name](#input\_vcs\_repo\_name) | The name of the project | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
