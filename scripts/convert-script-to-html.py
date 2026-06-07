#!/usr/bin/env python3
"""Converteert script-van-parisii-tot-napoleon.md naar HTML."""

import re

MD_PATH = "tours/parisii tot napoleon/script-van-parisii-tot-napoleon.md"
HTML_PATH = "tours/parisii tot napoleon/script-van-parisii-tot-napoleon.html"

def convert(md: str) -> str:
    lines = md.split("\n")
    html_parts = []
    in_ul = False
    in_bold_section = False

    def close_ul():
        nonlocal in_ul
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False

    def fmt(line: str) -> str:
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)
        return line

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # HR
        if line.strip() == "---":
            close_ul()
            html_parts.append("<hr>")
            i += 1
            continue

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            close_ul()
            html_parts.append(f"<h1>{fmt(line[2:].strip())}</h1>")
            i += 1
            continue

        # H2 (##)
        if line.startswith("## "):
            close_ul()
            title = fmt(line[3:].strip())
            # Detect 📖 background sections vs stop sections vs intro/outro
            if "📖" in title:
                html_parts.append(f'<div class="background"><h2>{title}</h2>')
                in_bold_section = True
            elif title.startswith("Stop ") or title.startswith("Intro") or title.startswith("Outro"):
                html_parts.append(f'<div class="section"><h2>{title}</h2>')
            else:
                html_parts.append(f'<div class="section"><h2>{title}</h2>')
            i += 1
            # Collect content until next ## or --- or end
            content_lines = []
            while i < len(lines) and not lines[i].startswith("## ") and lines[i].strip() != "---":
                if lines[i].strip():
                    content_lines.append(lines[i])
                i += 1
            # Process content lines
            ul_open = False
            for cl in content_lines:
                stripped = cl.strip()
                if stripped.startswith("- "):
                    if not ul_open:
                        html_parts.append("<ul>")
                        ul_open = True
                    html_parts.append(f"<li>{fmt(stripped[2:])}</li>")
                elif stripped.startswith("1. ") or stripped.startswith("2. ") or stripped.startswith("3. "):
                    # Numbered list
                    if not ul_open:
                        # We'll close any open ul first
                        if ul_open:
                            html_parts.append("</ul>")
                        html_parts.append("<ol>")
                        ul_open = True
                        html_parts.append(f"<li>{fmt(re.sub(r'^\d+\.\s*', '', stripped))}</li>")
                    else:
                        html_parts.append(f"<li>{fmt(re.sub(r'^\d+\.\s*', '', stripped))}</li>")
                else:
                    if ul_open:
                        if stripped.startswith("**") or stripped == "":
                            continue
                        html_parts.append("</ul>")
                        ul_open = False
                    # Check for italic-only lines (location, walk cues, optional asides)
                    if stripped.startswith("*") and stripped.endswith("*") and stripped.count("*") == 2:
                        html_parts.append(f'<p class="meta">{fmt(stripped)}</p>')
                    elif stripped.startswith("*Locatie:") or stripped.startswith("*Van ") or stripped.startswith("*Loop ") or stripped.startswith("*Blijf ") or stripped.startswith("*Rechts,") or stripped.startswith("*Aan ") or stripped.startswith("*Als ") or stripped.startswith("*De piramide") or stripped.startswith("*Deze tuinen"):
                        html_parts.append(f'<p class="meta">{fmt(stripped)}</p>')
                    elif stripped == "**Spreektekst:**" or stripped == "**Onderweg:**" or stripped == "**Onderweg — Quai aux Fleurs (~2 min optioneel):**":
                        # Label
                        label = stripped.replace("**", "")
                        html_parts.append(f'<p class="label">{label}</p>')
                    elif stripped.startswith("**Optioneel"):
                        html_parts.append(f'<p class="optional-label">{fmt(stripped)}</p>')
                    elif stripped.startswith("**Hoe kon") or stripped.startswith("**Waarom is") or stripped.startswith("**De val") or stripped.startswith("**Waarom is dit"):
                        html_parts.append(f'<p class="subheading">{fmt(stripped)}</p>')
                    elif stripped.startswith("Optioneel:"):
                        html_parts.append(f'<p class="optional-label">{fmt(stripped)}</p>')
                    else:
                        html_parts.append(f"<p>{fmt(stripped)}</p>")
            if ul_open:
                html_parts.append("</ul>")
            # Close the div
            if in_bold_section:
                html_parts.append("</div>")
                in_bold_section = False
            else:
                html_parts.append("</div>")
            continue

        i += 1

    return "\n".join(html_parts)


def main():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md = f.read()

    body = convert(md)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Script: Van Parisii tot Napoleon</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    line-height: 1.7;
    padding: 2rem 1rem;
  }}
  .container {{ max-width: 860px; margin: 0 auto; }}

  h1 {{
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 2rem 1.5rem;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    color: #fff;
    font-size: 1.8rem;
  }}

  hr {{ border: none; border-top: 1px solid #333; margin: 1.5rem 0; }}

  .section, .background {{
    background: #16213e;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    overflow: hidden;
  }}

  .background {{ border-left: 4px solid #e67e22; }}

  h2 {{
    padding: .85rem 1.25rem;
    color: #fff;
    font-weight: 700;
    font-size: 1.15rem;
    background: rgba(255,255,255,.05);
    border-bottom: 1px solid rgba(255,255,255,.05);
  }}

  .background h2 {{ background: rgba(230,126,34,.15); }}

  p {{ padding: .2rem 1.25rem .6rem; font-size: .95rem; }}
  p:last-child {{ padding-bottom: 1rem; }}
  p.label {{
    font-weight: 700;
    color: #aaa;
    font-size: .8rem;
    text-transform: uppercase;
    letter-spacing: .05em;
    padding-top: .5rem;
    padding-bottom: .2rem;
  }}
  p.meta {{
    font-style: italic;
    color: #888;
    font-size: .88rem;
    background: rgba(255,255,255,.03);
    padding: .5rem 1.25rem;
    margin: 0;
  }}
  p.optional-label {{
    color: #e67e22;
    font-weight: 700;
    font-size: .9rem;
  }}
  p.subheading {{
    font-weight: 700;
    color: #80b5ff;
    font-size: .95rem;
    margin-top: .3rem;
  }}

  ul, ol {{ padding: .3rem 1.25rem 1rem 2.5rem; font-size: .95rem; }}
  li {{ margin-bottom: .3rem; }}
  li:last-child {{ margin-bottom: 0; }}

  strong {{ color: #80b5ff; }}
  em {{ color: #ccc; }}

  footer {{
    margin-top: 2rem;
    text-align: center;
    font-size: .85rem;
    color: #666;
    border-top: 1px solid #333;
    padding-top: 1.5rem;
  }}

  @media (max-width: 640px) {{
    h1 {{ font-size: 1.3rem; }}
    h2 {{ font-size: 1rem; }}
    p {{ font-size: .9rem; }}
  }}
</style>
</head>
<body>
<div class="container">

{body}

<footer>
  <p>Script voor Nederlandstalige wandelroute in Parijs · Van Parisii tot Napoleon</p>
</footer>

</div>
</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{HTML_PATH} gegenereerd.")


if __name__ == "__main__":
    main()
