#!/usr/bin/env bash
# lib/instance.sh — resolve instance identity. Sourced after common.sh; expects
# REPO_ROOT to point at the repository root.
#
# Produces these globals:
#   INSTANCE_ID    resource-name suffix and state key segment ("" only for prod)
#   STATE_KEY      S3 key of this instance's terraform state
#   TARGET_BRANCH  branch this instance serves ("" = personal instance / prod)
#   OWNER_GITHUB   GitHub login that owns this instance ("" only for prod)
#
# Resolution order for the instance ID:
#   1. $INSTANCE_ID already set in the environment ("prod" selects PROD)
#   2. a GitHub handle ($OWNER_GITHUB / $GITHUB_ACTOR / `gh api user`)
#   3. the current git branch, via .github/scripts/instance-id.sh
#
# The handle is used "as is" modulo AWS naming rules: lowercase [a-z0-9-],
# max 14 chars (the artifacts bucket name caps at 63).

sanitize_instance_id() {
  local raw="$1" id
  id="$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' | cut -c1-14)"
  id="${id%-}"
  [[ "$id" =~ ^[a-z0-9]([a-z0-9-]{0,12}[a-z0-9])?$ ]] || return 1
  printf '%s' "$id"
}

resolve_instance() {
  # The GitHub handle is kept verbatim (it must match issue.user.login in the
  # webhook payload); only the derived instance ID is sanitised.
  OWNER_GITHUB="${OWNER_GITHUB:-${GITHUB_ACTOR:-}}"
  if [[ -z "$OWNER_GITHUB" ]] && command -v gh >/dev/null 2>&1; then
    OWNER_GITHUB="$(gh api user --jq .login 2>/dev/null || true)"
  fi

  local mode
  if [[ "${INSTANCE_ID:-}" == "prod" ]]; then
    INSTANCE_ID=""
    TARGET_BRANCH=""
    OWNER_GITHUB=""
    mode="prod"
  elif [[ -n "${INSTANCE_ID:-}" ]]; then
    INSTANCE_ID="$(sanitize_instance_id "$INSTANCE_ID")" \
      || die "invalid INSTANCE_ID (lowercase letters, digits and '-', max 14 chars)"
    TARGET_BRANCH="${TARGET_BRANCH:-}"
    OWNER_GITHUB="${OWNER_GITHUB:-$INSTANCE_ID}"
    mode="explicit"
  elif [[ -n "$OWNER_GITHUB" ]]; then
    INSTANCE_ID="$(sanitize_instance_id "$OWNER_GITHUB")" \
      || die "cannot derive an instance ID from GitHub handle '$OWNER_GITHUB'"
    TARGET_BRANCH="${TARGET_BRANCH:-}"
    mode="personal"
  else
    local branch
    branch="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)" \
      || die "no INSTANCE_ID, no GitHub handle, and not in a git repo"
    INSTANCE_ID="$(bash "$REPO_ROOT/.github/scripts/instance-id.sh" "$branch")" \
      || die "cannot derive an instance ID from branch '$branch'; pass INSTANCE_ID=<id>"
    [[ "$INSTANCE_ID" == "prod" ]] \
      && die "on 'main' the derived ID is prod; pass INSTANCE_ID=prod explicitly"
    TARGET_BRANCH="${TARGET_BRANCH:-$branch}"
    OWNER_GITHUB="${OWNER_GITHUB:-$INSTANCE_ID}"
    mode="branch"
  fi

  [[ "$INSTANCE_ID" == "prod" ]] && die "instance ID 'prod' is reserved; use INSTANCE_ID=prod"

  if [[ -z "$INSTANCE_ID" ]]; then
    STATE_KEY="main-module/terraform.tfstate"
  else
    STATE_KEY="main-module/${INSTANCE_ID}/terraform.tfstate"
  fi

  case "$mode" in
    prod)     log "Instance: PROD (state: $STATE_KEY)" ;;
    personal) log "Instance: '${INSTANCE_ID}' — personal (owner: ${OWNER_GITHUB})" ;;
    branch)   log "Instance: '${INSTANCE_ID}' — branch '${TARGET_BRANCH}' (owner: ${OWNER_GITHUB})" ;;
    explicit) log "Instance: '${INSTANCE_ID}' — explicit (owner: ${OWNER_GITHUB}, branch: ${TARGET_BRANCH:-any})" ;;
  esac
}
