#!/usr/bin/env bash
# lib/backend.sh — S3 backend for main_module. Sourced after common.sh;
# expects MAIN_DIR, STATE_BUCKET, STATE_REGION, STATE_KEY.
#
# backend.generated.tf is gitignored and normally produced by bootstrap; it is
# recreated here (same content the workflow writes) and the per-instance key is
# overridden at init.

backend_init() {
  cat > "$MAIN_DIR/backend.generated.tf" <<EOT
#======================= The Main module for application infrastructure =======================#
terraform {
  backend "s3" {
    bucket       = "${STATE_BUCKET}"
    key          = "main-module/terraform.tfstate"
    region       = "${STATE_REGION}"
    encrypt      = true
    use_lockfile = true
  }
}
EOT

  log "Terraform init (state: s3://${STATE_BUCKET}/${STATE_KEY})"
  terraform -chdir="$MAIN_DIR" init -input=false -reconfigure \
    -backend-config="key=${STATE_KEY}"
}
