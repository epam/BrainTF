#!/usr/bin/env bash
# lib/config.sh — provide terraform tfvars/secrets for bootstrap and main_module.
# Sourced after common.sh; expects REPO_ROOT, MAIN_DIR, BOOTSTRAP_DIR.
#
# CONFIG_SOURCE=ssm   (default) pull the four files from SSM, same paths the
#                     deploy workflow uses. Every instance shares this config;
#                     per-instance values go through -var flags instead.
# CONFIG_SOURCE=local use the files already in the working tree (never pulled
#                     or overwritten — for offline work or custom tfvars).

config_pull() {
  case "${CONFIG_SOURCE:-ssm}" in
    ssm)
      log "Pulling tfvars + secrets from SSM (vcs: ${VCS_PROVIDER:-github})"
      local get
      get() { aws ssm get-parameter --name "$1" --with-decryption --query "Parameter.Value" --output text; }

      get "/Brain-TF/manual/${VCS_PROVIDER:-github}/bootstrap/terraform.tfvars"       > "$BOOTSTRAP_DIR/terraform.tfvars"
      get "/Brain-TF/manual/${VCS_PROVIDER:-github}/main_module/terraform.tfvars"     > "$MAIN_DIR/terraform.tfvars"
      get "/Brain-TF/manual/${VCS_PROVIDER:-github}/main_module/secrets.auto.tfvars"  > "$MAIN_DIR/secrets.auto.tfvars"
      get "/Brain-TF/manual/${VCS_PROVIDER:-github}/main_module/terraform.auto.tfvars" > "$MAIN_DIR/terraform.auto.tfvars"
      ;;
    local)
      log "Using local tfvars (CONFIG_SOURCE=local)"
      local f
      for f in terraform.tfvars secrets.auto.tfvars terraform.auto.tfvars; do
        [[ -s "$MAIN_DIR/$f" ]] || die "CONFIG_SOURCE=local: $MAIN_DIR/$f missing or empty"
      done
      ;;
    *)
      die "unknown CONFIG_SOURCE='${CONFIG_SOURCE}' (expected: ssm|local)"
      ;;
  esac
}
