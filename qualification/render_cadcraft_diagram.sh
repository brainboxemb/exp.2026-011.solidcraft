#!/usr/bin/env bash
set -euo pipefail

PLAN="${1:?usage: render_cadcraft_diagram.sh PLAN OUT_DIR [NAME]}"
OUT_DIR="${2:?usage: render_cadcraft_diagram.sh PLAN OUT_DIR [NAME]}"
NAME="${3:-$(basename "$PLAN" .cadcraft.json)}"

mkdir -p "$OUT_DIR"

mapfile -t COMMANDS < <(
  jq -cr '.commands[] | .command + " " + (.params | tojson)' "$PLAN"
)

ARGS=(run --metric)
for command in "${COMMANDS[@]}"; do
  ARGS+=(--cmd "$command")
done

CADCRAFT_CONFIG_DIR="" cadcraft-cli "${ARGS[@]}" \
  --save "$OUT_DIR/$NAME.dxf" \
  --export "$OUT_DIR/$NAME.svg" \
  --view extents

test -s "$OUT_DIR/$NAME.dxf"
test -s "$OUT_DIR/$NAME.svg"
