#!/usr/bin/env python3
"""Build Albirex Niigata offseason workbooks from CSV source da

This script is intended to run in GitHub Actions. It creates new Excel
workbooks from CSV source data and does not read, edit, or overwrite the
legacy reference .xlsx files in the repository root

"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
EXPORTS_ROOT = ROOT / "exports"

PLAYER_HEADERS = ["背番号", "ポジション", "氏名", "備考"]
EVENT_HEADERS = ["氏名", "動向", "発表日", "区分", "移籍先元", "ステータス", "出典URL", "備考"]
MOBILE_HEADERS = ["背番号", "ポジション", "氏名", "動向", "発表日", "区分", "移籍先/元", "ステータス", "出典URL"]
LOG_HEADERS = ["確認日", "対象", "確認内容", "結果", "備考"]

CATEGORY_MASTER = [
    ("契約更新", "残留系", "薄い緑"),
    ("加入", "加入系", "薄い青"),
    ("復帰", "加入系", "薄い青"),
    ("期限付き移籍加入", "加入系", "薄い青"),
    ("期限付き移籍延長", "加入系", "薄い青"),
    ("退団", "退団系", "薄い橙"),
    ("契約満了", "退団系", "薄い橙"),
    ("引退", "退団系", "薄い橙"),
    ("未発表", "未発表", "薄い黄"),
]

COLOR_MAP = {
    "薄い緑": "E2F0D9",
    "薄い青": "DDEBF7",
    "薄い橙": "FCE4D6",
    "薄い黄": "FFF2CC",
}

WORKBOOKS = {
    "men": "albirex_niigata_men_2026_27_offseason_print_mobile.xlsx",
    "ladies": "albirex_niigata_ladies_2026_27_offseason_print_mobile.xlsx",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))



def append_table(ws, headers: list[str], rows: Iterable[Iterable[str]]) -> None:
    ws.append(headers)
    for row in rows:
        ws.append(list(row))
    style_header(ws)
    ws.auto_filter.ref = ws.dimensions


def style_header(ws) -> None:
    fill = PatternFill("solid", fgColor="D9EAF7")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def set_widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def build_mobile_rows(players: list[dict[str, str]], events: list[dict[str, str]]) -> list[list[str]]:

    events_by_name = {event.get("氏名", ""): event for event in events if event.get("氏名")}
    rows = []
    for player in players:
        event = events_by_name.get(player.get("氏名", ""), {})
        category = event.get("区分", "") or "未発表"
        movement = event.get("動向", "") or ("―" if category == "未発表" else category)
        status = event.get("ステータス", "") or ("確認中" if category == "未発表" else "")
        rows.append([
            player.get("背番号", ""),
            player.get("ポジション", ""),
            player.get("氏名", ""),
            movement,
            event.get("発表日", ""),
            category,
            event.get("移籍先元", ""),
            status,
            event.get("出典URL", ""),
        ])
    return rows


def setup_mobile_sheet(ws, rows: list[list[str]]) -> None:
    append_table(ws, MOBILE_HEADERS, rows)
    max_row = max(ws.max_row, 1)
    ws.freeze_panes = "A2"
    ws.print_title_rows = "1:1"
    ws.print_area = f"A1:E{max_row}"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = 0.25
    ws.page_margins.right = 0.25
    ws.page_margins.top = 0.5
    ws.page_margins.bottom = 0.5
    ws.page_margins.header = 0.2
    ws.page_margins.footer = 0.2
    ws.row_dimensions[1].height = 24
    for row_number in range(2, max_row + 1):
        ws.row_dimensions[row_number].height = 30
    set_widths(ws, {"A": 7, "B": 9, "C": 18, "D": 16, "E": 12, "F": 14, "G": 18, "H": 14, "I": 12})
    for column in ("F", "G", "H", "I"):
        ws.column_dimensions[column].hidden = True
    for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=9):
        for cell in row:
            cell.alignment = Alignment(vertical="center", wrap_text=True)
    apply_conditional_formatting(ws, max_row)


def apply_conditional_formatting(ws, max_row: int) -> None:
    if max_row < 2:
        return
    rules_by_color: dict[str, list[str]] = {}
    for category, _group, color_name in CATEGORY_MASTER:
        rules_by_color.setdefault(COLOR_MAP[color_name], []).append(category)
    for color, categories in rules_by_color.items():
        quoted = ",".join(f'"{category}"' for category in categories)
        formula = f'OR(ISNUMBER(MATCH($D2,{{{quoted}}},0)),ISNUMBER(MATCH($F2,{{{quoted}}},0)))'
        fill = PatternFill("solid", fgColor=color)
        ws.conditional_formatting.add(f"A2:I{max_row}", FormulaRule(formula=[formula], fill=fill))


def setup_simple_sheet(ws, headers: list[str], rows: list[list[str]], widths: dict[str, float] | None = None) -> None:

    append_table(ws, headers, rows)
    ws.freeze_panes = "A2"
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="center", wrap_text=True)
    if widths:
        set_widths(ws, widths)


def build_workbook(team_key: str, output_name: str) -> None:
    players = read_csv(DATA_ROOT / team_key / "players.csv")
    events = read_csv(DATA_ROOT / team_key / "official_events.csv")

    wb = Workbook()
    wb.remove(wb.active)

    mobile_ws = wb.create_sheet("スマホ表示")
    setup_mobile_sheet(mobile_ws, build_mobile_rows(players, events))

    players_ws = wb.create_sheet("選手マスタ")
    setup_simple_sheet(players_ws, PLAYER_HEADERS, ([row.get(header, "") for header in PLAYER_HEADERS] for row in players), {"A": 8, "B": 12, "C": 22, "D": 30})

    events_ws = wb.create_sheet("オフ動向_入力")
    setup_simple_sheet(events_ws, EVENT_HEADERS, ([row.get(header, "") for header in EVENT_HEADERS] for row in events), {"A": 22, "B": 18, "C": 12, "D": 18, "E": 24, "F": 14, "G": 40, "H": 30})

    category_ws = wb.create_sheet("区分マスタ")
    setup_simple_sheet(category_ws, ["区分", "分類", "色"], CATEGORY_MASTER, {"A": 20, "B": 14, "C": 12})

    log_ws = wb.create_sheet("確認ログ")
    setup_simple_sheet(log_ws, LOG_HEADERS, [], {"A": 14, "B": 24, "C": 36, "D": 18, "E": 30})

    memo_ws = wb.create_sheet("メモ")
    memo_rows = [
        ["このExcelファイルは直接編集せず、dataフォルダ内のCSVを更新してGitHub Actionsで再生成する。"],
        ["スマホ表示シートの印刷範囲は A:E とする。"],
        ["F列以降は管理用情報であり、印刷対象外とする。"],
    ]
    setup_simple_sheet(memo_ws, ["運用上の注意点"], memo_rows, {"A": 90})

    EXPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    wb.save(EXPORTS_ROOT / output_name)


def main() -> None:
    for team_key, output_name in WORKBOOKS.items():
        build_workbook(team_key, output_name)


if __name__ == "__main__":
    main()
