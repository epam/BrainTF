# Installation and integration process

## Overview
This document describes the process of setting up the infrastructure for the BrainTF solution using Terraform. The infrastructure consists of two main modules:
1. terraform/bootstrap: Designed for setting up the initial infrastructure, including an S3 bucket for storing the Terraform state, KMS for encryption, and IAM roles.
2. terraform/main_module: The main module that manages the rest of the infrastructure, including resource creation, integration with VCS (GitHub/GitLab), SSM parameters, Lambda functions, and other necessary components.

## Prerequisites for installing BrainTF

Before starting the installation, ensure that you have the following available and properly configured:

* AWS Account with administrator permissions.
* AWS CLI version 2 installed and configured.
* Terraform installed (recommended version >= 1.14.5).
* Access to GitHub or GitLab for VCS integration.
* Git installed for repository management (recommended version >= 2.30).
* Docker (recommended version >= 29.2.1) installed, running, and accessible.
* AWS VPC ID with private subnets (IDs) and a security group (ID) with port 443 open in ingress.

## CI/CD pipeline configuration

Workflow/pipeline described in this section can work independently and also be adopted into your workflow/pipeline to start using the tool.

1. Define a comma-separated list of directories with Terraform code in the `WORK_DIRS` variable in the corresponding pipeline file: [.gitlab-ci.yml](../.gitlab-ci.yml) or [pipeline.yml](../.github/workflows/pipeline.yml). Please note that the pipeline can only process code in the same repository as the tools.
2. The rest of the variables can be configured as part of [advanced configuration](#Advanced configuration).

## Terraform backend configuration
1. Choose an option to store Terraform state file for the `bootstrap` module using the guide [here](../docs/state_management.md).
2. Copy the [docs/config_files/bootstrap/terraform.tfvars](./config_files/bootstrap/terraform.tfvars) file into the [bootstrap/](../terraform/bootstrap) directory and replace `<placeholders>` with values for your environment.
3. Copy the [docs/config_files/main_module/terraform.tfvars](./config_files/main_module/terraform.tfvars) and [docs/config_files/main_module/secrets.auto.tfvars](../docs/config_files/main_module/secrets.auto.tfvars) files into the [main_module/](../terraform/main_module) directory. Some variables will be filled in automatically in the next steps.
4. Run `terraform init` command in `terraform/bootstrap` directory.
5. Run `terraform plan/apply` commands in `terraform/bootstrap` directory.
6. `bootstrap` deployment automatically updates [terraform/main_module/main.tf](../terraform/main_module/main.tf) and [terraform/main_module/terraform.tfvars](../terraform/main_module/terraform.tfvars) with common variables.

   <details>
      <summary><b> - main_module/main.tf;</b></summary>
      <img src="../docs/pic/main_module.png" alt="main_module.tf">
   </details>

   <details>
      <summary><b> - main_module/terraform.tfvars</b></summary>
      <img src="../docs/pic/tfvars.png" alt="terraform.tfvars">
   </details>


## Bot deployment
1. Fill in other `<placeholders>` in [terraform/main_module/terraform.tfvars](config_files/main_module/terraform.tfvars) and [terraform/main_module/secrets.auto.tfvars](config_files/main_module/secrets.auto.tfvars) with values.
2. Run `terraform init` command in [terraform/main_module/](terraform/main_module) directory.
3. Run `terraform plan/apply` commands in [terraform/main_module/](terraform/main_module) directory.

## GitHub Environment Setup for Terraform Apply

The `terraform-apply` stage uses a GitHub Environment with manual approval (protection rules) to prevent unintended infrastructure changes. Before running the pipeline, the environment **must** be created and configured.

### User permissions required

To create and configure GitHub Environments with protection rules, the user must have one of the following roles:

| Repository type | Minimum required role |
|---|---|
| Personal repository | Repository owner |
| Organization repository (public) | **Admin** role on the repository |
| Organization repository (private/internal) | **Admin** role on the repository |
| Organization (GitHub Enterprise) | **Admin** role on the repository, or organization owner |

> **Note:** Users with `Write` or `Maintain` roles **cannot** create environments or configure protection rules. Only repository administrators or organization owners have this capability.

### Step-by-step: Create the `terraform-apply` environment

1. Navigate to your GitHub repository.
2. Go to **Settings** → **Environments**.
3. Click **New environment**.
4. Enter the name: `terraform-apply` (must match exactly the value specified in the pipeline YAML under `environment.name`).
5. Click **Configure environment**.

### Step-by-step: Activate Manual Approval (Required Reviewers)

1. Inside the `terraform-apply` environment configuration page, locate the **Environment protection rules** section.
2. Check the **Required reviewers** checkbox.
3. Add one or more users or teams who are authorized to approve deployments. These reviewers will be prompted to approve the workflow run before the `terraform-apply` job proceeds.
4. *(Optional)* Enable **Prevent self-review** if you want to prevent the person who triggered the pipeline from also approving it.
5. Click **Save protection rules**.

### Optional: Additional protection rules

| Protection rule | Description |
|---|---|
| **Wait timer** | Adds a delay (in minutes) before the job can proceed after approval. Useful for giving teams time to react. |
| **Deployment branches and tags** | Restricts which branches or tags can deploy to this environment. Recommended: set to **Selected branches** and add `main` only. |
| **Custom deployment protection rules** | Available on GitHub Enterprise — allows integration with external approval systems (e.g., ServiceNow, Jira). |

### How manual approval works in the pipeline

The `terraform-apply` job in the pipeline is configured as follows:

```yaml
terraform-apply:
  name: Terraform Apply
  needs:
    - setup
    - terraform-plan
  if: ${{ !cancelled() && contains(vars.RUN_TERRAFORM_APPLY, 'true') && needs.terraform-plan.result == 'success' && github.event_name == 'push' && github.ref == 'refs/heads/main' }}
  environment:
    name: terraform-apply
```
### When the pipeline reaches this stage:

1. All previous stages (terraform-plan, security checks, etc.) must have completed successfully.
2. The trigger event must be a push to the main branch (typically after a PR merge).
3. The repository variable RUN_TERRAFORM_APPLY must be set to true.
4. GitHub will pause the workflow and send a notification to the configured reviewers.
5. A reviewer must navigate to the Actions tab, review the pending deployment, and click Approve and deploy.
6. Only after approval will the terraform-apply job execute terraform apply -auto-approve.
````
Important: If no environment named terraform-apply exists or no protection rules are configured, the job will execute immediately without any manual gate. Always ensure the environment is properly configured in production repositories.
````

### After configuration, verify the setup:

1. Trigger the pipeline by pushing a commit to main (or merge a PR).
2. Observe that the pipeline pauses at the Terraform Apply stage.
3. Navigate to Actions → select the running workflow → click Review deployments.
4. Confirm that the correct environment (terraform-apply) is listed and requires approval.
5. Approve and verify that terraform apply executes successfully.

## Post installation check

**1. Create a new MR/PR**

**2. AI Handler automatically scans the Terraform code in the repo and attempts to fix the Terraform issues:**

![ai_handler_suggestion](pic/ai_handler_suggestion.png)

**3. Check the `help` command:**

![ai_handler_help](pic/ai_handler_help.png)

**4. Check the `bot list` command:**

![ai_handler_list](pic/ai_handler_list.png)

**5. Check the `bot approve <path/to/file1>` command:**

![ai_handler_approve](pic/ai_handler_approve.png)

**6. Check the `bot prompt` command:**

![ai_handler_prompt](pic/ai_handler_prompt.png)

**7. If outputs are similar to screenshots in each section, you can move on.**

## Advanced configuration

In order to modify the tools versions used in the pipeline, fill in [.gitlab-ci.yml](../.gitlab-ci.yml) or [pipeline.yml](../.github/workflows/pipeline.yml) with the required values for these tools.

> IMPORTANT. It's not guaranteed that the latest version of BrainTF works fine with older tools versions.

   <details>
     <summary><b> - .gitlab-ci.yml</b></summary>
     <img src="../docs/pic/gitlab_config.png" alt="gitlab_config">
   </details>

   <details>
     <summary><b> - pipeline.yml</b></summary>
     <img src="../docs/pic/github_config.png" alt="github_config">
   </details>
