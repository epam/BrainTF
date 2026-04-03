# BrainTF Demo Scenario

This directory contains intentionally broken and fixed Terraform code for demonstrating BrainTF AI bot capabilities to clients.

## Structure

```
demo/
├── broken/                  # Intentionally broken code (terraform fmt ✅, all other checks ❌)
│   ├── main.tf              # Fails TFLint (missing required_version, required_providers)
│   ├── validate.tf          # Fails Terraform Validate (unknown argument)
│   ├── network/
│   │   └── ec2.tf           # Fails TFSec (security group open to 0.0.0.0/0)
│   ├── storage/
│   │   ├── s3.tf            # Fails Checkov (no versioning, logging, encryption, public access block)
│   │   └── s3_trivy.tf      # Fails Trivy (no public access block, AES256 not KMS, no versioning)
│   └── logging/
│       └── cloudwatch.tf    # Fails Checkov (retention too short, no KMS)
├── fixed/                   # Fixed code — all checks pass ✅
│   ├── main.tf              # TFLint ✅
│   ├── validate.tf          # Terraform Validate ✅
│   ├── network/
│   │   └── ec2.tf           # TFSec ✅
│   ├── storage/
│   │   ├── s3.tf            # Checkov ✅
│   │   └── s3_trivy.tf      # Trivy ✅
│   └── logging/
│       └── cloudwatch.tf    # Checkov ✅
└── README.md
```

> **Note:** All files pass `terraform fmt`. Each file targets exactly one tool. The bot recursively scans all subdirectories when `WORK_DIRS` points to `demo/broken/`.

---

## Demo Files — What Is Broken and Why

| File | Stage | What is broken |
|------|-------|----------------|
| `main.tf` | TFLint | No `required_version`, no `required_providers` |
| `validate.tf` | Terraform Validate | Unknown argument `unknown_field` on resource |
| `network/ec2.tf` | TFSec | Security group ingress open to `0.0.0.0/0` on all ports |
| `storage/s3.tf` | Checkov | No versioning, logging, encryption, public access block |
| `storage/s3_trivy.tf` | Trivy | No public access block, AES256 instead of KMS, no versioning |
| `logging/cloudwatch.tf` | Checkov | Retention 7 days, no KMS encryption |

---

## Prerequisites

Before running the demo, make sure to deploy the BrainTF platform for a repository. Follow documentation in the [main README](../README.md) for more details about the deployment process.

---

## How to Run the Demo

### Step 1 — Create a branch and open a Pull Request

Create a new branch from `main` and open a Draft PR targeting `main`.

### Step 2 — Configure repository variables

Go to **GitHub → Settings → Secrets and variables → Actions → Variables** and set:

| Variable | Value |
|----------|-------|
| `AI_HANDLER_CREATE` | `true` |
| `RUN_TFLINT_ANALYSIS` | `false` |
| `RUN_TERRAFORM_VALIDATE` | `false` |
| `RUN_CHECKOV_ANALYSIS` | `false` |
| `RUN_TFSEC_ANALYSIS` | `false` |
| `RUN_TRIVY_ANALYSIS` | `false` |

Enable **only the stage you want to demonstrate** (see scenarios below).

### Step 3 — Set WORK_DIRS in pipeline.yml

In `.github/workflows/pipeline.yml`, set:

```yaml
env:
  WORK_DIRS: "demo/broken/"
```

The bot will recursively scan all subdirectories (`network/`, `storage/`, `logging/`).

### Step 4 — Trigger the pipeline

Push a commit to trigger the pipeline. The bot will post AI suggestions in the PR comments.

### Step 5 — Interact with the bot

Use bot commands in PR comments:

```
bot list                                    # Show files with suggested fixes
bot approve demo/broken/storage/s3.tf       # Apply fix for a specific file
bot approve all                             # Apply fixes for all files
```

> ⚠️ **Only use `bot list` when the pipeline has failed.**
>
> The bot stores the list of files from the last analysis that found issues. If the pipeline passes with no findings, the stored list is **not cleared automatically**. Running `bot list` after a green pipeline will return files from the previous failing run — which may confuse the audience.
>
> `bot list` is cleared only when `bot approve` is run or a new failing analysis is triggered.

