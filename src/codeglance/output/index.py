"""Offline HTML index for generated output folders."""

from __future__ import annotations

import html
import time
from pathlib import Path

from .profiles import GeneratedOutput


def build_output_index(root: Path, outputs: list[GeneratedOutput]) -> str:
    """Build an offline-friendly index for a generated output folder."""
    rows = []
    for item in outputs:
        rel = item.path.name
        rows.append(
            '<a class="item" href="{href}">'
            '<span class="kind">{kind}</span>'
            '<span class="name">{name}</span>'
            '<span class="label">{label}</span>'
            "</a>".format(
                href=html.escape(rel),
                kind=html.escape(item.kind),
                name=html.escape(rel),
                label=html.escape(item.label),
            )
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>codeglance outputs · {html.escape(root.name)}</title>
<style>
  :root {{ color-scheme:dark; --bg:#0b0f14; --panel:#141b24; --line:#263342;
    --text:#e8edf2; --muted:#94a3b8; --accent:#5ba4cf; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ width:min(920px,100%); margin:0 auto; padding:22px; }}
  header {{ padding:12px 0 18px; border-bottom:1px solid var(--line); margin-bottom:16px; }}
  h1 {{ margin:0 0 6px; font-size:24px; letter-spacing:0; }}
  .sub {{ color:var(--muted); font-size:13px; word-break:break-word; }}
  .list {{ display:grid; gap:9px; }}
  .item {{ display:grid; grid-template-columns:96px 1fr 1.4fr; gap:12px; align-items:center;
    min-height:48px; padding:10px 12px; color:var(--text); text-decoration:none;
    background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
  .item:hover {{ border-color:var(--accent); }}
  .kind {{ color:var(--accent); font-size:11px; font-weight:700; text-transform:uppercase; }}
  .name {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:13px; }}
  .label {{ color:var(--muted); font-size:13px; }}
  footer {{ color:var(--muted); font-size:12px; padding:18px 0 4px; }}
  @media (max-width:640px) {{
    main {{ padding:16px; }}
    .item {{ grid-template-columns:1fr; gap:4px; }}
  }}
</style>
</head>
<body>
<main>
  <header>
    <h1>codeglance outputs</h1>
    <div class="sub">{html.escape(str(root))}</div>
  </header>
  <section class="list">{''.join(rows)}</section>
  <footer>Generated {html.escape(time.strftime("%Y-%m-%d %H:%M"))}</footer>
</main>
</body>
</html>
"""
