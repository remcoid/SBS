#!/usr/bin/env python3
"""Dagelijkse Parijs-update — haalt RSS-feeds op en genereert een HTML-digest.

Usage:
    python3 scripts/daily-digest.py [--hours 48] [--dry-run]

Output: news/YYYY-MM-DD-digest.html (of stdout met --dry-run)
"""

import datetime
import email.utils
import html as htmlmod
import os
import sys
import time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import URLError

OUT_DIR = "news"

FEEDS = [
    {
        "url": "https://www.leparisien.fr/paris-75/rss.xml",
        "label": "Le Parisien",
    },
    {
        "url": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
        "label": "Le Figaro",
    },
]

CATEGORY_RULES = [
    ("disruptions", [
        "fermeture", "fermé", "fermée", "grève", "perturbation",
        "circulation", "coupé", "coupée", "tunnel", "ligne",
        "metro", "rer", "bus", "tram", "travaux",
        "station", "retard", "accident", "bouclé", "bouclée",
    ]),
    ("events", [
        "festival", "exposition", "concert", "nuit blanche",
        "spectacle", "salon", "foire", "marché", "course",
        "match", "roland garros", "psg", "sport", "tennis",
        "finale", "open air", "baignade", "cinéma", "musique",
        "comédie musicale", "show", "performance", "fête",
        "célébration", "défilé", "14-juillet",
    ]),
    ("history", [
        "histoire", "historique", "musée", "monument", "statue",
        "restauration", "patrimoine", "siècle", "napoleon",
        "napoléon", "louvre", "notre-dame", "sainte-chapelle",
        "pont-neuf", "place de la concorde", "arc de triomphe",
        "renaissance", "romain", "gothique", "classé",
        "fouille", "vestige",
    ]),
    ("tourist", [
        "touriste", "touristique", "visite", "découvrir",
        "balade", "promenade", "jardin", "parc", "guide",
        "conseil", "bon plan", "à voir", "incontournable",
        "hébergement", "hôtel", "restaurant", "boulangerie",
        "terrasse", "shop", "boutique",
    ]),
]

PARIS_KEYWORDS = [
    "paris", "île-de-france", "ile-de-france", "roland garros",
    "seine", "versailles", "saint-denis", "notre-dame", "louvre",
    "bastille", "champs-élysées", "champs-elysees", "concorde",
    "périphérique", "peripherique", "porte de", "gare de",
    "montparnasse", "gare du nord", "gare de l'est",
    "pont-neuf", "sainte-chapelle", "pigalle", "moulin rouge",
    "trocadéro", "trocadero", "tuileries", "grand palais",
    "opéra", "opera", "bastille", "république", "republique",
    "marseille", "lyon",
]

SOURCE_IS_PARIS_SPECIFIC = {
    "Le Parisien": True,
    "Le Figaro": False,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DailyDigest/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}

ORDER = ["disruptions", "events", "history", "tourist", "news"]
CATEGORY_META = {
    "disruptions": {"icon": "🚧", "label": "Verkeer & verstoringen", "color": "#e74c3c"},
    "events":     {"icon": "🎭", "label": "Evenementen & cultuur",   "color": "#3498db"},
    "history":    {"icon": "🏛️", "label": "Geschiedenis & erfgoed",  "color": "#e67e22"},
    "tourist":    {"icon": "📍", "label": "Voor bezoekers",          "color": "#27ae60"},
    "news":       {"icon": "📰", "label": "Overig Parijs-nieuws",    "color": "#9b59b6"},
}


def parse_rfc2822(text):
    try:
        return email.utils.parsedate_to_datetime(text)
    except Exception:
        return None


def fetch_feed(url):
    items = []
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            raw = resp.read()
    except URLError as e:
        print(f"  [skipped] {url} — {e.reason}", file=sys.stderr)
        return items
    except OSError as e:
        print(f"  [skipped] {url} — {e}", file=sys.stderr)
        return items

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  [skipped] {url} — parse error: {e}", file=sys.stderr)
        return items

    ch = root.find("channel")
    if ch is not None:
        fallback_date = None
        lb = ch.find("lastBuildDate")
        if lb is not None and lb.text:
            fallback_date = parse_rfc2822(lb.text)
        for item in ch.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            date_el = item.find("pubDate")
            title = title_el.text if title_el is not None and title_el.text else ""
            link = link_el.text if link_el is not None and link_el.text else ""
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            pub = parse_rfc2822(date_el.text) if date_el is not None and date_el.text else fallback_date
            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "desc": desc.strip(),
                "pub": pub,
            })
        return items

    ns_atom = "http://www.w3.org/2005/Atom"
    entries = root.findall(f"{{{ns_atom}}}entry")
    if entries:
        for entry in entries:
            title_el = entry.find(f"{{{ns_atom}}}title")
            link_el = entry.find(f"{{{ns_atom}}}link")
            desc_el = entry.find(f"{{{ns_atom}}}summary")
            date_el = entry.find(f"{{{ns_atom}}}published")
            title = title_el.text if title_el is not None and title_el.text else ""
            link = ""
            if link_el is not None:
                link = link_el.get("href", "")
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            pub = parse_rfc2822(date_el.text) if date_el is not None and date_el.text else None
            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "desc": desc.strip(),
                "pub": pub,
            })
        return items

    return items


def classify(item):
    text = (item["title"] + " " + item["desc"]).lower()
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return cat
    return "news"


def is_paris_relevant(item):
    text = (item["title"] + " " + item["desc"]).lower()
    return any(kw in text for kw in PARIS_KEYWORDS)


