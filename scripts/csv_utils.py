"""CSV helpers for Albirex offseason source data.

These helpers intentionally preserve the repository CSV headers and avoid
rewriting files unless their logical row content changes.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

PLAYERS_HEADER = ["背番号", "ポジション", "選手名", "その他備考"]
EVENTS_HEADER = ["選手名", "動向", "発表日", "区分", "移籍先元", "ステータス", "出典URL", "その他備考"]
ALLOWED_EVENT_CATEGORIES = {
    "契約更新",
    "復帰",
    "移籍in",
    "移籍out",
    "期限付移籍in",
    "期限付移籍out",
    "期限付移籍in延長",
    "期限付移籍out延長",
    "契約満了",
    "引退",
    "未発表",
}


def read_csv_dicts(path: Path, expected_header: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_header:
            raise ValueError(f"CSVヘッダー不正: {path}: {reader.fieldnames!r}")
        return [{key: (row.get(key) or "") for key in expected_header} for row in reader]


def write_csv_dicts_if_changed(path: Path, header: list[str], rows: Iterable[dict[str, str]]) -> bool:
    normalized_rows = [{key: (row.get(key) or "") for key in header} for row in rows]
    existing_rows = read_csv_dicts(path, header)
    if existing_rows == normalized_rows:
        return False

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized_rows)
    return True


def validate_event_categories(rows: Iterable[dict[str, str]], path: Path) -> None:
    invalid = sorted({row.get("区分", "") for row in rows if row.get("区分", "") not in ALLOWED_EVENT_CATEGORIES})
    if invalid:
        raise ValueError(f"区分マスタ外の値があります: {path}: {invalid}")


def event_identity(row: dict[str, str]) -> tuple[str, str, str, str]:
    """Identity used to avoid duplicate official event rows."""

    return (
        row.get("選手名", ""),
        row.get("動向", ""),
        row.get("発表日", ""),
        row.get("区分", ""),
    )
