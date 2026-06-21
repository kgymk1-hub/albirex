#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORTS_DIR="$ROOT_DIR/exports"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

shopt -s nullglob
workbooks=("$EXPORTS_DIR"/*.xlsx)
if (( ${#workbooks[@]} == 0 )); then
  echo "No Excel files found in $EXPORTS_DIR" >&2
  exit 1
fi

for workbook in "${workbooks[@]}"; do
  base_name="$(basename "$workbook" .xlsx)"
  tmp_xlsx="$TMP_DIR/${base_name}.xlsx"

  # Create a temporary workbook that contains only the mobile sheet before PDF export.
  python "$ROOT_DIR/scripts/prepare_pdf_workbook.py" "$workbook" "$tmp_xlsx"

  libreoffice --headless --convert-to pdf --outdir "$TMP_DIR" "$tmp_xlsx"
  pdf_path="$TMP_DIR/${base_name}.pdf"
  if [[ ! -f "$pdf_path" ]]; then
    echo "PDF conversion failed for $workbook" >&2
    exit 1
  fi
  mv "$pdf_path" "$EXPORTS_DIR/${base_name}.pdf"
done
