# Personal BrainTF Instances

A **personal instance** is a long-lived copy of BrainTF that a single developer
deploys to the shared AWS account to test the AI handler and the bot on their own
resources, without touching the PROD instance or anyone else's.

Every instance is namespaced by an **instance ID** (`var.instance_id`). For a
personal instance the ID is the developer's GitHub login (`github.actor`,
sanitised to lowercase `[a-z0-9-]`, max 14 chars). All instance-scoped resources
get the `-<instance_id>` suffix; the PROD instance keeps the un-suffixed names and
owns the account singletons (OIDC provider, shared role, repo-level CI variables),
which personal instances reuse.

| Resource | PROD (`instance_id=""`) | Personal (`instance_id=vasjr`) |
|---|---|---|
| Artifacts bucket | `ai-handler-artifacts-bucket-braintf-eu-central-1` | `...-braintf-eu-central-1-vasjr` |
| DynamoDB table | `ai-chat-history-braintf-eu-central-1` | `...-braintf-eu-central-1-vasjr` |
| Comment lambda | `AI_Handler_Comment_braintf` | `AI_Handler_Comment_braintf-vasjr` |
| SSM prefix | `/braintf/...` | `/braintf/vasjr/...` |
| State key | `main-module/terraform.tfstate` | `main-module/vasjr/terraform.tfstate` |
| OIDC provider / role | created & owned by PROD | reused (not recreated) |

The comment bot on a personal instance only answers pull requests **authored by
its owner** (`OWNER_GITHUB`, see `owner_github`), so each developer's instance
handles only their own PRs and there is no duplicate bot response between
personal instances.

## Safe test: deploy a personal instance without touching PROD

Deploying a suffixed personal instance is **non-destructive to PROD**: it uses a
different state key and different resource names, and it only *reads* the shared
OIDC provider that PROD created. The two operations that WOULD affect PROD —
applying this model to PROD's own state (`instance_id=""`) and migrating the
shared OIDC provider/role out of PROD — are never part of a personal deploy.

Prerequisite: an AWS session with write access to the account (e.g. `aws login`
or exported credentials) — the same identity you would use for any terraform
apply. Config (tfvars + secrets) is pulled from SSM exactly like the deploy
workflow does; set `CONFIG_SOURCE=local` to use local tfvars files instead.

1. Verify the plan touches only `-<your-id>` resources and nothing of PROD's:

   ```bash
   make plan INSTANCE_ID=<your-github-login>
   ```

   The plan must show only creations of `...-<your-github-login>` resources. If any
   un-suffixed PROD resource (e.g. `...-braintf-eu-central-1` with no suffix, the
   shared OIDC provider, or `/braintf/vcs_token`) appears as change/replace/destroy,
   stop — the ID is wrong or you are pointed at PROD's state key.

2. Apply once the plan is clean:

   ```bash
   make deploy INSTANCE_ID=<your-github-login>
   ```

3. Tear it down when done (PROD and shared singletons are left intact):

   ```bash
   make destroy INSTANCE_ID=<your-github-login>
   ```

`INSTANCE_ID` defaults to your GitHub handle (`gh api user`, or `GITHUB_ACTOR`
in CI) and is sanitised to lowercase `[a-z0-9-]` max 14 chars; `OWNER_GITHUB`
defaults to the same handle. Without a handle or an explicit ID, the instance
ID is derived from the current git branch (same rule as the deploy workflow),
and the instance serves that branch (`TARGET_BRANCH=<branch>`).

## What is shared and not isolated

- **OIDC provider and role** — one shared set per account; a personal instance
  reuses them (fine for testing; it does not create or delete them).
- **Repo-level CI variables** (`ARTIFACTS_BUCKET`, `OIDC_ROLE_ARN`, ...) — owned by
  PROD. The comment bot (webhook) path is isolated; the automatic
  "AI on Terraform errors" path driven by the CI pipeline uploads logs to PROD's
  artifacts bucket, so that specific path is not isolated per personal instance.
- **KMS key** — shared, un-suffixed (does not break isolation of data).
