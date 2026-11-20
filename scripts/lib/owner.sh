#!/usr/bin/env bash
# lib/owner.sh — instance ownership marker next to the state object.
# Sourced after common.sh; expects STATE_BUCKET, STATE_KEY, TARGET_BRANCH,
# OWNER_GITHUB, INSTANCE_ID.
#
# Two contexts can derive the same instance ID (a branch and a developer handle
# can both sanitise to the same suffix). A marker object next to the state
# records who the instance belongs to, so a foreign deploy/destroy refuses
# instead of clobbering it. Marker content: the served branch for a branch
# instance, the owner handle for a personal one.

_owner_key() { printf '%s' "${STATE_KEY%/*}/owner"; }

# Prints the marker content, or nothing when absent. Any failure other than
# "not found" (e.g. AccessDenied) is an error, not "no owner".
owner_read() {
  local out
  if out="$(aws s3 cp "s3://${STATE_BUCKET}/$(_owner_key)" - 2>&1)"; then
    printf '%s' "$out"
    return 0
  fi
  if grep -qE "Not Found|NoSuchKey|404" <<<"$out"; then
    return 0
  fi
  printf '%s\n' "$out" >&2
  return 1
}

owner_expected() { printf '%s' "${TARGET_BRANCH:-$OWNER_GITHUB}"; }

owner_claim() {
  local owner expected
  owner="$(owner_read)" || die "cannot read the ownership marker"
  expected="$(owner_expected)"
  if [[ -n "$owner" && "$owner" != "$expected" ]]; then
    die "instance '${INSTANCE_ID}' belongs to '${owner}', not '${expected}'. Destroy it first or pick another ID."
  fi
  if [[ -z "$owner" ]]; then
    printf '%s' "$expected" | aws s3 cp - "s3://${STATE_BUCKET}/$(_owner_key)" --content-type text/plain \
      || die "cannot write the ownership marker"
    log "Instance '${INSTANCE_ID}' claimed for '${expected}'"
  fi
}

# Refuse to destroy an instance owned by someone else unless FORCE=1.
owner_check_destroy() {
  local owner expected
  owner="$(owner_read)" || die "cannot read the ownership marker"
  expected="$(owner_expected)"
  if [[ -n "$owner" && "$owner" != "$expected" && "${FORCE:-}" != "1" ]]; then
    die "instance '${INSTANCE_ID}' belongs to '${owner}', not '${expected}'. Re-run with FORCE=1 to destroy anyway."
  fi
}

owner_release() {
  aws s3 rm "s3://${STATE_BUCKET}/$(_owner_key)" >/dev/null 2>&1 || true
}
