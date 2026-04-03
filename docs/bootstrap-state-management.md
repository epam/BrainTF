# Bootstrap State Management

## Overview

The `bootstrap` module creates the AWS infrastructure required to store Terraform state remotely:

- **S3 bucket** — `backend-state-bucket-{vcs_repo_name}-{region}` (stores `main_module` state)
- **KMS key** — `alias/kms_key_{vcs_repo_name}_{region}` (encrypts state files)
- **IAM role** — `Terraform-role-{vcs_repo_name}-{region}`

After a successful `terraform apply`, bootstrap automatically injects the backend configuration into `terraform/main_module/main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket       = "backend-state-bucket-{vcs_repo_name}-{region}"
    key          = "terraform.tfstate"
    region       = "{region}"
    encrypt      = "true"
    use_lockfile = "true"
  }
}
data "aws_kms_alias" "kms_key" {
  name = "alias/kms_key_{vcs_repo_name}_{region}"
}
```

## The Problem

By default, bootstrap's own Terraform state is stored **locally** on the machine that ran `terraform apply` (a `terraform.tfstate` file in the `terraform/bootstrap/` directory).

This creates a risk: if the machine is lost or the file is deleted, you lose the ability to manage bootstrap resources (update or destroy them).

## Options for Managing Bootstrap State

### Option 1: Store state in the git repository

Commit `terraform.tfstate` to the repository.

> This approach can be used to store **ONLY** this particular state file. Other state files must not be stored in VCS, since Terraform state files might contain sensitive data. Storing them in git exposes this data to everyone with repository access.
>
> Consider moving to Option 2 if there is a requirement to encrypt **all** Terraform state files.

### Option 2: Migrate state to S3 (recommended)

After bootstrap creates the S3 bucket, migrate the local bootstrap state into that same bucket.

#### Steps

1. Run bootstrap as usual:

   ```bash
   cd terraform/bootstrap
   terraform init
   terraform apply
   ```

2. Add a backend configuration to `terraform/bootstrap/main.tf`:

   ```hcl
   terraform {
     backend "s3" {
       bucket       = "backend-state-bucket-{vcs_repo_name}-{region}"
       key          = "bootstrap/terraform.tfstate"
       region       = "{region}"
       encrypt      = true
       use_lockfile = true
     }
   }
   ```

   > Use a different `key` than `main_module` (e.g. `bootstrap/terraform.tfstate`) to avoid overwriting.

3. Migrate the local state to S3:

   ```bash
   terraform init -migrate-state
   ```

   Terraform will detect the new backend and ask to copy the existing local state to S3. Confirm with `yes`.

4. Verify the migration — check that the state file appears in the S3 bucket:

   ```bash
   aws s3 ls s3://backend-state-bucket-{vcs_repo_name}-{region}/bootstrap/
   ```

5. The local `terraform.tfstate` file in `terraform/bootstrap/` is no longer needed. It can be deleted or added to `.gitignore`.

#### Result

| Module        | State location | S3 key                     |
|---------------|----------------|----------------------------|
| bootstrap     | Remote S3      | `bootstrap/terraform.tfstate` |
| main_module   | Remote S3      | `terraform.tfstate`           |

Both modules now store state in the same S3 bucket, protected by KMS encryption and S3 versioning.
