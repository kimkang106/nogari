"""
fetch_notion.py
GitHub Actions에서 실행 — Notion DB를 data.json으로 변환

환경변수 (GitHub Secrets에서 주입):
  NOTION_API_KEY       : secret_xxx...
  NOTION_DATABASE_ID   : 32자리 DB ID
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

API_KEY = os.environ["NOTION_API_KEY"]
DB_ID   = os.environ["NOTION_DATABASE_ID"]

HEADERS = {
    "Authorization":  f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type":   "application/json",
}

KST = timezone(timedelta(hours=9))


def query_database(db_id: str) -> list:
    """데이터베이스 전체 쿼리 (페이지네이션 지원)"""
    url     = f"https://api.notion.com/v1/databases/{db_id}/query"
    results = []
    payload = {
        "sorts": [{"property": "날짜", "direction": "descending"}],
        "page_size": 100,
    }

    while True:
        res = requests.post(url, headers=HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()
        results.extend(data.get("results", []))

        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return results


def get_title(prop) -> str:
    if not prop:
        return "제목 없음"
    texts = prop.get("title", [])
    return "".join(t.get("plain_text", "") for t in texts) or "제목 없음"


def get_rich_text(prop) -> str:
    if not prop:
        return ""
    texts = prop.get("rich_text", [])
    return "\n".join(t.get("plain_text", "") for t in texts)


def get_select(prop) -> str:
    if not prop:
        return ""
    if prop.get("type") == "select" and prop.get("select"):
        return prop["select"]["name"]
    if prop.get("type") == "multi_select":
        return ", ".join(s["name"] for s in prop.get("multi_select", []))
    return ""


def get_date(prop) -> str:
    if not prop or prop.get("type") != "date":
        return ""
    d = prop.get("date")
    return d["start"] if d else ""


def get_url(prop) -> str:
    if not prop:
        return ""
    if prop.get("type") == "url":
        return prop.get("url") or ""
    if prop.get("type") == "files":
        files = prop.get("files", [])
        if files:
            f = files[0]
            if f.get("type") == "external":
                return f["external"]["url"]
            elif f.get("type") == "file":
                return f["file"]["url"]
    return ""


def get_page_cover(page: dict) -> str:
    cover = page.get("cover")
    if not cover:
        return ""
    if cover["type"] == "external":
        return cover["external"]["url"]
    if cover["type"] == "file":
        return cover["file"]["url"]
    return ""


def parse_page(page: dict) -> dict:
    props = page.get("properties", {})

    # 속성명 후보 (한/영 모두 대응)
    title_prop  = props.get("제목") or props.get("이름") or props.get("Name") or props.get("title") or {}
    desc_prop   = props.get("설명") or props.get("Description") or {}
    tag_prop    = props.get("태그") or props.get("Tag") or props.get("카테고리") or props.get("Category") or {}
    date_prop   = props.get("날짜") or props.get("Date") or {}
    cover_prop  = props.get("커버이미지") or props.get("Cover") or props.get("이미지") or props.get("Image") or {}

    cover_image = get_url(cover_prop) or get_page_cover(page)

    icon = page.get("icon", {})
    emoji = icon.get("emoji", "📄") if icon and icon.get("type") == "emoji" else "📄"

    return {
        "id":          page["id"],
        "notionUrl":   page.get("url", ""),
        "title":       get_title(title_prop),
        "description": get_rich_text(desc_prop),
        "tag":         get_select(tag_prop),
        "date":        get_date(date_prop),
        "coverImage":  cover_image,
        "emoji":       emoji,
    }


def main():
    print(f"[fetch_notion] DB ID: {DB_ID[:8]}... 쿼리 시작")
    pages = query_database(DB_ID)
    print(f"[fetch_notion] {len(pages)}개 페이지 발견")

    items = [parse_page(p) for p in pages]

    output = {
        "updatedAt": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
        "count":     len(items),
        "items":     items,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[fetch_notion] data.json 저장 완료 ({len(items)}개 항목)")


if __name__ == "__main__":
    main()
