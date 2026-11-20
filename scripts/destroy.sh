#!/usr/bin/env bash
# destroy.sh — tear down one BrainTF instance (never prod).
#
# Same steps as .github/workflows/destroy-braintf.yml, runnable locally under
# your own AWS login. Requires an explicit INSTANCE_ID — an operator naming the
# instance, like a manual workflow run with instance_id set.
#
# Env:
#   INSTANCE_ID=<id>   REQUIRED. The instance suffix to destroy ("prod" refused).
#   OWNER_GITHUB=<l>   expected owner for the marker check (default: INSTANCE_ID)
#   TARGET_BRANCH=<b>  expected branch for the marker check
#   FORCE=1            destroy even when the owner marker names someone else
#   CONFIG_SOURCE=ssm|local   (default: ssm)
#   VCS_PROVIDER, STATE_BUCKET, STATE_REGION — as in deploy.sh
#   AUTO_APPROVE=1     non-interactive destroy
#
# Usage:
#   ./scripts/destroy.sh INSTANCE_ID=vasjr
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

for arg in "$@"; do
  case "$arg" in
    *=*) export "$arg" ;;
    *) die "unexpected argument '$arg' (use NAME=value)" ;;
  esac
done

[[ -n "${INSTANCE_ID:-}" && "${INSTANCE_ID}" != "prod" ]] \
  || die "INSTANCE_ID is required and must not be 'prod' (the prod instance is never destroyed by this script)."

resolve_instance
config_pull

log "Preflight check"
preflight

backend_init

log "Checking instance state (s3://${STATE_BUCKET}/${STATE_KEY})"
if out="$(aws s3api head-object --bucket "$STATE_BUCKET" --key "$STATE_KEY" 2>&1)"; then
  :
elif grep -qE "Not Found|NoSuchKey|404" <<<"$out"; then
  log "No state at s3://${STATE_BUCKET}/${STATE_KEY}; releasing the owner marker if any."
  owner_release
  log "Nothing to destroy."
  exit 0
else
  printf '%s\n' "$out" >&2
  die "cannot check the state object"
fi

owner_check_destroy

log "Destroying terraform/main_module (instance '${INSTANCE_ID}')"
DESTROY_ARGS=(-input=false -var="instance_id=${INSTANCE_ID}" -var="environment=${INSTANCE_ID}" -var="target_branch=${TARGET_BRANCH}")
[[ "${AUTO_APPROVE:-}" == "1" ]] && DESTROY_ARGS+=(-auto-approve)
terraform -chdir="$MAIN_DIR" destroy "${DESTROY_ARGS[@]}"

# Only drop the state once nothing is left in it, so a partial destroy can be
# retried instead of orphaning resources.
if [[ -n "$(terraform -chdir="$MAIN_DIR" state list)" ]]; then
  die "state for '${INSTANCE_ID}' still tracks resources; keeping it (re-run to continue)."
fi
aws s3 rm "s3://${STATE_BUCKET}/${STATE_KEY}"

owner_release
log "Done. Instance '${INSTANCE_ID}' destroyed."
