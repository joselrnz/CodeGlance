"""Zero-JavaScript static renderer: inline SVG (cards + layer containers). No interactivity."""

from __future__ import annotations

import html


def _clip(name: str, max_chars: int) -> str:
    return name if len(name) <= max_chars else name[: max_chars - 1] + "…"


def render_static_html(vm: dict) -> str:
    nodes = vm["nodes"]
    edges = vm["edges"]
    containers = vm.get("containers", [])
    layers = vm["layers"]
    types = vm.get("types", [])
    project = vm.get("project", {})
    stats = vm.get("stats", {})
    cw, ch = vm.get("cardW", 196.0), vm.get("cardH", 60.0)
    pos = {i: (n["x"], n["y"]) for i, n in enumerate(nodes)}

    if containers:
        minx = min(c["x"] for c in containers); miny = min(c["y"] for c in containers)
        maxx = max(c["x"] + c["w"] for c in containers); maxy = max(c["y"] + c["h"] for c in containers)
    elif nodes:
        xs = [n["x"] for n in nodes]; ys = [n["y"] for n in nodes]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    else:
        minx = miny = 0; maxx = maxy = 100
    pad = 40
    vb = f"{minx - pad:.0f} {miny - pad:.0f} {(maxx - minx) + 2 * pad:.0f} {(maxy - miny) + 2 * pad:.0f}"

    parts: list[str] = [
        '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
        '<path d="M0,0 L7,3 L0,6 Z" fill="#5b6b86"/></marker></defs>'
    ]
    # containers
    for c in containers:
        parts.append(
            f'<rect x="{c["x"]:.0f}" y="{c["y"]:.0f}" width="{c["w"]:.0f}" height="{c["h"]:.0f}" '
            f'rx="11" fill="rgba(255,255,255,0.02)" stroke="{c["color"]}" stroke-opacity="0.45"/>'
            f'<text x="{c["x"] + 12:.0f}" y="{c["y"] + 21:.0f}" fill="{c["color"]}" '
            f'font-family="ui-sans-serif,sans-serif" font-size="13" font-weight="600">'
            f'{html.escape(c["name"])} ({c["count"]})</text>'
        )
    # edges
    parts.append('<g stroke="#3a4661" stroke-width="1" stroke-opacity="0.5">')
    for a, b, _ty in edges:
        ax, ay = pos[a]; bx, by = pos[b]
        # stop at target card's top/center-ish so the arrow is visible
        parts.append(f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" marker-end="url(#arr)"/>')
    parts.append("</g>")
    # cards
    maxchars = int((cw - 18) / 7)
    for n in nodes:
        x = n["x"] - cw / 2; y = n["y"] - ch / 2
        parts.append(
            f'<g><rect x="{x:.0f}" y="{y:.0f}" width="{cw:.0f}" height="{ch:.0f}" rx="7" '
            f'fill="#151b29" stroke="rgba(148,163,184,0.18)"/>'
            f'<rect x="{x:.0f}" y="{y + 1:.0f}" width="4" height="{ch - 2:.0f}" fill="{n["color"]}"/>'
            f'<text x="{x + 10:.0f}" y="{y + 17:.0f}" fill="{n["color"]}" '
            f'font-family="ui-monospace,monospace" font-size="9" font-weight="700">{html.escape(n["type"].upper())}</text>'
            f'<text x="{x + 10:.0f}" y="{y + ch - 14:.0f}" fill="#e8edf5" '
            f'font-family="ui-sans-serif,sans-serif" font-size="12" font-weight="600">{html.escape(_clip(n["name"], maxchars))}</text>'
            f'<title>{html.escape(n["name"])}{" — " + html.escape(n["path"]) if n["path"] else ""}</title></g>'
        )
    svg_inner = "\n".join(parts)

    type_rows = "\n".join(
        f'<div class="lg"><span class="sw" style="background:{t["color"]}"></span>'
        f'<span class="nm">{html.escape(t["type"])}</span><span class="ct">{t["count"]}</span></div>'
        for t in types
    )
    layer_rows = "\n".join(
        f'<div class="lg"><span class="sw" style="background:{l["color"]}"></span>'
        f'<span class="nm">{html.escape(l["name"])}</span><span class="ct">{l["count"]}</span></div>'
        for l in layers
    )
    name = html.escape(project.get("name", "project"))
    subtitle = f'{stats.get("nodes", 0)} nodes · {stats.get("edges", 0)} edges · {len(layers)} layers (static)'

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{name} · Knowledge Graph (static)</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; background:#0b1220; color:#e8edf5; font-family:ui-sans-serif,system-ui,sans-serif; }}
  header {{ padding:16px 20px; border-bottom:1px solid #243049; }}
  header h1 {{ margin:0; font-size:18px; }} header .sub {{ color:#93a1b5; font-size:13px; margin-top:3px; }}
  .wrap {{ display:flex; align-items:flex-start; }}
  .graph {{ flex:1; min-width:0; }} svg {{ width:100%; height:auto; display:block; background:#0b1220; }}
  aside {{ width:240px; flex:none; border-left:1px solid #243049; padding:16px; position:sticky; top:0; max-height:100vh; overflow:auto; }}
  aside h4 {{ margin:14px 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:#93a1b5; }}
  aside h4:first-child {{ margin-top:0; }}
  .lg {{ display:flex; align-items:center; gap:8px; padding:3px 2px; font-size:12px; }}
  .sw {{ width:11px; height:11px; border-radius:3px; flex:none; }}
  .lg .nm {{ flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }} .lg .ct {{ color:#64748b; }}
  footer {{ padding:10px 20px; color:#475569; font-size:11px; border-top:1px solid #243049; }}
</style></head>
<body>
<header><h1>{name}</h1><div class="sub">{subtitle}</div></header>
<div class="wrap">
  <div class="graph"><svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg">
{svg_inner}
  </svg></div>
  <aside><h4>Node types</h4>{type_rows}<h4>Layers</h4>{layer_rows}</aside>
</div>
<footer>Generated by understand-anything-py · static (zero-JavaScript) render.</footer>
</body></html>
"""
