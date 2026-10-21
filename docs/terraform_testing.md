# Terraform tests

BrainTF's own Terraform code (`terraform/bootstrap`, `terraform/main_module`, `terraform/modules/*`) is tested with the native `terraform test` command in a dedicated developer pipeline, [`.github/workflows/terraform-tests.yml`](../.github/workflows/terraform-tests.yml). This first step contains **unit tests only**: they need no AWS credentials and create nothing in any cloud account.

The existing pipelines are unchanged. `pipeline.yml` keeps scanning the demo workload in `WORK_DIRS`, and `developer-pipeline.yml` keeps running the Python tests of the Lambda functions.

## Contents

- [How a unit test runs without AWS](#how-a-unit-test-runs-without-aws)
- [What deserves a unit test](#what-deserves-a-unit-test)
- [Developer pipeline](#developer-pipeline)
- [Layout and conventions](#layout-and-conventions)
- [Running the tests locally](#running-the-tests-locally)
- [Test catalogue](#test-catalogue)
- [Open findings](#open-findings)
- [Prerequisites and constraints](#prerequisites-and-constraints)
- [Known risks and limitations](#known-risks-and-limitations)
- [Plan for further implementation](#plan-for-further-implementation)
- [What we took from the HashiCorp tutorial](#what-we-took-from-the-hashicorp-tutorial)

## How a unit test runs without AWS

`terraform test` reads the `*.tftest.hcl` files of a configuration and executes their `run` blocks in order. Each `run` is a `plan` (or an `apply`) of the configuration with the variables the test sets, followed by its `assert` blocks. State lives in memory only; the S3 backend is never used.

Nothing reaches AWS because every provider is replaced in one of three ways:

| Technique | What it does | Used where |
|---|---|---|
| `mock_provider` | Terraform answers for the provider: computed attributes get generated values, data sources return the configured `defaults`. The real provider is still loaded for its schema and argument validation | `bootstrap`, `main_module`, `modules/bucket` |
| Real provider, offline | The real AWS provider with fake credentials and `skip_credentials_validation`, `skip_requesting_account_id`, `skip_metadata_api_check`. It renders `aws_iam_policy_document` locally, so tests read the real policy JSON. Every resource and every data source that would call AWS is overridden | `modules/oidc`, `bucket_policy.tftest.hcl` |
| `override_module` / `override_resource` / `override_data` | Replace a module's outputs, a resource's attributes or a data source's result with fixed values. An overridden module is not evaluated at all | Child modules of `main_module`, upstream modules of `bootstrap`, the thumbprint script of `modules/oidc` |

Terraform works in two steps. First it evaluates the configuration: variables, locals, conditions, `count`, `for_each`, names, policy documents. Then the provider calls the AWS API. A unit test stops after the first step: the plan holds every planned resource with its arguments, and the assertions read those arguments. Where the configuration needs something only AWS knows (region, account id, the ARN of a bucket that does not exist yet), the mock answers with a fixed value. A test therefore says: with these inputs and these answers from AWS, our code computes this.

Unit tests check BrainTF's own logic: input validation, feature toggles, names other components depend on, IAM policy content, the CI variables written to the VCS, and the files bootstrap generates. They do not prove that AWS accepts a change; that needs integration tests (see the plan below).

## What deserves a unit test

A unit test is worth its upkeep when it protects a decision in BrainTF's code that something depends on or that is dangerous to get wrong:

1. **A contract with another component**: names the Lambdas read (SSM parameters), CI variables the workflows read, the state bucket name that bootstrap and main_module compute separately, the generated backend file.
2. **Security**: who may assume the pipeline role, which values are secrets, no `Resource = "*"`, TLS-only bucket policies.
3. **Validation rules** written in `variables.tf`.
4. **Known bugs**: the `finding_*` runs.

A test that only restates a string concatenation or a `count` condition nobody relies on is not written. For example, the bucket module's `create_directories = false` branch is not tested: BrainTF always passes `true`.

## Developer pipeline

`terraform-tests.yml` has two stages.

| | Stage 1: unit tests | Stage 2: report |
|---|---|---|
| Trigger | `pull_request` to `main` with changes in `terraform/**` or in the workflow; manual run (`workflow_dispatch`) | After Stage 1, also when it failed |
| Jobs | One job per configuration that has `tests/unit/*.tftest.hcl` (found by the `discover` job) | One job |
| Steps | `terraform fmt -check -recursive` (includes the test files), `terraform init -backend=false`, `terraform validate -test-directory=tests/unit` (validates the test files too), `terraform test -test-directory=tests/unit -junit-xml=…`, then `scripts/normalize_terraform_junit.py` on the JUnit file | Downloads the JUnit files and publishes them with `dorny/test-reporter`, the action `developer-pipeline.yml` already uses |
| Access | No AWS credentials, `AWS_CONFIG_FILE`/`AWS_SHARED_CREDENTIALS_FILE` point to `/dev/null`, instance metadata disabled. `terraform test` runs in a network namespace without interfaces | `checks: write` to publish the report |
| Quality gate | Any failing run fails the job of that configuration; the job is meant to become a required status check | The check run "Terraform test results" lists every run with its result |

Why the JUnit file is normalized: Terraform 1.14 writes the duration only on each `<testcase>`, not on `<testsuite>`, so the report showed "NaNms"; and for a run that ends in an error (such as a missing expected failure) it writes `message="Encountered an error"` and keeps the reason in the element text, so the report showed only that phrase. `scripts/normalize_terraform_junit.py` sets the suite durations and puts "<error title>: <explanation>" into the message. It changes nothing Terraform already filled in, and uses only the Python standard library.

Why the network is cut during `terraform test` (GitHub runners do have internet access, and `init` uses it): a `mock_provider` only replaces providers that are declared in the root module under test, and `local-exec` provisioners run even for mocked resources. Both were observed while building these tests (see [Layout and conventions](#layout-and-conventions)). Without network, such a leak fails the test instead of quietly calling the internet. `terraform init` runs before that, with network, because it downloads providers and modules.

The role of `terraform test` in BrainTF: it checks the behaviour of BrainTF's Terraform code before review. The static checks (`fmt`, `validate`, TFLint, Checkov, TFSec, Trivy in `pipeline.yml`) stay as they are; a full deployment to a test AWS account stays the end-to-end check.

## Layout and conventions

```text
terraform/
  tests/mocks/aws/aws.tfmock.hcl     shared mock data of the AWS provider
  bootstrap/tests/unit/*.tftest.hcl
  main_module/tests/unit/*.tftest.hcl
  modules/<name>/tests/unit/*.tftest.hcl
```

Every test file has the same shape: a header comment (what it tests, how to run it), providers and overrides, one `variables` block, the `run` blocks grouped by topic, and at the end the section of open findings.

**Where literal values may appear.** Test data is defined once and referenced everywhere else:

- The `variables` block at the top of the file holds the inputs of the module under test and test values used by several runs. Run blocks set only the values that differ for that run.
- Assertions contain no copies of test data. They reference variables (`var.vcs_repo_name`), data sources that return mock values (`data.aws_region.current.region`), module outputs (`module.oidc[0].oidc_role_arn`) or other attributes. Literals in assertions are limited to the contract itself: names such as `JOB_TOKEN`, values such as `SecureString` or `Deny`.
- `mock_provider`, `mock_data`, `override_*` blocks cannot use variables (Terraform rejects `var.*` there). Their values are written once: in `terraform/tests/mocks/aws/aws.tfmock.hcl` for data that several configurations share, or in a single override block per file.

**Rules learned while writing the first tests:**

1. **Set every variable in the test file.** `terraform test` loads `terraform.tfvars` and `*.auto.tfvars` from the configuration directory. Locally that includes your `secrets.auto.tfvars`; in CI those files do not exist. Values in the test file take precedence over them, so setting all of them makes local and CI runs identical. Do not create `.tfvars` files for tests: `*.tfvars` is in `.gitignore`.
2. **A `mock_provider` only replaces providers declared in the root module under test.** `main_module` uses `external` (thumbprint script) and `null` (Lambda packaging) only inside child modules, so mocking them in a `main_module` test has no effect, and Terraform gives no warning: the script really opened a TLS connection. In root-module tests, replace child modules with `override_module` and test each module in its own directory.
3. **Provisioners run even for mocked and overridden resources.** An `apply` of `main_module` in a test ran `docker run … pip install` and packaged the Lambdas. Test `main_module` and `modules/lambdas` with `command = plan`, or override the module.
4. **Mocked values must look real.** Mocks fill computed attributes with random 8-character strings, and the provider still validates them ("invalid ARN", "invalid JSON"). Give `mock_data` realistic `defaults`.
5. **`override_resource` does not skip the provider's argument validation; `override_module` does**, because the module's resources are not evaluated. Use `override_module` when the point of a run is a value computed before a module, such as a name.
6. **Asserts only see outputs of child modules**, not their resources. Assert on root resources, locals and module outputs.
7. **Compare lists with `tolist()`.** `local.x == ["a", "b"]` fails with "LHS and RHS values are of different types"; write `local.x == tolist(["a", "b"])`. Policy JSON renders one value as a string and several as a list; `flatten([...])` reads both.
8. **A run that ends in an error makes Terraform skip all later runs of the file.** A failed assertion does not. A missing expected failure (`expect_failures` that did not happen) is an error, which is why the open findings sit at the end of each file.
9. **Paths in `mock_provider { source = … }` are relative to the configuration directory**, not to the test file.

## Running the tests locally

From the configuration directory:

```bash
terraform init -backend=false -test-directory=tests/unit
terraform test -test-directory=tests/unit
```

To run them exactly like the pipeline, without network:

```bash
unshare -rn terraform test -test-directory=tests/unit
```

`terraform init -backend=false` leaves an existing S3 backend configuration and its state alone. `-test-directory` matters for `init` too: without it, `init` does not look at `tests/unit`.

## Test catalogue

Runs whose name starts with `finding_` describe an open finding and fail on purpose; see [Open findings](#open-findings).

### `terraform/bootstrap/tests/unit/bootstrap.tftest.hcl`

Mocked `aws` and `local` providers; the upstream KMS and S3 modules are overridden, so the tests look only at bootstrap's own resources and locals.

| Run | Checks |
|---|---|
| `state_bucket_name_is_lowercase_and_regional` | `local.state_bucket` is `<prefix>-<repo in lowercase>-<region>` |
| `state_bucket_name_replaces_underscores_and_uses_custom_prefix` | `_` becomes `-`, and `platform_state_bucket_prefix` replaces the default prefix |
| `backend_file_is_generated_for_main_module` | `backend.generated.tf` is planned next to `main_module` with the state bucket, key `main-module/terraform.tfstate`, region, `encrypt` and `use_lockfile` |
| `tfvars_are_copied_to_main_module` | `terraform.tfvars` is copied byte for byte to `main_module/terraform.auto.tfvars` |
| `state_bucket_denies_insecure_transport` | The state bucket policy starts with a Deny of non-TLS requests to the bucket and its objects (`apply` with mocks, because the policy needs the bucket ARN) |
| `finding_state_bucket_name_keeps_only_s3_characters` | Open finding 1 |
| `finding_repo_name_too_long_for_bucket_is_rejected` | Open finding 2 |

### `terraform/main_module/tests/unit/main_module.tftest.hcl`

Mocked `aws`, `random`, `github`, `gitlab`; modules `oidc` and `ai_lambda` are overridden.

| Run | Checks |
|---|---|
| `ai_handler_disabled_creates_only_vcs_integration` | With `ai_handler_create = false`: no artifacts bucket, OIDC, IAM, DynamoDB, Lambda, webhook secret or SSM parameters; only the GitHub integration; no AI handler CI variables |
| `ai_handler_enabled_creates_ai_stack` | With the AI handler on: every component is planned, all AI handler CI variables are published, exactly three SSM parameters, all `SecureString` |
| `shared_resource_names_follow_convention` | Names other components depend on: the artifacts bucket, the state bucket (bootstrap computes the same name separately) and the SSM parameters (the Lambdas read them by name) |
| `only_job_token_is_secret` | `JOB_TOKEN` is the only CI value stored as a secret |
| `ci_variables_point_to_this_deployment` | `ARTIFACTS_BUCKET` points to `<bucket>/logs`, `OIDC_ROLE_ARN` comes from the oidc module, `VCS_API_ENDPOINT` is `https://api.<host>`, `OIDC_AUDIENCE` is `sts.amazonaws.com`, `AWS_REGION` is the deployment region |
| `backend_params_use_bootstrap_bucket_by_default` | `TERRAFORM_BACKEND_PARAMS` with the bootstrap state bucket, the managed key, region, KMS alias, encryption and S3 locking |
| `backend_params_use_managed_bucket_when_set` | `managed_state_bucket` and `managed_state_key` replace the defaults |
| `github_oidc_trust_limited_to_main_and_pull_requests` | The OIDC `sub` values allow only `main` pushes and pull requests of the repository, in both claim formats |
| `gitlab_uses_gitlab_integration_and_claims` | With `vcs_provider = gitlab`: only the GitLab integration, GitLab `sub` claim and audience, API endpoint `https://<host>/api/v4` |
| `rejects_unknown_vcs_provider` | Validation of `vcs_provider` |
| `rejects_unknown_log_level` | Validation of `log_level` |
| `rejects_temperature_above_two` | Validation of `ai_temperature` |
| `rejects_state_key_without_directory` | Validation of `managed_state_key`: a directory prefix is required |
| `rejects_state_key_with_leading_slash` | Validation of `managed_state_key`: no leading slash |
| `finding_artifacts_bucket_name_keeps_only_s3_characters` | Open finding 1 |
| `finding_repo_name_too_long_is_rejected` | Open finding 2 |

### `terraform/modules/oidc/tests/unit/oidc.tftest.hcl`

Real AWS provider offline; every resource and the thumbprint script are overridden.

| Run | Checks |
|---|---|
| `trust_policy_is_scoped_to_repository` | `sts:AssumeRoleWithWebIdentity` only, from this module's provider, with the audience pinned and exactly the given `sub` values |
| `role_policy_has_no_wildcard_resources` | No statement on `Resource = "*"`; S3 only on the artifacts and state buckets; KMS only on the given key; web identity only on the role itself |
| `gitlab_audience_and_claims` | Same trust policy checks with GitLab inputs |
| `finding_thumbprint_is_passed_in_lowercase` | Open finding 4 |

### `terraform/modules/bucket/tests/unit/bucket.tftest.hcl`

Mocked `aws`.

| Run | Checks |
|---|---|
| `lifecycle_rule_is_rendered` | Status mapping, prefix, expiration and noncurrent expiration days, no expiration blocks for a rule without them, multipart abort default of 7 days |
| `rejects_abort_days_above_seven` | Validation of `abort_incomplete_multipart_upload_days` |
| `finding_wildcard_lifecycle_prefix_is_rejected` | Open finding 3 |

### `terraform/modules/bucket/tests/unit/bucket_policy.tftest.hcl`

Real AWS provider offline; the two data sources of the upstream S3 module that call AWS are overridden.

| Run | Checks |
|---|---|
| `policy_denies_insecure_transport` | First statement denies non-TLS requests to the bucket and its objects |
| `policy_grants_only_this_account` | The Allow statement is limited to the account root and lists actions explicitly |

## Open findings

These runs describe what the code should do and fail today. They stay red until the code is fixed; the fix is out of scope of this change. When a finding is fixed, the run turns green and can be renamed without the `finding_` prefix.

| # | Finding | Where in the code | Failing runs | What the run shows |
|---|---|---|---|---|
| 1 | Bucket name sanitising does nothing: `replace(…, "[^a-z0-9.-]", "")` matches that text literally; a regular expression needs slashes, `"/[^a-z0-9.-]/"` | `bootstrap/main.tf` (`local.state_bucket`), `main_module/main.tf` (`local.artifacts_bucket`, `local.bootstrap_state_bucket`) | `finding_state_bucket_name_keeps_only_s3_characters`, `finding_artifacts_bucket_name_keeps_only_s3_characters` | `backend-state-bucket-brain+tf-eu-west-1`, `artifacts-brain/tf-eu-west-1` |
| 2 | `vcs_repo_name` has no validation. The safe length depends on the prefixes and the region: in `eu-west-1` with the default prefixes, more than 28 characters break the Lambda IAM role name (`Terraform-AI-Handler-Role-<repo>-<region>`, limit 64) and more than 32 the state bucket name (limit 63). Characters such as space or `+` break IAM, KMS alias or S3 names. The user only learns it from the AWS provider | `bootstrap/variables.tf`, `main_module/variables.tf` | `finding_repo_name_too_long_for_bucket_is_rejected`, `finding_repo_name_too_long_is_rejected` | `var.vcs_repo_name, was expected to report an error but did not` |
| 3 | S3 lifecycle prefixes are literal. `main_module` passes `prefix = "artifacts/*"` for the 3-day retention, so the rule never matches objects under `artifacts/`, and the bucket module accepts the wildcard silently | `main_module/main.tf` (module `artifacts_bucket`), `modules/bucket/variables.tf` | `finding_wildcard_lifecycle_prefix_is_rejected` | `var.lifecycle_rules, was expected to report an error but did not` |
| 4 | `get_thumbprint.sh` returns the fingerprint in uppercase; AWS stores it in lowercase, so every plan shows a change to `thumbprint_list` | `modules/oidc/get_thumbprint.sh`, `modules/oidc/main.tf` | `finding_thumbprint_is_passed_in_lowercase` | `["06D927FECD0A84AEBA28AAD1D808139470FE95C3"]` |

One more finding cannot be shown by a unit test, because it is about the order in which AWS calls happen:

| # | Finding | Where in the code | How it was confirmed |
|---|---|---|---|
| 5 | The directory placeholder objects only reference the bucket id, which is known as soon as the bucket exists, before the upstream module applies default encryption and versioning. `logs/` and `artifacts/` end up encrypted with SSE-S3 (`AES256`) instead of the KMS key. The lifecycle configuration references `var.bucket_name` and does not depend on the bucket at all | `modules/bucket/main.tf` (`aws_s3_object.directory`, `aws_s3_bucket_lifecycle_configuration.lifecycle`) | A prototype integration test in a separate AWS account, and `aws s3api head-object` on a deployed artifacts bucket. It belongs to the future integration tests |

## Prerequisites and constraints

| Topic | Requirement |
|---|---|
| Terraform version | `terraform test` exists since 1.6, mocks and overrides since 1.7. The pipeline uses `TERRAFORM_VERSION` 1.14.8, the same as `pipeline.yml` (see `DEPENDENCIES.md`). Some modules declare `required_version >= 1.5.7`; their tests still need 1.7+. `skip_cleanup` and `terraform test cleanup` exist only in experimental builds of 1.14.8; unit tests do not need them |
| Providers | `init` downloads every provider even for mocked tests, because mocks need the provider schema. `.terraform.lock.hcl` is not committed, so provider versions float within their constraints; a new provider release can change mock behaviour |
| Modules | `main_module` pulls pinned `terraform-aws-modules` from GitHub; an uncached `init` took 2 min 43 s. The pipeline caches the plugin cache and `.terraform/modules` |
| Backend | Not used: `init -backend=false`, state in memory. `backend.generated.tf` does not interfere |
| Test data | In the test files and in `terraform/tests/mocks`: fake account id `123456789012`, region `eu-west-1`, fake ARNs and IDs |
| AWS credentials | None. Nothing is created, and the tests run without network |
| Resource isolation and cleanup | Not needed for unit tests: no real resource exists at any point. Both become requirements for integration tests |

## Known risks and limitations

- **Mocks are not AWS.** A green unit test does not mean AWS accepts the change (finding 5 is an example). Integration tests and a full deployment to a test account cover that gap.
- **Mocks need upkeep.** New resources and attributes need new overrides or defaults, and upstream modules can break on generated values.
- **Tests execute code.** Provisioners and external scripts run unless overridden; review test files as carefully as the configuration they test. The network cut in the pipeline is the safety net.
- **The sudo fallback for the network namespace.** GitHub's Ubuntu 24.04 runners block unprivileged user namespaces, so the pipeline uses `sudo unshare --net` and drops back to the runner user with `setpriv`. Self-hosted runners without passwordless sudo need another way to cut the network.
- **The JUnit normalizer depends on Terraform's report format.** If a Terraform upgrade changes the format, the report may fall back to "NaNms" or "Encountered an error"; the test results themselves are not affected. Check the report after upgrading Terraform.
- **Slow `init`.** Uncached `init` of `main_module` takes minutes because of git-sourced modules.
- **Red pipeline until the findings are fixed.** The open findings fail on purpose, so the unit jobs of `bootstrap`, `main_module`, `modules/oidc` and `modules/bucket` stay red until then. Make the job a required check only after that.

## Plan for further implementation

1. **Fix the open findings** in separate pull requests; each fix turns its `finding_` run green.
2. **More unit tests**: `modules/iam` (log group ARNs match the Lambda function names, policy scope), `modules/vcs_integration/github` and `gitlab` (masked values become secrets, webhook only with the AI handler), `modules/lambdas` (environment variables, layer rebuild trigger; plan only), and the branch of `bootstrap` that skips `backend.generated.tf` when `main_module` already has a backend. Then make the unit job a required status check and add a check that every module under `terraform/modules` has `tests/unit`.
3. **Integration tests** (a separate stage, run on request) for cheap modules such as `modules/bucket` and `modules/dynamodb`: `command = apply` in a dedicated test AWS account, unique names per run, automatic teardown by `terraform test`, and a leak check afterwards. Prerequisites:
   - an IAM role for the tests, assumed through GitHub OIDC, limited to resources with a test name prefix and without access to the state bucket;
   - a repository variable with that role's ARN, so the workflow does not hardcode the account (the same pattern as the existing `OIDC_ROLE_ARN`);
   - a long-lived KMS key for test buckets (a deleted key stays pending deletion for at least 7 days);
   - a GitHub environment with required reviewers to approve each cloud run. Environments in private repositories need a paid GitHub plan; without one, the role has to trust the pull request claim instead.
4. **End-to-end and versions**: a full `main_module` deployment in an ephemeral environment before releases; re-evaluate newer Terraform versions for `skip_cleanup` and backend blocks in `run` blocks; consider committing `.terraform.lock.hcl`.

## What we took from the HashiCorp tutorial

The primary reference is [Write Terraform tests](https://developer.hashicorp.com/terraform/tutorials/configuration-language/test).

Adopted:

- `.tftest.hcl` files in `tests/` next to each configuration, with `-test-directory` selecting the suite (`tests/unit` now, `tests/integration` later).
- `run` blocks with `command = plan`, `assert` blocks with clear error messages, `expect_failures` for validation rules.
- Mocks and overrides (`mock_provider`, `override_resource`, `override_data`, `override_module`) instead of real resources.
- Pinned provider versions and `terraform init` after adding a provider or module.

Not adopted now:

- `command = apply` against real infrastructure, helper modules that create test resources, and automatic teardown: they belong to the integration tests in the plan above.
- HCP Terraform and private registry testing (`-cloud-run`, "Enable testing for Module"): BrainTF runs on GitHub Actions with an S3 backend, and its modules are local paths.
- The live HTTP endpoint check: BrainTF has no public website.

Other references: [Tests language](https://developer.hashicorp.com/terraform/language/tests), [Mocks](https://developer.hashicorp.com/terraform/language/tests/mocking), [`terraform test` command](https://developer.hashicorp.com/terraform/cli/commands/test).
