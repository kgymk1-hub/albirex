"""Official site fetchers/parsers for safe CSV updates.

Only official Albirex Niigata and Albirex Niigata Ladies domains are used.
The parser is deliberately conservative: if a page cannot be fetched or parsed,
it logs that the official site is unavailable/unparseable and returns no changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

OFFICIAL_DOMAINS = {
    "men": "www.albirex.co.jp",
    "ladies": "albirex-niigata-ladies.com",
}

TEAM_CONFIG = {
    "men": {
        "name": "アルビレックス新潟",
        "base_url": "https://www.albirex.co.jp/",
        "player_urls": [
            "https://www.albirex.co.jp/team/player/",
            "https://www.albirex.co.jp/team/player/2026-27/",
        ],
        "news_urls": [
            "https://www.albirex.co.jp/news/",
            "https://www.albirex.co.jp/news/?category=1",
        ],
    },
    "ladies": {
        "name": "アルビレックス新潟レディース",
        "base_url": "https://albirex-niigata-ladies.com/",
        "player_urls": [
            "https://albirex-niigata-ladies.com/team/player/",
            "https://albirex-niigata-ladies.com/player/",
        ],
        "news_urls": [
            "https://albirex-niigata-ladies.com/news/",
        ],
    },
}

EVENT_KEYWORDS = {
    "期限付移籍延長": ["期限付き移籍期間延長", "期限付き移籍延長", "レンタル移籍延長"],
    "期限付移籍": ["期限付き移籍のお知らせ", "期限付き移籍移行"],
    "移籍": ["完全移籍", "移籍加入"],
    "契約満了": ["契約満了"],
    "契約更新": ["契約更新"],
    "復帰": ["復帰"],
    "退団": ["退団"],
    "引退": ["引退"],
    "加入": ["加入", "新加入", "内定"],
}

PLAYER_NAME_PATTERN = re.compile(r"([一-龥ぁ-んァ-ヶーA-Za-z]+(?:[ 　][一-龥ぁ-んァ-ヶーA-Za-z]+){0,3})")
DATE_PATTERN = re.compile(r"(20\d{2})[./年-](\d{1,2})[./月-](\d{1,2})")


@dataclass(frozen=True)
class OfficialPlayer:
    number: str
    position: str
    name: str
    source_url: str


@dataclass(frozen=True)
class OfficialEvent:
    player_name: str
    movement: str
    announced_on: str
    category: str
    club: str
    status: str
    source_url: str
    note: str


def _is_official_url(url: str, team: str) -> bool:
    return urlparse(url).netloc == OFFICIAL_DOMAINS[team]


def fetch_soup(url: str, team: str) -> BeautifulSoup | None:
    if not _is_official_url(url, team):
        print(f"公式サイト以外のURLをスキップ: {url}")
        return None
    try:
        response = requests.get(url, timeout=20, headers={"User-Agent": "albirex-offseason-csv-updater/1.0"})
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"公式サイト取得不可: {url}: {exc}")
        return None
    return BeautifulSoup(response.text, "html.parser")


def fetch_official_players(team: str) -> list[OfficialPlayer]:
    players: dict[str, OfficialPlayer] = {}
    for url in TEAM_CONFIG[team]["player_urls"]:
        soup = fetch_soup(url, team)
        if soup is None:
            continue
        parsed = _parse_players_from_soup(soup, url)
        if not parsed:
            print(f"解析不可: 選手一覧を取得できませんでした: {url}")
            continue
        for player in parsed:
            players.setdefault(player.name, player)
    return list(players.values())


def _parse_players_from_soup(soup: BeautifulSoup, source_url: str) -> list[OfficialPlayer]:
    results: list[OfficialPlayer] = []
    candidates = soup.select("article, li, .player, .player-list__item, .team-player, .card") or soup.find_all(["article", "li"])
    for node in candidates:
        text = " ".join(node.get_text(" ", strip=True).split())
        if len(text) < 2:
            continue
        number_match = re.search(r"(?:No\.?|背番号)?\s*(\d{1,2})", text, re.IGNORECASE)
        pos_match = re.search(r"\b(GK|DF|MF|FW)\b", text)
        name = _extract_name(text)
        if name and pos_match:
            results.append(OfficialPlayer(number_match.group(1) if number_match else "", pos_match.group(1), name, source_url))
    # Conservative de-duplication by player name.
    deduped: dict[str, OfficialPlayer] = {}
    for player in results:
        deduped.setdefault(player.name, player)
    return list(deduped.values())


def fetch_official_events(team: str, known_player_names: Iterable[str]) -> list[OfficialEvent]:
    known_names = set(known_player_names)
    events: dict[tuple[str, str, str, str], OfficialEvent] = {}
    for listing_url in TEAM_CONFIG[team]["news_urls"]:
        soup = fetch_soup(listing_url, team)
        if soup is None:
            continue
        links = _event_links(soup, listing_url, team)
        if not links:
            print(f"解析不可: ニュース一覧を取得できませんでした: {listing_url}")
            continue
        for title, url in links[:80]:
            category = _detect_category(title)
            if not category:
                continue
            article_soup = fetch_soup(url, team)
            article_text = title if article_soup is None else " ".join(article_soup.get_text(" ", strip=True).split())
            event = _build_event(title, article_text, category, url, known_names)
            if event:
                events.setdefault((event.player_name, event.movement, event.announced_on, event.category), event)
    return list(events.values())


def _event_links(soup: BeautifulSoup, listing_url: str, team: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for anchor in soup.find_all("a", href=True):
        title = " ".join(anchor.get_text(" ", strip=True).split())
        href = urljoin(listing_url, anchor["href"])
        if not title or not _is_official_url(href, team):
            continue
        if _detect_category(title):
            links.append((title, href))
    return links


def _detect_category(text: str) -> str | None:
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return event_type
    return None


def _normalize_event_category(event_type: str, title: str, article_text: str) -> str:
    text = f"{title} {article_text}"
    if event_type == "期限付移籍延長":
        if "から期限付き移籍" in text or "からの期限付き移籍" in text or "加入期間" in text:
            return "期限付移籍in延長"
        return "期限付移籍out延長"
    if event_type == "期限付移籍":
        if "期限付き移籍加入" in text or "育成型期限付き移籍加入" in text or "から期限付き移籍" in text:
            return "期限付移籍in"
        return "期限付移籍out"
    if event_type == "移籍":
        if "完全移籍加入" in text or "移籍加入" in text or "より完全移籍" in text or "から完全移籍" in text:
            return "移籍in"
        return "移籍out"
    if event_type == "復帰":
        return "期限付移籍out終了"
    if event_type == "加入":
        return "移籍in"
    return event_type


def _club_note(category: str, club: str) -> str:
    if not club:
        return "公式サイト確認"
    if category == "移籍in":
        return f"{club}より完全移籍加入"
    if category == "移籍out":
        return f"{club}へ完全移籍"
    if category == "期限付移籍in":
        return f"{club}より期限付き移籍加入"
    if category == "期限付移籍out":
        return f"{club}へ期限付き移籍"
    if category == "期限付移籍in延長":
        return f"{club}からの期限付き移籍期間を延長"
    if category == "期限付移籍out延長":
        return f"{club}への期限付き移籍期間を延長"
    if category == "期限付移籍out終了":
        return f"{club}への期限付き移籍より復帰" if club else "期限付き移籍out終了"
    return "公式サイト確認"


def _build_event(title: str, article_text: str, category: str, url: str, known_names: set[str]) -> OfficialEvent | None:
    player_name = _extract_known_name(title + " " + article_text, known_names) or _extract_name(title)
    if not player_name:
        return None
    category = _normalize_event_category(category, title, article_text)
    announced_on = _extract_date(article_text) or _extract_date(url)
    movement = category
    club = _extract_transfer_club(title, player_name, category)
    if category in {"契約更新", "移籍in", "期限付移籍in", "期限付移籍in延長", "期限付移籍out終了"}:
        status = "在籍予定"
    elif category in {"期限付移籍out", "期限付移籍out延長"}:
        status = "期限付き移籍中"
    elif category == "移籍out":
        status = "退団予定"
    else:
        status = category
    return OfficialEvent(player_name, movement, announced_on, category, club, status, url, _club_note(category, club))


def _extract_transfer_club(title: str, player_name: str, category: str) -> str:
    text = title.replace(player_name, "").replace("選手", "")
    if category in {"移籍out", "期限付移籍out", "期限付移籍out延長"}:
        match = re.search(r"(.+?)に", text) or re.search(r"(.+?)へ", text)
    elif category in {"移籍in", "期限付移籍in", "期限付移籍in延長", "期限付移籍out終了"}:
        match = re.search(r"(.+?)から", text) or re.search(r"(.+?)より", text)
    else:
        match = None
    if not match:
        return ""
    club = match.group(1).strip(" 　｜|-/")
    return re.sub(r"(完全移籍|期限付き移籍|復帰|加入|延長|のお知らせ).*$", "", club).strip(" 　｜|-/")


def _extract_known_name(text: str, known_names: set[str]) -> str | None:
    matches = [name for name in known_names if name and name in text]
    return max(matches, key=len) if matches else None


def _extract_name(text: str) -> str:
    cleaned = re.sub(r"(選手|契約|更新|加入|復帰|退団|引退|期限付き|完全移籍|のお知らせ|について).*$", "", text).strip(" 　｜|-/")
    match = PLAYER_NAME_PATTERN.search(cleaned)
    return match.group(1).strip() if match else ""


def _extract_date(text: str) -> str:
    match = DATE_PATTERN.search(text)
    if not match:
        return ""
    year, month, day = match.groups()
    try:
        return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
    except ValueError:
        return ""
