#!/usr/bin/env bash
# deploy.sh — deploy one BrainTF instance (prod, per-branch, or personal).
#
# Same steps as the deploy job in .github/workflows/deploy-braintf.yml, runnable
# locally under your own AWS login ('aws login' / exported credentials) or from
# CI. All per-instance values arrive as env vars -var flags; the shared config
# (tfvars + secrets) comes from SSM by default.
#
# Env:
#   INSTANCE_ID=<id>   instance suffix ("prod" for the PROD instance).
#                      Default: GitHub handle ($OWNER_GITHUB / GITHUB_ACTOR /
#                      `gh api user`), else derived from the current branch.
#   OWNER_GITHUB=<l>   GitHub login owning the instance (comment-bot author
#                      filter + OwnerGithub tag). Default: the ID's handle.
#   TARGET_BRANCH=<b>  branch this instance serves (branch instances only;
#                      default "" = personal instance answering all of the
#                      owner's PRs).
#   CONFIG_SOURCE=ssm|local   pull tfvars+secrets from SSM (default) or use the
#                             files already in terraform/main_module.
#   VCS_PROVIDER=github|gitlab (default: github — selects the SSM path)
#   STATE_BUCKET / STATE_REGION  state backend (defaults match the workflows)
#   PLAN_ONLY=1        plan only, create nothing
#   AUTO_APPROVE=1     apply the saved plan without a prompt (it never prompts
#                      anyway; kept for interface parity)
#
# Usage:
#   ./scripts/deploy.sh INSTANCE_ID=vasjr     # or: INSTANCE_ID=vasjr ./scripts/deploy.sh
#   PLAN_ONLY=1 ./scripts/deploy.sh           # dry run
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN_DIR="${REPO_ROOT}/terraform/main_module"
BOOTSTRAP_DIR="${REPO_ROOT}/terraform/bootstrap"
STATE_BUCKET="${STATE_BUCKET:-backend-state-bucket-braintf-eu-central-1}"
STATE_REGION="${STATE_REGION:-eu-central-1}"

# shellcheck source=lib/common.sh
source "${REPO_ROOT}/scripts/lib/common.sh"
# shellcheck source=lib/instance.sh
source "${REPO_ROOT}/scripts/lib/instance.sh"
# shellcheck source=lib/config.sh
source "${REPO_ROOT}/scripts/lib/config.sh"
# shellcheck source=lib/backend.sh
source "${REPO_ROOT}/scripts/lib/backend.sh"
# shellcheck source=lib/owner.sh
source "${REPO_ROOT}/scripts/lib/owner.sh"
# shellcheck source=lib/preflight.sh
source "${REPO_ROOT}/scripts/lib/preflight.sh"

# NAME=value args are also accepted (./scripts/deploy.sh INSTANCE_ID=x)
for arg in "$@"; do
  case "$arg" in
    *=*) export "$arg" ;;
    *) die "unexpected argument '$arg' (use NAME=value)" ;;
  esac
done

resolve_instance
config_pull

log "Preflight check"
preflight

backend_init

# Claim the instance before the first apply, so a half-built instance is owned
# too (prod never claims; it is the primary singleton owner).
if [[ -n "$INSTANCE_ID" ]]; then
  owner_claim
fi

# -var outranks the tfvars files. Prod keeps its own Environment tag from
# tfvars; a suffixed instance is tagged with its ID.
log "Planning terraform/main_module"
ARGS=(
  -var="instance_id=${INSTANCE_ID}"
  -var="target_branch=${TARGET_BRANCH}"
  -var="owner_github=${OWNER_GITHUB}"
)
[[ -n "$INSTANCE_ID" ]] && ARGS+=(-var="environment=${INSTANCE_ID}")

terraform -chdir="$MAIN_DIR" plan -input=false "${ARGS[@]}" -out=tfplan

if [[ "${PLAN_ONLY:-}" == "1" ]]; then
  log "PLAN_ONLY=1 — plan saved at $MAIN_DIR/tfplan, nothing applied."
  exit 0
fi

log "Applying terraform/main_module"
terraform -chdir="$MAIN_DIR" apply -input=false tfplan

log "Done. Instance '${INSTANCE_ID:-prod}' deployed (state: s3://${STATE_BUCKET}/${STATE_KEY})."
