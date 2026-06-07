# AGENTS.md — StepByStep

Dutch-speaking walking tour business in Paris.

## Directories

| Path | Contents |
|------|----------|
| `scripts/` | 2 Python scripts (stdlib) — run from repo root |
| `tours/obs_vault/` | Obsidian vault: 13 stops, 25 personen, 15 periodes, 15 concepten, 9 plaatsen |
| `tours/parisii tot napoleon/` | Route description, spoken script, generated Leaflet map |
| `admin/` | Business, legal, website content, etc. — **ignore** |

## Commands

```sh
python3 scripts/paris-chronological-route.py    # regen Leaflet map
python3 scripts/convert-script-to-html.py       # regen script HTML from .md
```

Both use relative paths (`tours/...`) — must run from repo root, not from `scripts/`.

No pip, no build, no tests.

## Constraints

- **Scripts must run from repo root** — they reference `tours/parisii tot napoleon/` (spaces in path).
- **Script ↔ HTML**: hand-synced. Only the 2 Python scripts above auto-generate HTML. All other `.md`/`.html` pairs are manual.
- **CartoDB tiles**: if you see a 403 from `file://`, do NOT switch to OSM — same Referer issue. Serve via HTTP or use a local server.
- **13 stops** (not 12). Adding/removing a stop means updating: the Python script's `stops` list, the script .md + HTML, the route description .md + HTML, and the vault files + `00-wandelroute.md`.
- **Route description lags**: `van-parisii-tot-napoleon.md` lists 12 stops — missing "Stadsmuur Philippe Auguste". The script has 13. Both must be manually kept in sync.
- **Obsidian vault**: `.obsidian/` has sync-conflict files. Dataview queries YAML frontmatter only. Stops use nav format `← [[prev\|label]] · [[next\|label]] →` (first omits `←`, last omits `· next`). Templates use Templater syntax.