def esc(text):
    return htmlmod.escape(text)


def truncate(text, n=200):
    if len(text) > n:
        return text[:n].rsplit(" ", 1)[0] + "…"
    return text


def render_html(items, today):
    grouped = {}
    for cat in ORDER:
        grouped[cat] = []
    for item in items:
        grouped[item["category"]].append(item)

    date_display = datetime.datetime.now().strftime("%A %d %B %Y")
    gen_time = datetime.datetime.now().strftime("%d %b %Y %H:%M")

    # Build category sections
    sections_html = ""
    for cat in ORDER:
        cat_items = grouped[cat]
        if not cat_items:
            continue
        meta = CATEGORY_META[cat]
        rows = ""
        for item in cat_items:
            desc = truncate(item.get("desc", ""), 160)
            desc_html = f'<p class="desc">{esc(desc)}</p>' if desc else ""
            rows += f"""
            <li>
              <a href="{esc(item['link'])}" target="_blank" rel="noopener">{esc(item['title'])}</a>
              {desc_html}
              <span class="source">{esc(item['source'])}</span>
            </li>"""
        sections_html += f"""
        <section>
          <h2 style="border-left:4px solid {meta['color']}">{meta['icon']} {esc(meta['label'])}</h2>
          <ul>{rows}</ul>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dagelijkse Parijs-update — {today}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    line-height: 1.6;
    padding: 2rem 1rem;
  }}
  .container {{ max-width: 860px; margin: 0 auto; }}

  header {{
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem 1.5rem;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
  }}
  header h1 {{ color: #fff; font-size: 1.6rem; font-weight: 700; }}
  header p {{ color: #aaa; font-size: .85rem; margin-top: .4rem; }}

  section {{
    background: #16213e;
    border-radius: 14px;
    margin-bottom: 1.2rem;
    overflow: hidden;
  }}
  section h2 {{
    padding: .85rem 1.25rem;
    color: #fff;
    font-weight: 700;
    font-size: 1.05rem;
    background: rgba(255,255,255,.04);
  }}
  section ul {{
    list-style: none;
    padding: .5rem 0;
  }}
  section li {{
    padding: .6rem 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,.04);
  }}
  section li:last-child {{ border-bottom: none; }}

  section li a {{
    color: #7bb8ff;
    text-decoration: none;
    font-weight: 500;
    font-size: .95rem;
    display: inline-block;
    margin-bottom: .15rem;
  }}
  section li a:hover {{ text-decoration: underline; color: #9fcbff; }}

  .desc {{
    color: #999;
    font-size: .85rem;
    margin-top: .15rem;
    line-height: 1.5;
  }}
  .source {{
    display: inline-block;
    font-size: .75rem;
    color: #666;
    margin-top: .2rem;
  }}
  .source::before {{ content: "— "; }}

  footer {{
    margin-top: 2rem;
    text-align: center;
    font-size: .82rem;
    color: #555;
    border-top: 1px solid #2a2a3e;
    padding-top: 1.5rem;
  }}

  @media (max-width: 640px) {{
    body {{ padding: 1rem .5rem; }}
    header h1 {{ font-size: 1.25rem; }}
    section h2 {{ font-size: .95rem; }}
    section li {{ padding: .5rem 1rem; }}
  }}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>📍 Dagelijkse Parijs-update</h1>
  <p>{esc(date_display)} · {len(items)} items uit {len(FEEDS)} bronnen</p>
</header>

{sections_html}

<footer>Generated {esc(gen_time)} · scripts/daily-digest.py</footer>

</div>
</body>
</html>"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parijs daily digest")
    parser.add_argument("--hours", type=int, default=48,
                        help="Items publicer in de afgelopen N uur (default: 48)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print naar stdout ipv bestand")
    args = parser.parse_args()

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=args.hours)

    print(f"📡 Feeds ophalen (sinds {cutoff.strftime('%a %d %b %H:%M')})...", file=sys.stderr)

    all_items = []
    seen_titles = set()

    for feed in FEEDS:
        print(f"  → {feed['label']}: {feed['url']}", file=sys.stderr)
        items = fetch_feed(feed["url"])
        is_specific = SOURCE_IS_PARIS_SPECIFIC.get(feed["label"], False)
        for item in items:
            item["source"] = feed["label"]
            if item["pub"] and item["pub"] >= cutoff:
                norm = item["title"].lower().strip()
                if norm and norm not in seen_titles:
                    seen_titles.add(norm)
                    if not is_specific and not is_paris_relevant(item):
                        continue
                    item["category"] = classify(item)
                    all_items.append(item)

    print(f"  ✓ {len(all_items)} items na filtering + dedup", file=sys.stderr)

    today = datetime.date.today().isoformat()

    if not all_items:
        output = f"""<!DOCTYPE html>
<html lang="nl">
<head><meta charset="UTF-8"><title>Dagelijkse Parijs-update — {today}</title>
<style>body{{font-family:system-ui,sans-serif;background:#1a1a2e;color:#e0e0e0;padding:2rem;text-align:center}}</style>
</head>
<body><h1>📍 Dagelijkse Parijs-update — {today}</h1><p>Geen nieuwe items gevonden.</p></body>
</html>"""
        _write_output(output, args.dry_run, today)
        return

    html = render_html(all_items, today)
    _write_output(html, args.dry_run, today)


def _write_output(output, dry_run, date_str):
    if dry_run:
        print(output)
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date_str}-digest.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✅ {path} — {len(output.splitlines())} regels", file=sys.stderr)


if __name__ == "__main__":
    main()