### Step 6 — Show the fixed version

Change `WORK_DIRS` to `demo/fixed/` — pipeline passes clean with no findings.

---

## Demo Scenarios

### Scenario 1 — TFLint

**Target file:** `demo/broken/main.tf`

**Enable:** `RUN_TFLINT_ANALYSIS=true` (all others `false`)

**What the bot finds:**
- Missing `required_version` in terraform block
- Missing `required_providers` in terraform block

---

### Scenario 2 — Terraform Validate

**Target file:** `demo/broken/validate.tf`

**Enable:** `RUN_TERRAFORM_VALIDATE=true` (all others `false`)

**What the bot finds:**
- `An argument named "unknown_field" is not expected here`

---

### Scenario 3 — Checkov

**Target files:** `demo/broken/storage/s3.tf`, `demo/broken/logging/cloudwatch.tf`

**Enable:** `RUN_CHECKOV_ANALYSIS=true` (all others `false`)

**What the bot finds:**
- `CKV_AWS_21` — S3 bucket versioning not enabled
- `CKV_AWS_18` — S3 bucket logging not enabled
- `CKV_AWS_19` — S3 bucket not encrypted with KMS
- `CKV_AWS_53/54/55/56` — Public access block not configured
- `CKV_AWS_338` — CloudWatch log group retention too short
- `CKV_AWS_158` — CloudWatch log group not encrypted with KMS

---

### Scenario 4 — TFSec

**Target file:** `demo/broken/network/ec2.tf`

**Enable:** `RUN_TFSEC_ANALYSIS=true` (all others `false`)

**What the bot finds:**
- `AVD-AWS-0105` — Security group ingress open to `0.0.0.0/0` on all ports
- `AVD-AWS-0107` — Ingress rule missing description

---

### Scenario 5 — Trivy

**Target file:** `demo/broken/storage/s3_trivy.tf`

**Enable:** `RUN_TRIVY_ANALYSIS=true` (all others `false`)

**What the bot finds:**
- `AVD-AWS-0094` — S3 bucket missing public access block
- `AVD-AWS-0132` — S3 bucket using AES256 instead of KMS
- `AVD-AWS-0090` — S3 bucket versioning not enabled

---

## Important: Run Stages One at a Time

> ⚠️ **Always enable only one stage at a time for demo purposes.**
>
> If multiple stages are enabled and one of them fails, all subsequent stages are skipped — only the first failing stage will upload findings to S3 and trigger the bot. Enable stages one at a time to ensure each tool gets a clean, isolated demo run.
>

---

## Advanced: Scanning Multiple Directories

`WORK_DIRS` supports comma-separated paths — the pipeline will scan each directory sequentially in a single run.

Example:

```yaml
env:
  WORK_DIRS: "terraform/main_module/,demo/broken/"
```

**What this shows:**
1. Pipeline scans `terraform/main_module/` — real infrastructure, all checks pass ✅
2. Pipeline scans `demo/broken/` — bot finds issues and posts AI suggestions ❌

This is useful for demonstrating that the bot can handle multiple directories at once and report findings per directory.

---

## Expected Demo Flow

```
WORK_DIRS = demo/broken/  →  pipeline FAILED  →  bot posts AI suggestions
                          →  bot list          →  shows affected files (incl. subdirectories)
                          →  bot approve all   →  bot commits fixes
                          →  pipeline re-runs  →  FAILED count reduced

WORK_DIRS = demo/fixed/   →  pipeline SUCCESS  →  bot: "No issues were found"
```

> ⚠️ **Do not run `bot list` after a green pipeline.**
>
> When the pipeline passes with no findings, the bot does not clear its stored file list from the previous failing run. If `bot list` is called after a successful run, it will return files from the last failure — not the current state. This is expected behavior, not a bug.
>
> Use `bot list` only when the pipeline has **failed** and the bot has posted AI suggestions.
