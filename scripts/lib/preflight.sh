#!/usr/bin/env bash
# lib/preflight.sh — fail fast BEFORE terraform init/plan/apply/destroy.
# Sourced after common.sh; expects MAIN_DIR.
#
# Tokens are checked for non-emptiness: vcs_token/ai_token default to "" in
# variables.tf, so Terraform would NOT prompt for them — it would run silently
# with an empty token (the GitHub provider then 404s on the repo).

_pf_missing=0

_pf_pass() { printf '  \033[0;32m*\033[0m %s\n' "$1"; }
_pf_fail() { printf '  \033[0;31m*\033[0m %s\n' "$1"; _pf_missing=1; }
_pf_warn() { printf '  \033[0;33m*\033[0m %s\n' "$1"; }

_pf_tool() {
  if command -v "$1" >/dev/null 2>&1; then
    _pf_pass "tool: $1"
  else
    _pf_fail "tool: $1 — NOT FOUND"
  fi
}

# Value of `key = "..."` in a tfvars file (empty for missing/empty).
_pf_tfvars_val() { sed -nE "s/^[[:space:]]*$2[[:space:]]*=[[:space:]]*\"?([^\"]*)\"?.*/\1/p" "$1" | head -n1; }

preflight() {
  _pf_tool terraform
  _pf_tool aws

  if aws sts get-caller-identity >/dev/null 2>&1; then
    _pf_pass "AWS credentials (account $(aws sts get-caller-identity --query Account --output text 2>/dev/null))"
  else
    _pf_fail "AWS credentials — sts:GetCallerIdentity failed (log in with 'aws login' or export credentials)"
  fi

  local f
  for f in terraform.tfvars terraform.auto.tfvars secrets.auto.tfvars; do
    if [[ -s "$MAIN_DIR/$f" ]]; then
      _pf_pass "file: main_module/$f"
    else
      _pf_fail "file: main_module/$f — missing or empty (config step should have provided it)"
    fi
  done

  # Secrets: an exported TF_VAR_* wins; otherwise a non-empty value inside
  # secrets.auto.tfvars.
  local env_name key_name val pair
  for pair in "TF_VAR_vcs_token:vcs_token" "TF_VAR_ai_token:ai_token" "TF_VAR_job_token:job_token"; do
    env_name="${pair%%:*}"; key_name="${pair##*:}"; val="${!env_name:-}"
    if [[ -z "$val" && -s "$MAIN_DIR/secrets.auto.tfvars" ]]; then
      val="$(_pf_tfvars_val "$MAIN_DIR/secrets.auto.tfvars" "$key_name")"
    fi
    # job_token also lives in terraform.tfvars on GitHub setups (GitLab-only var
    # still needs SOME value); accept it from either file.
    if [[ -z "$val" && -s "$MAIN_DIR/terraform.tfvars" ]]; then
      val="$(_pf_tfvars_val "$MAIN_DIR/terraform.tfvars" "$key_name")"
    fi
    if [[ -n "$val" ]]; then
      _pf_pass "secret: $key_name (<set>)"
    else
      _pf_fail "secret: $key_name — missing (TF_VAR_${key_name} or a tfvars file)"
    fi
  done

  if [[ "$_pf_missing" != "0" ]]; then
    printf '\n\033[0;31mPreflight failed: fix the items marked red and re-run.\033[0m\n' >&2
    exit 1
  fi
}
