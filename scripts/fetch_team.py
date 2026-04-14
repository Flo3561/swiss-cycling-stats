"""
fetch_team.py – Scrapes the Swiss Cycling team pages and updates:
  - data/personal.json     (structured data + fetch timestamp + yearly_stats)
  - index.html             (PERSONAL_DATA const replaced in-place)

Run annually:
  uv run --with requests --with beautifulsoup4 python scripts/fetch_team.py

Or via VS Code task: Ctrl+Shift+P → "Run Task" → "Fetch Personal Data (annual)"
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Run with:")
    print("  uv run --with requests --with beautifulsoup4 python scripts/fetch_team.py")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
TEAM_JSON = ROOT / "data" / "personal.json"
INDEX_HTML = ROOT / "index.html"

URLS = {
    "geschaeftsstelle": "https://www.swiss-cycling.ch/de/verband/team/geschaeftsstelle/",
    "trainer":          "https://www.swiss-cycling.ch/de/verband/team/trainerinnen/",
    "vorstand":         "https://www.swiss-cycling.ch/de/verband/team/vorstand/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SwissCyclingStatsBot/1.0)"}


def scrape_page(url: str) -> list[dict]:
    """Return list of {name, rolle/funktion/disziplin} dicts from a team page."""
    print(f"  Fetching {url} …", end=" ", flush=True)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    people = []

    # Swiss Cycling uses Craft CMS / custom theme.
    # Team cards typically look like:
    #   <div class="team-card"> or <article class="…">
    #     <h3 class="…">Name</h3>
    #     <p class="…">Role</p>
    #   </div>
    # We try several selector strategies in order.

    # Strategy 1: elements with class containing "team" or "person" or "member" or "card"
    card_selectors = [
        "[class*='team-member']", "[class*='person']", "[class*='TeamMember']",
        "[class*='team-card']",  "[class*='TeamCard']",
        "article",
    ]
    for sel in card_selectors:
        cards = soup.select(sel)
        if len(cards) >= 3:
            for card in cards:
                name_el = card.find(["h2", "h3", "h4", "strong"])
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if len(name) < 3 or len(name) > 60:
                    continue
                # role: first <p> after the name heading
                role_el = name_el.find_next(["p", "span"])
                role = role_el.get_text(strip=True) if role_el else ""
                if name and name not in [p["name"] for p in people]:
                    people.append({"name": name, "rolle": role})
            if people:
                break

    # Strategy 2: fallback – every h3 on the page paired with following sibling
    if not people:
        for h in soup.find_all(["h3", "h4"]):
            name = h.get_text(strip=True)
            if 3 < len(name) < 60 and re.search(r"[A-ZÄÖÜ][a-zäöü]", name):
                nxt = h.find_next_sibling(["p", "div", "span"])
                role = nxt.get_text(strip=True) if nxt else ""
                people.append({"name": name, "rolle": role})

    print(f"found {len(people)} people")
    return people


def add_department_from_headings(soup: BeautifulSoup, people: list[dict]) -> list[dict]:
    """Best-effort: assign abteilung by nearest preceding h2 heading."""
    all_h2 = [(h.get_text(strip=True), h) for h in soup.find_all("h2")]
    # map each person name → nearest preceding h2
    for p in people:
        name_el = soup.find(string=re.compile(re.escape(p["name"][:10])))
        if not name_el:
            continue
        pos = name_el.parent
        # walk up tree to find preceding h2
        for h2_text, h2_el in reversed(all_h2):
            try:
                if h2_el.find_parent() and pos.find_parent():
                    p.setdefault("abteilung", h2_text)
                    break
            except Exception:
                pass
    return people


def build_team_data(
    geschaeftsstelle: list[dict],
    trainer: list[dict],
    vorstand: list[dict],
    existing: dict | None = None,
) -> dict:
    # Append a new yearly_stats entry for the current year
    year = date.today().year
    new_stat = {
        "jahr": year,
        "geschaeftsstelle": len(geschaeftsstelle),
        "trainer": len(trainer),
        "vorstand": len(vorstand),
    }
    old_stats = (existing or {}).get("yearly_stats", [])
    # Replace entry for current year if already present, otherwise append
    stats = [s for s in old_stats if s["jahr"] != year] + [new_stat]
    stats.sort(key=lambda s: s["jahr"])
    return {
        "fetched_at": date.today().isoformat(),
        "yearly_stats": stats,
        "geschaeftsstelle": geschaeftsstelle,
        "trainer": trainer,
        "vorstand": vorstand,
    }


def json_to_js_literal(data: dict) -> str:
    """Convert Python dict to compact JS object literal (no JSON.parse needed)."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def update_index_html(team_data: dict) -> None:
    """Replace the PERSONAL_DATA const block in index.html."""
    html = INDEX_HTML.read_text(encoding="utf-8")

    js_block = (
        "/* AUTO-GENERATED by scripts/fetch_team.py – do not edit manually */\n"
        "const PERSONAL_DATA = "
        + json_to_js_literal(team_data)
        + ";"
    )

    # Replace existing block if present
    pattern = re.compile(
        r"/\* AUTO-GENERATED by scripts/fetch_team\.py.*?^const PERSONAL_DATA\s*=\s*\{.*?\};",
        re.DOTALL | re.MULTILINE,
    )
    if pattern.search(html):
        new_html = pattern.sub(js_block, html)
    else:
        # Insert just before the init section
        new_html = html.replace("/* ── INIT ALL", js_block + "\n\n/* ── INIT ALL", 1)

    INDEX_HTML.write_text(new_html, encoding="utf-8")
    print(f"  Updated {INDEX_HTML.name}")


def main():
    print("=== Swiss Cycling – Annual Team Fetch ===")

    scraped = {}
    errors = []

    for key, url in URLS.items():
        try:
            people = scrape_page(url)
            scraped[key] = people
        except Exception as e:
            print(f"  ERROR scraping {key}: {e}")
            errors.append(key)

    if errors:
        print(f"\nWARNING: {len(errors)} section(s) failed to scrape: {errors}")
        print("Keeping existing data for failed sections from data/team.json …")
        existing = json.loads(TEAM_JSON.read_text(encoding="utf-8")) if TEAM_JSON.exists() else {}
        for key in errors:
            scraped[key] = existing.get(key, [])

    existing = json.loads(TEAM_JSON.read_text(encoding="utf-8")) if TEAM_JSON.exists() else None
    team_data = build_team_data(
        geschaeftsstelle=scraped.get("geschaeftsstelle", []),
        trainer=scraped.get("trainer", []),
        vorstand=scraped.get("vorstand", []),
        existing=existing,
    )

    # Write team.json
    TEAM_JSON.write_text(
        json.dumps(team_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWritten {TEAM_JSON.name} ({sum(len(v) for v in [team_data['geschaeftsstelle'], team_data['trainer'], team_data['vorstand']])} people, fetched_at={team_data['fetched_at']})")

    # Patch index.html
    update_index_html(team_data)

    print("\nDone. Reload index.html in the browser to see the updated Team section.")


if __name__ == "__main__":
    main()
