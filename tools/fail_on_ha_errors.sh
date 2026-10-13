#!/usr/bin/env bash
# Home Assistant's check_config logs blueprint and automation errors but can still
# exit 0. Pipe its output through this script to turn any logged error into a failure.
#   usage: <check_config command> 2>&1 | tools/fail_on_ha_errors.sh
set -uo pipefail
log="$(mktemp)"
sed 's/\x1b\[[0-9;]*m//g' | tee "$log"
if grep -qE '^(ERROR|CRITICAL)|Failed config|Invalid config|Failed to generate automation|generated invalid' "$log"; then
  echo "::error::Home Assistant config check reported errors (see above)"
  exit 1
fi
echo "Home Assistant config check: no errors"
