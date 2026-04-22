# Project Dependencies Map

This document lists all external dependencies used in the project, their locations, current versions, and where to check for updates.

> Last updated: 2026-04-21 (EPMCACMAWS-420)

## CI/CD Pipeline Tools

| Tool | File | Variable/Pattern | Current Version | Check Latest |
|------|------|-----------------|-----------------|--------------|
| Terraform | `.github/workflows/pipeline.yml` | `TERRAFORM_VERSION` | 1.14.8 | https://releases.hashicorp.com/terraform/ |
| TFLint | `.github/workflows/pipeline.yml` | `TFLINT_VERSION` | v0.62.0 | https://github.com/terraform-linters/tflint/releases |
| Checkov | `.github/workflows/pipeline.yml` | `CHECKOV_VERSION` | 3.2.524 | https://github.com/bridgecrewio/checkov/releases |
| TFSec | `.github/workflows/pipeline.yml` | `TFSEC_VERSION` | v1.28.14 | https://github.com/aquasecurity/tfsec/releases |
| Trivy | `.github/workflows/pipeline.yml` | `TRIVY_VERSION` | 0.70.0 | https://github.com/aquasecurity/trivy/releases |

## GitLab CI (legacy, same tools)

| Tool | File | Variable/Pattern | Current Version | Check Latest |
|------|------|-----------------|-----------------|--------------|
| Terraform | `.gitlab-ci.yml` | `TERRAFORM_VERSION` | 1.5.6 | https://releases.hashicorp.com/terraform/ |
| TFLint | `.gitlab-ci.yml` | `TFLINT_VERSION` | v0.56.0 | https://github.com/terraform-linters/tflint/releases |
| Checkov | `.gitlab-ci.yml` | `CHECKOV_VERSION` | 3.2.432 | https://github.com/bridgecrewio/checkov/releases |
| TFSec | `.gitlab-ci.yml` | `TFSEC_VERSION` | v1.28.12 | https://github.com/aquasecurity/tfsec/releases |
| Trivy | `.gitlab-ci.yml` | `TRIVY_VERSION` | 0.69.3 | https://github.com/aquasecurity/trivy/releases |

## TFLint Plugins

| Plugin | File | Current Version | Check Latest |
|--------|------|-----------------|--------------|
| tflint-ruleset-aws | `.tflint.hcl` | 0.47.0 | https://github.com/terraform-linters/tflint-ruleset-aws/releases |
| tflint-ruleset-terraform | `.tflint.hcl` | 0.14.1 | https://github.com/terraform-linters/tflint-ruleset-terraform/releases |

## Pre-commit Hooks

| Hook | File | Current Version | Check Latest |
|------|------|-----------------|--------------|
| pre-commit-terraform | `.pre-commit-config.yaml` | v1.105.0 | https://github.com/antonbabenko/pre-commit-terraform/releases |
| pre-commit-hooks | `.pre-commit-config.yaml` | v6.0.0 | https://github.com/pre-commit/pre-commit-hooks/releases |

## Custom Action Tools

| Tool | File | Pattern | Current Version | Check Latest |
|------|------|---------|-----------------|--------------|
| Trivy | `.github/actions/pre-commit/action.yml` | download URL | 0.70.0 | https://github.com/aquasecurity/trivy/releases |
| terraform-docs | `.github/actions/pre-commit/action.yml` | download URL | v0.22.0 | https://github.com/terraform-docs/terraform-docs/releases |
| ripgrep | `.github/actions/pre-commit/action.yml` | download URL | 15.1.0 | https://github.com/BurntSushi/ripgrep/releases |
| hcledit | `.github/actions/pre-commit/action.yml` | download URL | 0.2.17 | https://github.com/minamijoyo/hcledit/releases |
| tfsec | `.github/actions/pre-commit/action.yml` | download URL | v1.28.14 | https://github.com/aquasecurity/tfsec/releases |

## Semantic Release (npm)

