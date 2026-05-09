"""
fetch_events.py – Scrapes the Swiss Cycling event calendar for multiple years and updates:
  - data/veranstaltungen.json   (full raw event list + yearly aggregates)
  - index.html                  (EMBEDDED_DATA.veranstaltungen replaced in-place)

Run for one or more years:
  uv run --with requests --with beautifulsoup4 python scripts/fetch_events.py
  uv run --with requests --with beautifulsoup4 python scripts/fetch_events.py --years 2021 2022 2023 2024 2025

Or via VS Code task: Ctrl+Shift+P → "Run Task" → "Fetch Events Data (annual)"
"""

import json
import re
import sys
import argparse
from datetime import date
from pathlib import Path
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Run with:")
    print("  uv run --with requests --with beautifulsoup4 python scripts/fetch_events.py")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
EVENTS_JSON = ROOT / "data" / "veranstaltungen.json"
INDEX_HTML  = ROOT / "index.html"

BASE_URL = "https://www.swiss-cycling.ch/de/veranstaltungen/kalender/?y={year}"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; SwissCyclingStatsBot/1.0)"}

# Discipline normalisation: maps raw Disziplin values → dashboard bucket
DISZ_MAP = {
    "Strasse":           "Strasse",
    "MTB XCO":           "MTB",
    "MTB XCC":           "MTB",
    "MTB XCM":           "MTB",
    "E-MTB Cross Country": "MTB",
    "MTB DH":            "MTB Gravity",
    "MTB Enduro":        "MTB Gravity",
    "MTB 4X":            "MTB Gravity",
    "Bahn":              "Bahn",
    "BMX":               "BMX",
    "Radquer":           "Radquer",
    "Trial":             "Trial",
    "Para-Cycling":      "Para",
    "Pumptrack":         "Sonstige",
    "Gravel":            "Sonstige",
    "Diverse":           "Sonstige",
    "Bikefestival":      "Sonstige",
}

# Class/Klasse normalisation: maps to one of National / International / Regional
def normalise_class(klasse: str) -> str:
    k = klasse.strip().lower()
    if any(x in k for x in ["international", "weltcup", "weltmeister", "europameister",
                              "uci", "uec", "c1", "c2", "c3", "hc", "1.1", "1.2", "2.1",
                              "uwwt", "worldtour"]):
        return "International"
    if any(x in k for x in ["regional", "training"]):
        return "Regional_Training"
    if any(x in k for x in ["national", "national", "schweizermeister", "championnat",
                              "top tour", "cycling for all"]):
        return "National"
    return "Sonstige_Klassen"


def scrape_year(year: int) -> list[dict]:
    url = BASE_URL.format(year=year)
    print(f"  Fetching {url} …", end=" ", flush=True)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    # Find the events table — look for a <table> or <tr> rows with ≥4 <td> cells
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        datum  = cells[0].get_text(strip=True)
        titel  = cells[1].get_text(strip=True)
        ort    = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        disz   = cells[3].get_text(strip=True) if len(cells) > 3 else ""
        klasse = cells[4].get_text(strip=True) if len(cells) > 4 else ""

        # Skip header-like rows and empty rows
        if not datum or datum.lower() in ("datum", "date"):
            continue
        if not disz:
            continue
        # Skip cancelled events
        titel_lower = titel.lower()
        if any(x in titel_lower for x in ["abgesagt", "annulé", "annulliert", "annulée"]):
            continue

        events.append({
            "datum":  datum,
            "titel":  titel,
            "ort":    ort,
            "disz":   disz,
            "klasse": klasse,
        })

    print(f"found {len(events)} events")
    return events


def aggregate(events: list[dict], year: int) -> dict:
    """Produce yearly summary counts."""
    disz_counts   = defaultdict(int)
    klasse_counts = defaultdict(int)

    for e in events:
        bucket = DISZ_MAP.get(e["disz"], "Sonstige")
        disz_counts[bucket] += 1
        klasse_counts[normalise_class(e["klasse"])] += 1

    return {
        "Jahr":            year,
        "Total":           len(events),
        "Strasse":         disz_counts["Strasse"],
        "MTB":             disz_counts["MTB"],
        "MTB_Gravity":     disz_counts["MTB Gravity"],
        "Bahn":            disz_counts["Bahn"],
        "BMX":             disz_counts["BMX"],
        "Radquer":         disz_counts["Radquer"],
        "Trial":           disz_counts["Trial"],
        "Para":            disz_counts["Para"],
        "Sonstige":        disz_counts["Sonstige"],
        "National":        klasse_counts["National"],
        "International":   klasse_counts["International"],
        "Regional_Training": klasse_counts["Regional_Training"],
    }


def update_index_html(aggregates: list[dict]) -> None:
    """Replace EMBEDDED_DATA.veranstaltungen in index.html."""
    html = INDEX_HTML.read_text(encoding="utf-8")

    rows_js = ",\n    ".join(
        "{" + ", ".join(f"{k}:{v}" for k, v in agg.items()) + "}"
        for agg in aggregates
    )
    new_block = (
        "veranstaltungen: [\n"
        f"    {rows_js},\n"
        "  ],"
    )

    # Replace existing veranstaltungen array in EMBEDDED_DATA
    pattern = re.compile(
        r"veranstaltungen:\s*\[.*?\],",
        re.DOTALL,
    )
    if pattern.search(html):
        new_html = pattern.sub(new_block, html)
        INDEX_HTML.write_text(new_html, encoding="utf-8")
        print(f"  Updated EMBEDDED_DATA.veranstaltungen in {INDEX_HTML.name}")
    else:
        print(f"  WARNING: Could not find veranstaltungen array in {INDEX_HTML.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--years", nargs="+", type=int,
        default=list(range(2021, date.today().year + 1)),
        help="Which years to fetch (default: 2021 to current year)"
    )
    args = parser.parse_args()

    print(f"=== Swiss Cycling – Event Calendar Fetch ({', '.join(map(str, args.years))}) ===")

    # Load existing data so we can merge (preserve years not being re-fetched)
    existing: dict = {}
    if EVENTS_JSON.exists():
        try:
            existing = json.loads(EVENTS_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass

    all_events: dict = existing.get("events_by_year", {})
    all_aggregates: dict = {a["Jahr"]: a for a in existing.get("aggregates", [])}

    for year in args.years:
        try:
            events = scrape_year(year)
            all_events[str(year)] = events
            all_aggregates[year] = aggregate(events, year)
        except Exception as e:
            print(f"  ERROR scraping {year}: {e}")
            # Keep existing data for this year if present
            if str(year) in all_events:
                print(f"  Keeping existing data for {year}")
            else:
                print(f"  No existing data for {year}, skipping")

    aggregates_sorted = sorted(all_aggregates.values(), key=lambda a: a["Jahr"])

    # Write veranstaltungen.json
    output = {
        "fetched_at": date.today().isoformat(),
        "aggregates": aggregates_sorted,
        "events_by_year": {k: all_events[k] for k in sorted(all_events.keys())},
    }
    EVENTS_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    total_events = sum(len(v) for v in all_events.values())
    print(f"\nWritten {EVENTS_JSON.name} ({total_events} total events across {len(all_events)} years)")

    # Patch index.html
    update_index_html(aggregates_sorted)

    print("\nDone. Reload index.html in the browser to see updated Veranstaltungen charts.")


if __name__ == "__main__":
    main()
