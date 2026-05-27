# github

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.7, < 2.0 |
| <a name="requirement_github"></a> [github](#requirement\_github) | ~> 6.5 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_github"></a> [github](#provider\_github) | ~> 6.5 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [github_actions_secret.secrets](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/actions_secret) | resource |
| [github_actions_variable.variables](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/actions_variable) | resource |
| [github_repository_webhook.webhook](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_webhook) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_ai_handler_create"></a> [ai\_handler\_create](#input\_ai\_handler\_create) | Whether to create AI handler webhooks. | `bool` | `false` | no |
| <a name="input_function_url"></a> [function\_url](#input\_function\_url) | The URL for the webhook function. | `string` | n/a | yes |
| <a name="input_vcs_project_path"></a> [vcs\_project\_path](#input\_vcs\_project\_path) | The vcs project path or ID | `string` | n/a | yes |
| <a name="input_vcs_variables"></a> [vcs\_variables](#input\_vcs\_variables) | List of variables to create in the vcs project | <pre>list(object({<br/>    key         = string                # The variable key<br/>    value       = string                # The variable value<br/>    description = optional(string)      # The description of the variable<br/>    masked      = optional(bool, false) # If true, the variable will be masked in CI/CD logs<br/>    protected   = optional(bool, false) # If true, the variable will only be used in protected branches<br/>  }))</pre> | n/a | yes |
| <a name="input_webhook_secret"></a> [webhook\_secret](#input\_webhook\_secret) | The webhook secret | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_webhook_id"></a> [webhook\_id](#output\_webhook\_id) | The ID of the created GitHub webhook |
<!-- END_TF_DOCS -->
