#!/usr/bin/env bash
# Assemble a throwaway Home Assistant config that loads every blueprint and every
# example package, so Home Assistant's own config check can validate them.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/.ci/config}"
rm -rf "$OUT"; mkdir -p "$OUT/packages" "$OUT/blueprints"
cp -R "$ROOT/blueprints/." "$OUT/blueprints/"
for f in "$ROOT"/packages/examples/*.yaml; do
  name="$(basename "$f" .yaml)"; cp "$f" "$OUT/packages/${name//./_}.yaml"
done
cat > "$OUT/configuration.yaml" <<'YAML'
homeassistant:
  name: CI
  latitude: 12.97
  longitude: 77.59
  elevation: 900
  unit_system: metric
  time_zone: Asia/Kolkata
  packages: !include_dir_named packages
YAML
echo "test config written to $OUT"
