# Swiss Cycling – Association Statistics

Interactive dashboard displaying the key figures of [Swiss Cycling](https://www.swiss-cycling.ch) – licenses, members, finances, events, and staff. Data sourced from the public annual reports.

**Live:** [flo3561.github.io/swisscycling_statistics](https://flo3561.github.io/swisscycling_statistics/)

![Dashboard Screenshot](screenshot.png)

---

## Features

- Five sections: **Licenses · Members · Finances · Events · Staff**
- Interactive charts (Chart.js) – hover tooltips, double-click to isolate, dark mode
- Trilingual **DE / FR / EN**
- Fully static – no backend, no database, runs entirely in the browser
- Cookieless, GDPR-compliant analytics via PostHog (no cookie banner needed)

---

## Updating data (annually)

| File | Content | Tool |
|---|---|---|
| `data/lizenzen.csv` | License counts by category | Manual from PDF |
| `data/mitglieder.csv` | Active & club members | Manual from PDF |
| `data/erfolgsrechnung.csv` | Revenue, expenses, result | Manual from PDF |
| `data/veranstaltungen.json` | Event calendar | `scripts/fetch_events.py` |
| `PERSONAL_DATA` in index.html | Team, board, commissions | `scripts/fetch_team.py` |

After updating the CSVs, run the build step to embed the data into `index.html`:

```bash
node build.js
```

For the event calendar (scrapes swiss-cycling.ch):

```bash
uv run --with requests --with beautifulsoup4 python scripts/fetch_events.py
```

---

## Local development

No installation required – open `index.html` directly in the browser. A VS Code Live Server task is preconfigured.

---

## Deployment

GitHub Actions (`.github/workflows/deploy.yml`) builds and deploys automatically on every push to `main`. The PostHog API key is injected from the GitHub Secret `POSTHOG_KEY` at build time – never stored in source code.

---

## Tech stack

| | |
|---|---|
| Charts | [Chart.js 4.4](https://www.chartjs.org/) |
| Fonts | Google Fonts – Syne & DM Sans |
| Analytics | [PostHog](https://posthog.com/) (EU, cookieless) |
| Hosting | GitHub Pages |

---

## License

Source code: [MIT](LICENSE) · Data: Swiss Cycling (copyright holder of the annual reports) · Independent community project, no official affiliation with Swiss Cycling.
