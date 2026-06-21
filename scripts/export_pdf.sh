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
  cp "$workbook" "$tmp_xlsx"

  # Create a temporary workbook for PDF export that contains only the mobile sheet.
  python - "$tmp_xlsx" <<'PY'
from pathlib import Path
import sys
from openpyxl import load_workbook

path = Path(sys.argv[1])
wb = load_workbook(path)
if "スマホ表示" not in wb.sheetnames:
    raise SystemExit(f"スマホ表示 sheet is missing: {path}")
for sheet_name in list(wb.sheetnames):
    if sheet_name != "スマホ表示":
        del wb[sheet_name]
wb.active = 0
wb.save(path)
PY

  libreoffice --headless --convert-to pdf --outdir "$TMP_DIR" "$tmp_xlsx"
  pdf_path="$TMP_DIR/${base_name}.pdf"
  if [[ ! -f "$pdf_path" ]]; then
    echo "PDF conversion failed for $workbook" >&2
    exit 1
  fi
  mv "$pdf_path" "$EXPORTS_DIR/${base_name}.pdf"
done
