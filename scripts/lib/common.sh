#!/usr/bin/env bash
# lib/common.sh — shared helpers sourced by deploy.sh / destroy.sh and lib/*.

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33mWARNING: %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[0;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }
