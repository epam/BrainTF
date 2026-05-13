# dynamodb

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.5.7, < 2.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dynamodb_table"></a> [dynamodb\_table](#module\_dynamodb\_table) | git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git | 495d7a5e6ee9a45ae985a4160d9242c8b8727d69 |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_attributes"></a> [attributes](#input\_attributes) | Attributes for the DynamoDB table | <pre>list(object({<br>    name = string<br>    type = string<br>  }))</pre> | n/a | yes |
| <a name="input_billing_mode"></a> [billing\_mode](#input\_billing\_mode) | The billing mode for the DynamoDB table | `string` | `"PAY_PER_REQUEST"` | no |
| <a name="input_hash_key"></a> [hash\_key](#input\_hash\_key) | The primary key of the DynamoDB table | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | The name of the DynamoDB table | `string` | n/a | yes |
| <a name="input_point_in_time_recovery_enabled"></a> [point\_in\_time\_recovery\_enabled](#input\_point\_in\_time\_recovery\_enabled) | Whether point-in-time recovery is enabled | `bool` | `false` | no |
| <a name="input_range_key"></a> [range\_key](#input\_range\_key) | The range key of the DynamoDB table (optional) | `string` | `null` | no |
| <a name="input_server_side_encryption_enabled"></a> [server\_side\_encryption\_enabled](#input\_server\_side\_encryption\_enabled) | Whether server-side encryption is enabled | `bool` | `true` | no |
| <a name="input_server_side_encryption_kms_key_arn"></a> [server\_side\_encryption\_kms\_key\_arn](#input\_server\_side\_encryption\_kms\_key\_arn) | KMS key ARN for server-side encryption | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to the DynamoDB table | `map(string)` | `{}` | no |
| <a name="input_ttl_attribute_name"></a> [ttl\_attribute\_name](#input\_ttl\_attribute\_name) | The name of the TTL attribute | `string` | `null` | no |
| <a name="input_ttl_enabled"></a> [ttl\_enabled](#input\_ttl\_enabled) | Whether TTL is enabled | `bool` | `false` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
