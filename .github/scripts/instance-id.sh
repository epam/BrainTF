#!/usr/bin/env bash
# Derive the BrainTF instance ID (the resource-name suffix and Terraform state
# key segment) from a git branch name.
#
#   main                                         -> prod
#   feature/EPMCACMAWS-504-automated-deployment  -> epmcacmaws-504
#   fix/some-very-long-branch-name               -> fix-some-v-<4 hex of sha1(branch)>
#
# The ID is appended to the S3 artifacts bucket name (48-char base + "-" + ID),
# which has a 63-char limit, so it is capped at 14 characters.
#
# Usage: instance-id.sh <branch>
# Prints the ID on stdout. Exits non-zero (message on stderr) if no valid ID
# can be derived.
set -euo pipefail

MAX_LEN=14
HASH_LEN=4

branch="${1:-}"
if [[ -z "$branch" ]]; then
  echo "usage: instance-id.sh <branch>" >&2
  exit 2
fi

sha1_hex() {
  if command -v sha1sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha1sum | cut -d' ' -f1
  else
    printf '%s' "$1" | shasum -a 1 | cut -d' ' -f1
  fi
}

if [[ "$branch" == "main" ]]; then
  echo "prod"
  exit 0
fi

id=""
# Prefer a Jira ticket key: it maps an instance to its ticket. Jira project keys
# are upper case with at least two characters; requiring that keeps ordinary
# words ("step-1", "v-2") from being mistaken for a ticket. Two branches that
# carry the same ticket still share an ID: the workflows refuse to deploy to or
# auto-destroy an instance owned by another branch.
if [[ "$branch" =~ ([[:upper:]][[:upper:][:digit:]]+-[[:digit:]]+) ]]; then
  id="$(printf '%s' "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')"
fi

# No ticket key, or it does not fit: sanitized prefix + hash of the full branch,
# so two long branches that share a prefix still get different IDs.
if [[ -z "$id" || ${#id} -gt $MAX_LEN ]]; then
  slug="$(printf '%s' "$branch" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
  hash="$(sha1_hex "$branch" | cut -c1-"$HASH_LEN")"
  head="${slug:0:$((MAX_LEN - HASH_LEN - 1))}"
  head="${head%-}"
  if [[ -n "$head" ]]; then
    id="${head}-${hash}"
  else
    id="$hash"
  fi
fi

if [[ "$id" == "prod" ]] || ! [[ "$id" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] || (( ${#id} > MAX_LEN )); then
  echo "cannot derive a valid instance ID from branch '$branch' (got '$id')" >&2
  exit 1
fi

echo "$id"