| Package | File | Pattern | Current Version | Check Latest |
|---------|------|---------|-----------------|--------------|
| semantic-release | `.github/workflows/release.yml` | `npm install` command | 25.0.3 | https://github.com/semantic-release/semantic-release/releases |
| conventional-changelog-conventionalcommits | `.github/workflows/release.yml` | `npm install` command | 9.3.1 | https://github.com/conventional-changelog/conventional-changelog/releases |
| @semantic-release/changelog | `.github/workflows/release.yml` | `npm install` command | 6.0.3 | https://github.com/semantic-release/changelog/releases |
| @semantic-release/git | `.github/workflows/release.yml` | `npm install` command | 10.0.1 | https://github.com/semantic-release/git/releases |

## GitHub Actions

| Action | Files | Current Version | Check Latest |
|--------|-------|-----------------|--------------|
| actions/checkout | `pipeline.yml`, `release.yml` | v6 | https://github.com/actions/checkout/releases |
| actions/cache | `pipeline.yml` | v5 | https://github.com/actions/cache/releases |
| aws-actions/configure-aws-credentials | `pipeline.yml` | v6 | https://github.com/aws-actions/configure-aws-credentials/releases |
| amannn/action-semantic-pull-request | `pipeline.yml` | v6.1.1 | https://github.com/amannn/action-semantic-pull-request/releases |
| cycjimmy/semantic-release-action | `release.yml` | v6 | https://github.com/cycjimmy/semantic-release-action/releases |
| clowdhaus/terraform-composite-actions | `pipeline.yml` | v1.14.0 | https://github.com/clowdhaus/terraform-composite-actions/releases |
| clowdhaus/terraform-min-max | `pipeline.yml` | v3.0.1 | https://github.com/clowdhaus/terraform-min-max/releases |
| actions/stale | `.github/workflows/stale.yml` | v10 | https://github.com/actions/stale/releases |

## Terraform Modules (pinned by commit hash)

| Module | File | Current Hash | Version | Check Latest |
|--------|------|-------------|---------|--------------|
| terraform-aws-kms | `terraform/bootstrap/main.tf` | `407e3db3...` | v4.2.0 | https://github.com/terraform-aws-modules/terraform-aws-kms/releases |
| terraform-aws-s3-bucket | `terraform/bootstrap/main.tf` | `6c5e082b...` | v5.12.0 | https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/releases |
| terraform-aws-ssm-parameter | `terraform/main_module/main.tf` | `c0456aa1...` | v2.1.0 | https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter/releases |
| terraform-aws-lambda (x2) | `terraform/modules/lambdas/main.tf` | `4cfa5b42...` | v8.7.0 | https://github.com/terraform-aws-modules/terraform-aws-lambda/releases |

> **Note:** Terraform modules are pinned by commit hash, not tag. To update: find the latest release tag on GitHub, then get the full commit SHA of that tag.

## Python Packages (production)

| Package | File | Current Version | Check Latest |
|---------|------|-----------------|--------------|
| python-gitlab | `terraform/modules/lambdas/functions/requirements.txt` | 8.2.0 | https://pypi.org/project/python-gitlab/ |
| requests | `terraform/modules/lambdas/functions/requirements.txt` | 2.33.1 | https://pypi.org/project/requests/ |
| openai | `terraform/modules/lambdas/functions/requirements.txt` | 2.32.0 | https://pypi.org/project/openai/ |
| beautifulsoup4 | `terraform/modules/lambdas/functions/requirements.txt` | 4.14.3 | https://pypi.org/project/beautifulsoup4/ |
| PyGithub | `terraform/modules/lambdas/functions/requirements.txt` | 2.9.1 | https://pypi.org/project/PyGithub/ |

## Python Packages (test)

| Package | File | Current Version | Check Latest |
|---------|------|-----------------|--------------|
| boto3 | `terraform/modules/lambdas/functions/test-requirements.txt` | 1.42.93 | https://pypi.org/project/boto3/ |
| pytest | `terraform/modules/lambdas/functions/test-requirements.txt` | 9.0.3 | https://pypi.org/project/pytest/ |
| pytest-cov | `terraform/modules/lambdas/functions/test-requirements.txt` | 7.1.0 | https://pypi.org/project/pytest-cov/ |

> **Note:** test-requirements.txt also includes the same packages as requirements.txt (production). Keep versions in sync.
