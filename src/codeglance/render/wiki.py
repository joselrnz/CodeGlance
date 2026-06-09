"""Wiki / docs renderer — a readable, low-jargon single-page "generated wiki" for a codebase.

Where the interactive renderer draws a graph, this renders a **document**: project overview,
getting-started (auto-detected install steps), architecture in prose, a per-file reference, and a
suggested reading order. It reuses ``build_view_model`` data and is fully self-contained + offline.
"""

from __future__ import annotations

import html as _html
from collections import defaultdict


def _esc(value: object) -> str:
    """HTML-escape a value (``None`` becomes an empty string)."""
    return _html.escape("" if value is None else str(value))


def _slug(text: str) -> str:
    """A lowercase, hyphenated anchor id from arbitrary text."""
    out = [c if c.isalnum() else "-" for c in str(text).lower()]
    return "".join(out).strip("-") or "x"


def _pills(items, cls: str = "pill") -> str:
    return "".join(f'<span class="{cls}">{_esc(i)}</span>' for i in items)


def render_wiki_html(vm: dict) -> str:
    """Render a view model into a self-contained docs/wiki HTML page (no JS required to read it)."""
    project = vm.get("project", {})
    stats = vm.get("stats", {})
    name = project.get("name", "project")
    description = project.get("description", "")
    languages = project.get("languages", []) or []
    frameworks = project.get("frameworks", []) or []
    layers = vm.get("layers", []) or []
    domains = vm.get("domains", []) or []
    tour = vm.get("tour", []) or []
    nodes = vm.get("nodes", []) or []
    install = vm.get("install", []) or []

    file_level = {"file", "config", "document", "service", "pipeline", "table", "schema", "resource", "endpoint"}

    # ---- sidebar nav (only sections that have content) ----
    nav = [("overview", "Overview"), ("getting-started", "Getting started")]
    if layers:
        nav.append(("architecture", "Architecture"))
    if domains:
        nav.append(("domains", "Domains"))
    nav.append(("reference", "Reference"))
    if tour:
        nav.append(("reading-order", "Reading order"))
    nav_html = "".join(f'<a href="#{anchor}">{_esc(label)}</a>' for anchor, label in nav)

    parts: list[str] = []

    # ---- Overview ----
    parts.append('<section id="overview"><h2>Overview</h2>')
    if description:
        parts.append(f'<p class="lead">{_esc(description)}</p>')
    parts.append('<div class="stats">')
    for value, key in (
        (stats.get("nodes", 0), "components"), (stats.get("edges", 0), "relationships"),
        (stats.get("layers", 0), "layers"), (len(domains), "domains"),
    ):
        parts.append(f'<div class="stat"><div class="v">{_esc(value)}</div><div class="k">{_esc(key)}</div></div>')
    parts.append("</div>")
    if languages:
        parts.append(f'<h4>Languages</h4><div class="pills">{_pills(languages)}</div>')
    if frameworks:
        parts.append(f'<h4>Frameworks</h4><div class="pills">{_pills(frameworks)}</div>')
    parts.append("</section>")

    # ---- Getting started ----
    parts.append('<section id="getting-started"><h2>Getting started</h2>')
    if install:
        for step in install:
            label, cmd = step.get("label", ""), step.get("command", "")
            if label:
                parts.append(f"<p>{_esc(label)}</p>")
            if cmd:
                parts.append(f"<pre><code>{_esc(cmd)}</code></pre>")
    else:
        parts.append('<p class="muted">No manifest files were detected, so there are no automatic '
                     "install steps. Clone the repository and follow its README.</p>")
    parts.append("</section>")

    # ---- Architecture (layers in prose) ----
    if layers:
        parts.append('<section id="architecture"><h2>Architecture</h2>'
                     "<p>The codebase is organised into the following layers:</p>")
        for layer in layers:
            color = layer.get("color", "#888")
            parts.append(
                f'<div class="layer"><span class="dot" style="background:{_esc(color)}"></span>'
                f'<div><strong>{_esc(layer.get("name", "Layer"))}</strong> '
                f'<span class="muted">· {_esc(layer.get("count", 0))} files</span>'
                + (f'<div class="desc">{_esc(layer.get("description"))}</div>' if layer.get("description") else "")
                + "</div></div>"
            )
        parts.append("</section>")

    # ---- Domains ----
    if domains:
        parts.append('<section id="domains"><h2>Domains</h2>'
                     "<p>Business areas inferred from the project structure:</p>")
        for d in domains:
            parts.append(f'<div class="card"><h4>{_esc(d.get("name"))}</h4>')
            if d.get("description"):
                parts.append(f'<p>{_esc(d.get("description"))}</p>')
            ents = d.get("entities", []) or []
            if ents:
                parts.append(f'<div class="pills">{_pills(ents, "pill chip")}</div>')
            parts.append(f'<div class="muted small">{_esc(d.get("nFiles", 0))} files · '
                         f'{_esc(d.get("flowCount", 0))} flows</div></div>')
        parts.append("</section>")

    # ---- Reference (file-level nodes grouped by directory) ----
    by_dir: dict[str, list] = defaultdict(list)
    for n in nodes:
        if n.get("type") in file_level and n.get("path"):
            d = n["path"].rsplit("/", 1)[0] if "/" in n["path"] else "(root)"
            by_dir[d].append(n)
    parts.append('<section id="reference"><h2>Reference</h2>')
    if by_dir:
        for d in sorted(by_dir):
            parts.append(f'<h3 class="dir">{_esc(d)}/</h3>')
            for n in sorted(by_dir[d], key=lambda x: x.get("name", "")):
                parts.append(
                    f'<div class="ref"><div class="ref-h"><code>{_esc(n.get("name"))}</code>'
                    f'<span class="tag">{_esc(n.get("type"))}</span>'
                    f'<span class="cx cx-{_esc(n.get("complexity", "moderate"))}">{_esc(n.get("complexity", ""))}</span></div>'
                    + (f'<p>{_esc(n.get("summary"))}</p>' if n.get("summary") else "")
                    + "</div>"
                )
    else:
        parts.append('<p class="muted">No file-level components were extracted.</p>')
    parts.append("</section>")

    # ---- Reading order (the tour) ----
    if tour:
        parts.append('<section id="reading-order"><h2>Reading order</h2>'
                     "<p>A suggested path for understanding this project:</p><ol class=\"steps\">")
        for step in tour:
            parts.append(f'<li><strong>{_esc(step.get("title"))}</strong>'
                         + (f'<div class="desc">{_esc(step.get("description"))}</div>' if step.get("description") else "")
                         + "</li>")
        parts.append("</ol></section>")

    body = "\n".join(parts)
    subtitle = (f'{stats.get("nodes", 0)} components · {stats.get("edges", 0)} relationships · '
                f'{stats.get("layers", 0)} layers')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{_esc(name)} · Documentation</title>
