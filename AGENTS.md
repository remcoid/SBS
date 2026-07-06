# AGENTS.md — StepByStep

Dutch-speaking walking tour business in Paris.

## Directories

| Path | Contents |
|------|----------|
| `scripts/` | 3 Python scripts (stdlib) — run from repo root |
| `tours/obs_vault/` | Obsidian vault: 13 stops, 25 personen, 15 periodes, 15 concepten, 9 plaatsen |
| `tours/parisii tot napoleon/` | Route description, spoken script, generated Leaflet map |
| `news/` | Daily digest output (auto-generated HTML) |
| `admin/` | Business, legal, website content, etc. — **ignore** |

## Commands

```sh
python3 scripts/paris-chronological-route.py    # regen Leaflet map
python3 scripts/convert-script-to-html.py       # regen script HTML from .md
python3 scripts/daily-digest.py                 # gen news/YYYY-MM-DD-digest.html
python3 scripts/daily-digest.py --dry-run       # preview to stdout
python3 scripts/daily-digest.py --hours 72      # catch up after weekend
```

All use relative paths (`tours/`, `news/`) — must run from repo root, not from `scripts/`.

No pip, no build, no tests.

## Constraints

- **Scripts must run from repo root** — they reference `tours/parisii tot napoleon/` (spaces in path).
- **Script ↔ HTML**: hand-synced. Only the 3 Python scripts above auto-generate HTML. All other `.md`/`.html` pairs are manual.
- **CartoDB tiles**: if you see a 403 from `file://`, do NOT switch to OSM — same Referer issue. Serve via HTTP or use a local server.
- **Daily digest**: `scripts/daily-digest.py` fetches RSS from Le Parisien (Paris-specifiek) + Le Figaro (gefilterd op Parijs-relevantie). Output naar `news/YYYY-MM-DD-digest.html`. Cron: `0 7 * * *`. Voor meer bronnen: voeg RSS-URL toe aan `FEEDS` lijst en zet `SOURCE_IS_PARIS_SPECIFIC` op True/False.
- **13 stops** (not 12). Adding/removing a stop means updating: the Python script's `stops` list, the script .md + HTML, the route description .md + HTML, and the vault files + `00-wandelroute.md`.
- **Route description lags**: `van-parisii-tot-napoleon.md` lists 12 stops — missing "Stadsmuur Philippe Auguste". The script has 13. Both must be manually kept in sync.
- **Obsidian vault**: `.obsidian/` has sync-conflict files. Dataview queries YAML frontmatter only. Stops use nav format `← [[prev\|label]] · [[next\|label]] →` (first omits `←`, last omits `· next`). Templates use Templater syntax.
