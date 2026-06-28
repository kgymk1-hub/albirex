#!/usr/bin/env python3
"""Update Albirex offseason CSV files from official sites only.

This script is safe by design:
- it only fetches official Albirex Niigata / Ladies domains;
- it never deletes existing CSV rows;
- it leaves existing values untouched when official pages are unavailable or
  cannot be parsed;
- it adds official event rows only when an official announcement is detected.
"""

from __future__ import annotations

from pathlib import Path
import sys

from csv_utils import EVENTS_HEADER, PLAYERS_HEADER, event_identity, read_csv_dicts, validate_event_categories, write_csv_dicts_if_changed
from official_sources import fetch_official_events, fetch_official_players

ROOT = Path(__file__).resolve().parents[1]
TEAMS = {
    "men": {
        "players": ROOT / "data/men/players.csv",
        "events": ROOT / "data/men/official_events.csv",
    },
    "ladies": {
        "players": ROOT / "data/ladies/players.csv",
        "events": ROOT / "data/ladies/official_events.csv",
    },
}


def sort_player_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    def sort_key(item: tuple[int, dict[str, str]]) -> tuple[int, int]:
        original_index, row = item
        number = row.get("背番号", "")
        return (0, int(number)) if number.isdigit() else (1, original_index)

    return [row for _, row in sorted(enumerate(rows), key=sort_key)]


def update_players(path: Path, team: str) -> tuple[list[dict[str, str]], bool]:
    rows = read_csv_dicts(path, PLAYERS_HEADER)
    by_name = {row["選手名"]: row for row in rows}
    official_players = fetch_official_players(team)
    if not official_players:
        print(f"解析不可: {team} の選手一覧更新をスキップし、既存CSVを維持します")
        return rows, False

    changed = False
    for player in official_players:
        if not player.name:
            continue
        if player.name in by_name:
            row = by_name[player.name]
            # Update only fields explicitly confirmed on the official site.
            for csv_key, official_value in (("背番号", player.number), ("ポジション", player.position)):
                if official_value and row.get(csv_key, "") != official_value:
                    row[csv_key] = official_value
                    changed = True
        else:
            rows.append({
                "背番号": player.number,
                "ポジション": player.position,
                "選手名": player.name,
                "その他備考": "公式プロフィール掲載確認",
            })
            changed = True

    sorted_rows = sort_player_rows(rows)
    return sorted_rows, write_csv_dicts_if_changed(path, PLAYERS_HEADER, sorted_rows) if changed or sorted_rows != rows else False


def update_events(path: Path, team: str, player_rows: list[dict[str, str]]) -> bool:
    rows = read_csv_dicts(path, EVENTS_HEADER)
    validate_event_categories(rows, path)
    official_events = fetch_official_events(team, [row["選手名"] for row in player_rows])
    if not official_events:
        print(f"解析不可: {team} の公式発表更新をスキップし、既存CSVを維持します")
        return False

    identities = {event_identity(row) for row in rows}
    changed = False
    for event in official_events:
        new_row = {
            "選手名": event.player_name,
            "動向": event.movement,
            "発表日": event.announced_on,
            "区分": event.category,
            "移籍先元": event.club,
            "ステータス": event.status,
            "出典URL": event.source_url,
            "その他備考": event.note,
        }
        if event_identity(new_row) in identities:
            continue
        rows.append(new_row)
        identities.add(event_identity(new_row))
        changed = True

    validate_event_categories(rows, path)
    return changed and write_csv_dicts_if_changed(path, EVENTS_HEADER, rows)


def main() -> int:
    changed_paths: list[str] = []
    for team, paths in TEAMS.items():
        player_rows, players_changed = update_players(paths["players"], team)
        if players_changed:
            changed_paths.append(str(paths["players"].relative_to(ROOT)))
        events_changed = update_events(paths["events"], team, player_rows)
        if events_changed:
            changed_paths.append(str(paths["events"].relative_to(ROOT)))

    if changed_paths:
        print("CSV updated from official sites:")
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("公式サイト確認完了: CSV変更なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
