# Bootstrap State Management

## Overview

The BrainTF project uses multiple Terraform state files stored in S3. This document covers:

1. [Bootstrap state management](#bootstrap-state-management) — where the bootstrap module stores its own state.
2. [Managed workload state management](#managed-workload-state-management) — where the CI/CD pipeline stores the Terraform state for the code under `WORK_DIRS`.
3. [State bucket deletion protection](#state-bucket-deletion-protection) — how the state bucket is protected from accidental deletion and how to tear it down.

---

## Bootstrap State Management

### What bootstrap creates

The `bootstrap` module creates the AWS infrastructure required to store Terraform state remotely:

- **S3 bucket** — `backend-state-bucket-{vcs_repo_name}-{region}` (stores `main_module` state; protected from accidental deletion, see [State Bucket Deletion Protection](#state-bucket-deletion-protection))
- **KMS key** — `alias/kms_key_{vcs_repo_name}_{region}` (encrypts state files)
- **IAM role** — `Terraform-role-{vcs_repo_name}-{region}`

`{region}` is the `region` input from `terraform/bootstrap/terraform.tfvars`; the AWS provider uses it instead of `AWS_REGION` or the AWS CLI profile.

After a successful `terraform apply`, bootstrap automatically generates `terraform/main_module/backend.generated.tf` with the backend configuration:

```hcl
terraform {
  backend "s3" {
    bucket       = "backend-state-bucket-{vcs_repo_name}-{region}"
    key          = "main-module/terraform.tfstate"
    region       = "{region}"
    encrypt      = true
    use_lockfile = true
  }
}
```

It also copies `terraform/bootstrap/terraform.tfvars` to `terraform/main_module/terraform.auto.tfvars` and adds the name of the state bucket:

```hcl
platform_state_bucket = "backend-state-bucket-{vcs_repo_name}-{region}"
```

The state bucket name is defined only in bootstrap (`local.state_bucket`, prefix set by `platform_state_bucket_prefix`). The `main_module` does not build the name itself; it reads `platform_state_bucket` from this file, so both modules always use the same bucket. Do not edit the file: change the bootstrap inputs and run `terraform apply` in `terraform/bootstrap` again.

The `main_module` also checks that this bucket exists (`data.aws_s3_bucket.platform_state`). If the name was changed by mistake, `terraform plan` stops with `reading S3 Bucket (<name>): couldn't find resource`, before the CI variables and the OIDC policy get the wrong bucket. Running `terraform apply` in `terraform/bootstrap` writes the correct name back.

### Migrating an existing deployment

Deployments created before `terraform.auto.tfvars` contained `platform_state_bucket` need one extra step before the next `main_module` run:

1. Run `terraform apply` in `terraform/bootstrap`. The plan replaces only `local_file.this` (the generated `terraform.auto.tfvars`), no AWS changes.
2. Run `terraform plan` in `terraform/main_module`. The bucket name is the same as before, so no resource changes come from this step.

If you cannot run bootstrap on this machine (for example, its local state is on another machine), add the value by hand to `terraform/main_module/terraform.tfvars`:

```hcl
platform_state_bucket = "<terraform output state_bucket_name in terraform/bootstrap>"
```

Without the value, `main_module` stops with `No value for required variable "platform_state_bucket"`.

`main_module` no longer declares `platform_state_bucket_prefix`. Keep it in `bootstrap/terraform.tfvars` if you use a custom prefix: bootstrap does not copy this line to `main_module/terraform.auto.tfvars`. If the prefix is also set by hand in a `main_module` `*.tfvars` file, remove it there; otherwise Terraform shows a harmless `Value for undeclared variable` warning.

### The Problem

By default, bootstrap's own Terraform state is stored **locally** on the machine that ran `terraform apply` (a `terraform.tfstate` file in the `terraform/bootstrap/` directory).

This creates a risk: if the machine is lost or the file is deleted, you lose the ability to manage bootstrap resources (update or destroy them).

### Options for Managing Bootstrap State

#### Option 1: Store state in the git repository

Commit `terraform.tfstate` to the repository.

> This approach can be used to store **ONLY** this particular state file. Other state files must not be stored in VCS, since Terraform state files might contain sensitive data. Storing them in git exposes this data to everyone with repository access.
>
> Consider moving to Option 2 if there is a requirement to encrypt **all** Terraform state files.

#### Option 2: Migrate state to S3 (recommended)

After bootstrap creates the S3 bucket, migrate the local bootstrap state into that same bucket.

##### Steps

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

##### Result

| Module      | State location | S3 key                          |
|-------------|----------------|---------------------------------|
| bootstrap   | Remote S3      | `bootstrap/terraform.tfstate`   |
| main_module | Remote S3      | `main-module/terraform.tfstate` |

Both modules now store state in the same S3 bucket, protected by KMS encryption and S3 versioning.

---

## Managed Workload State Management

### Overview

The CI/CD pipeline (`terraform-plan` and `terraform-apply` stages) needs its own Terraform state file to track infrastructure deployed from the working directories (`WORK_DIRS`). This state is **separate** from the `main_module` state.

The `main_module` automatically:
1. Determines which S3 bucket to use for the managed workload state.
2. Creates a prefix (folder) in that bucket for the managed state file.
3. Exports the full backend configuration string as a VCS CI/CD variable (`TERRAFORM_BACKEND_PARAMS`).

### Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `managed_state_bucket` | Name of the S3 bucket for the managed workload state. Leave **empty** to reuse the bootstrap platform state bucket. | `""` (empty) |
| `managed_state_key` | The S3 object key (path) for the managed workload state file. Must include a directory prefix and end with `.tfstate`. | `pipeline/terraform.tfstate` |

These are configured in `terraform/main_module/terraform.tfvars`:

```hcl
# Managed workload state backend configuration (code under WORK_DIRS)
managed_state_bucket = ""                           # (Optional) Name of an existing S3 bucket for the managed workload state.
managed_state_key    = "pipeline/terraform.tfstate" # S3 key (path) for the managed workload state within the chosen bucket.
```

---

### Scenario A: Use the bootstrap state bucket (default)

This is the simplest option — no additional buckets are needed.

**When to use:** You want to keep everything in a single bucket managed by bootstrap.

#### How it works

1. Leave `managed_state_bucket` empty (`""`).
2. The `main_module` uses the bootstrap state bucket name from `platform_state_bucket` in `terraform.auto.tfvars`, generated by bootstrap:
   ```
   backend-state-bucket-{vcs_repo_name}-{region}
   ```
3. A prefix (folder) is created inside the bucket based on `managed_state_key`. For the default key `pipeline/terraform.tfstate`, the created prefix is `pipeline/`.
4. The pipeline uses this backend configuration at runtime:
   ```
   -backend-config=bucket=backend-state-bucket-{vcs_repo_name}-{region}
   -backend-config=key=pipeline/terraform.tfstate
   -backend-config=region={region}
   -backend-config=kms_key_id={kms_key_arn}
   -backend-config=encrypt=true
   -backend-config=use_lockfile=true
   ```

#### Resulting bucket structure

```
backend-state-bucket-{vcs_repo_name}-{region}/
├── bootstrap/terraform.tfstate       # (if Option 2 above was used)
├── main-module/terraform.tfstate     # main_module state
└── pipeline/terraform.tfstate        # managed workload state (created by CI/CD)
```

#### Configuration example

```hcl
# terraform/main_module/terraform.tfvars
managed_state_bucket = ""                           # Empty → reuse bootstrap bucket
managed_state_key    = "pipeline/terraform.tfstate" # Folder "pipeline/" will be auto-created
```

---

### Scenario B: Use a custom (user-provided) S3 bucket

Use an existing S3 bucket that you manage independently (e.g., a shared bucket across multiple projects).

**When to use:**
- You want to separate the managed workload state from bootstrap infrastructure.
- You have an existing bucket with specific policies, encryption, or cross-account access.

#### Prerequisites

The custom bucket must:
- Already exist in your AWS account.
- Have appropriate IAM permissions for the pipeline role to `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`.
- Preferably have versioning and encryption enabled.

#### How it works

1. Set `managed_state_bucket` to the name of your existing bucket.
2. The `main_module` creates a prefix (folder) in the specified bucket based on `managed_state_key`. For example, key `my-project/terraform.tfstate` results in folder `my-project/`.
3. The pipeline uses this backend configuration at runtime:
   ```
   -backend-config=bucket=my-custom-state-bucket
   -backend-config=key=my-project/terraform.tfstate
   -backend-config=region={region}
   -backend-config=kms_key_id={kms_key_arn}
   -backend-config=encrypt=true
   -backend-config=use_lockfile=true
   ```

#### Resulting bucket structure

```
my-custom-state-bucket/
└── my-project/terraform.tfstate   # managed workload state (created by CI/CD)
```

The bootstrap bucket remains untouched by managed workload state:

```
backend-state-bucket-{vcs_repo_name}-{region}/
├── bootstrap/terraform.tfstate       # (if Option 2 above was used)
└── main-module/terraform.tfstate     # main_module state only
```

#### Configuration example

```hcl
# terraform/main_module/terraform.tfvars
managed_state_bucket = "my-custom-state-bucket"          # Your existing bucket
managed_state_key    = "my-project/terraform.tfstate"    # Folder "my-project/" will be auto-created
```

---

### How the prefix (folder) is created

In both scenarios, the `main_module` creates an empty S3 object acting as the folder prefix. The key is derived from `managed_state_key` via `dirname()`:

```hcl
resource "aws_s3_object" "managed_state_prefix" {
  bucket       = local.managed_state_bucket
  key          = "${dirname(var.managed_state_key)}/"
  content      = ""
  content_type = "application/x-directory"
  tags         = local.tags

  lifecycle {
    precondition {
      condition     = dirname(var.managed_state_key) != "." && dirname(var.managed_state_key) != "/"
      error_message = "managed_state_key must contain a directory prefix (got: '${var.managed_state_key}')."
    }
  }
}
```

For `managed_state_key = "pipeline/terraform.tfstate"`, this creates the object with key `pipeline/` in the target bucket.

For `managed_state_key = "envs/dev/terraform.tfstate"`, this creates the object with key `envs/dev/` in the target bucket.

> **Note:** The actual state file (`terraform.tfstate`) is written by Terraform during `terraform init` in the pipeline. The `aws_s3_object` resource only ensures the parent folder exists beforehand. The `precondition` block enforces that `managed_state_key` includes a directory prefix — a bare `terraform.tfstate` (with no directory) will fail `terraform plan`.

---

## State Bucket Deletion Protection

The platform state bucket (`backend-state-bucket-{vcs_repo_name}-{region}`) holds the `main_module` state, the bootstrap state (if Option 2 was used) and, when `managed_state_bucket` is empty, the managed workload state. Losing it means losing the ability to manage the deployed infrastructure.

### Decision

The bucket is protected from accidental deletion by default. The `state_bucket_force_destroy` bootstrap variable controls the S3 `force_destroy` behavior:

| `state_bucket_force_destroy` | Behavior |
|------------------------------|----------|
| `false` (default) | `terraform destroy` or a resource replacement fails if the bucket contains any objects, object versions or delete markers. The state stays intact. |
| `true` | Terraform deletes the bucket together with **all** objects and versions. S3 versioning does not help. Use for demo/dev environments only. |

The [bootstrap `terraform.tfvars` template](./config_files/bootstrap/terraform.tfvars) sets it to `false`. Set the value in `terraform/bootstrap/terraform.tfvars`:

```hcl
state_bucket_force_destroy = false # default; set true only for demo/dev teardown
```

> **Limits.** The protection works only while the bucket is not empty. An empty bucket can still be destroyed. It also covers Terraform operations only; deleting the bucket directly with the AWS CLI or console is not blocked by this setting.

> **Future consideration.** A bucket policy statement denying `s3:DeleteBucket` could protect against deletes made outside Terraform. It is not part of the current change, because a full `terraform destroy` removes the policy before the bucket.

### Upgrading an existing deployment

Existing deployments were created with `force_destroy = true`. After pulling this change, `terraform apply` in `terraform/bootstrap` performs an in-place update of `force_destroy` only (no replacement of the bucket, KMS key or policy):

- With `state_bucket_force_destroy = false` (the template value and the variable default) the bucket becomes protected. Add the line to your `terraform/bootstrap/terraform.tfvars` or rely on the default.
- To keep the previous behavior, set `state_bucket_force_destroy = true` before applying.

### Teardown

`force_destroy` is stored in the Terraform state, so the flag must be applied before the destroy:

1. Destroy `main_module` and any workload resources first.
2. Set `state_bucket_force_destroy = true` in `terraform/bootstrap/terraform.tfvars` and run `terraform apply` in `terraform/bootstrap`.
3. If the state bucket is used as the backend for bootstrap (Option 2), migrate the bootstrap state back to local first (`terraform init -migrate-state` after removing the `backend "s3"` block). Otherwise Terraform would delete the bucket that holds its own state.
4. Run `terraform destroy` in `terraform/bootstrap`.

To remove the bucket manually, empty **all** object versions and delete markers first. A plain `aws s3 rm --recursive` removes only the current versions and leaves the bucket non-empty.

> The KMS key is scheduled for deletion (7-day window) on destroy. State files cannot be read after the key is deleted.