<style>
  :root {{ color-scheme: dark; --bg:#0a0a0a; --panel:#141414; --bd:rgba(212,165,116,0.18);
    --tx:#e9e3da; --tx2:#a39787; --muted:#6b5f53; --acc:#d4a574; --code:#0f0d0b; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--tx); line-height:1.6;
    font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
  a {{ color:var(--acc); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
  .wrap {{ display:flex; max-width:1100px; margin:0 auto; gap:36px; padding:0 24px; }}
  aside {{ width:210px; flex:none; position:sticky; top:0; align-self:flex-start; height:100vh;
    padding:28px 0; overflow:auto; }}
  aside .brand {{ font-family:Georgia,serif; font-size:20px; color:var(--tx); margin-bottom:4px; }}
  aside .tag {{ color:var(--muted); font-size:12px; margin-bottom:20px; }}
  aside nav {{ display:flex; flex-direction:column; gap:2px; }}
  aside nav a {{ color:var(--tx2); padding:6px 10px; border-radius:7px; font-size:14px; }}
  aside nav a:hover {{ background:var(--panel); color:var(--tx); text-decoration:none; }}
  main {{ flex:1; min-width:0; padding:36px 0 80px; }}
  h1 {{ font-family:Georgia,serif; font-weight:400; font-size:30px; margin:0 0 6px; }}
  h2 {{ font-family:Georgia,serif; font-weight:400; font-size:22px; margin:36px 0 12px;
    padding-bottom:8px; border-bottom:1px solid var(--bd); scroll-margin-top:20px; }}
  h3 {{ font-size:15px; margin:22px 0 8px; }} h4 {{ font-size:13px; color:var(--tx2); margin:18px 0 8px;
    text-transform:uppercase; letter-spacing:.05em; }}
  p {{ margin:8px 0; }} .lead {{ font-size:17px; color:var(--tx); }}
  .muted {{ color:var(--muted); }} .small {{ font-size:12px; }}
  pre {{ background:var(--code); border:1px solid var(--bd); border-radius:8px; padding:12px 14px;
    overflow:auto; }} code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; color:#e0c79a; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:12px; margin:14px 0; }}
  .stat {{ background:var(--panel); border:1px solid var(--bd); border-radius:10px; padding:12px 18px; min-width:110px; }}
  .stat .v {{ font-size:26px; font-weight:700; }} .stat .k {{ color:var(--tx2); font-size:12px; }}
  .pills {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .pill {{ background:var(--panel); border:1px solid var(--bd); border-radius:99px; padding:3px 11px; font-size:13px; }}
  .chip {{ font-family:ui-monospace,monospace; font-size:12px; }}
  .layer {{ display:flex; gap:10px; align-items:flex-start; padding:8px 0; }}
  .layer .dot {{ width:11px; height:11px; border-radius:3px; margin-top:7px; flex:none; }}
  .layer .desc, .ref p, .steps .desc {{ color:var(--tx2); font-size:14px; margin-top:2px; }}
  .card {{ background:var(--panel); border:1px solid var(--bd); border-radius:10px; padding:14px 16px; margin:10px 0; }}
  .card h4 {{ color:var(--acc); margin:0 0 6px; text-transform:none; letter-spacing:0; font-size:15px; }}
  .dir {{ font-family:ui-monospace,monospace; color:var(--tx2); font-size:13px; margin-top:26px; }}
  .ref {{ border-left:2px solid var(--bd); padding:4px 0 4px 14px; margin:10px 0; }}
  .ref-h {{ display:flex; align-items:center; gap:10px; }} .ref-h code {{ font-size:14px; color:var(--tx); }}
  .tag {{ font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--tx2);
    border:1px solid var(--bd); border-radius:4px; padding:1px 6px; }}
  .cx {{ font-size:11px; font-family:ui-monospace,monospace; }}
  .cx-simple {{ color:#5a9e6f; }} .cx-moderate {{ color:#d4a574; }} .cx-complex {{ color:#cf7a8a; }}
  .steps {{ padding-left:22px; }} .steps li {{ margin:10px 0; }}
  @media (max-width:760px) {{ .wrap {{ flex-direction:column; gap:0; }} aside {{ position:static; height:auto; width:auto; }} aside nav {{ flex-flow:row wrap; }} }}
</style></head>
<body>
<div class="wrap">
  <aside>
    <div class="brand">{_esc(name)}</div>
    <div class="tag">{_esc(subtitle)}</div>
    <nav>{nav_html}</nav>
  </aside>
  <main>
    <h1>{_esc(name)}</h1>
{body}
    <p class="muted small" style="margin-top:60px;border-top:1px solid var(--bd);padding-top:16px">
      Generated by codeglance · wiki mode · self-contained, offline.</p>
  </main>
</div>
</body></html>
"""
