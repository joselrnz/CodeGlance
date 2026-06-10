"""Local output browser for generated codeglance artifacts."""

from __future__ import annotations

import html
import socket
import time
import webbrowser
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ARTIFACT_SUFFIXES = {".html", ".htm", ".md", ".json", ".txt", ".svg"}


@dataclass(frozen=True)
class Artifact:
    """A generated file that is useful from the local output browser."""

    path: str
    suffix: str
    size: int
    mtime: float

    @property
    def kind(self) -> str:
        if self.suffix in {".html", ".htm"}:
            return "HTML"
        if self.suffix == ".md":
            return "Markdown"
        if self.suffix == ".json":
            return "JSON"
        if self.suffix == ".svg":
            return "SVG"
        return self.suffix.lstrip(".").upper() or "File"


def iter_artifacts(root: Path) -> list[Artifact]:
    """Return generated artifacts under `root`, sorted for a stable local index."""
    out: list[Artifact] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix not in ARTIFACT_SUFFIXES:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        out.append(Artifact(rel, suffix, stat.st_size, stat.st_mtime))
    return sorted(out, key=lambda item: (item.kind, item.path.lower()))


def build_index_html(root: Path, title: str = "codeglance outputs") -> str:
    """Build a mobile-friendly index page for artifacts in `root`."""
    artifacts = iter_artifacts(root)
    rows = []
    for artifact in artifacts:
        href = "/__file__/" + "/".join(_quote_url_part(part) for part in artifact.path.split("/"))
        rows.append(
            '<a class="item" href="{href}">'
            '<span class="kind">{kind}</span>'
            '<span class="name">{name}</span>'
            '<span class="meta">{size} &middot; {mtime}</span>'
            "</a>".format(
                href=href,
                kind=html.escape(artifact.kind),
                name=html.escape(artifact.path),
                size=html.escape(_format_size(artifact.size)),
                mtime=html.escape(time.strftime("%Y-%m-%d %H:%M", time.localtime(artifact.mtime))),
            )
        )
    listing = "\n".join(rows) or '<p class="empty">No HTML, Markdown, JSON, TXT, or SVG artifacts found.</p>'
    root_label = html.escape(str(root))
    title_esc = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_esc}</title>
<style>
  :root {{
    color-scheme: dark;
    --bg:#0b0f14; --panel:#141b24; --line:#263342; --text:#e8edf2;
    --muted:#94a3b8; --accent:#5ba4cf; --accent2:#63c18f;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ width:min(980px,100%); margin:0 auto; padding:22px; }}
  header {{ display:flex; align-items:flex-start; justify-content:space-between; gap:18px;
    padding:16px 0 18px; border-bottom:1px solid var(--line); margin-bottom:16px; }}
  h1 {{ margin:0 0 5px; font-size:24px; line-height:1.15; letter-spacing:0; }}
  .sub {{ color:var(--muted); font-size:13px; word-break:break-word; }}
  .count {{ flex:none; color:var(--accent2); border:1px solid rgba(99,193,143,.35);
    border-radius:8px; padding:6px 10px; font-size:13px; }}
  .list {{ display:grid; gap:9px; }}
  .item {{ display:grid; grid-template-columns:86px 1fr auto; gap:12px; align-items:center;
    min-height:48px; padding:10px 12px; color:var(--text); text-decoration:none;
    background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
  .item:hover {{ border-color:var(--accent); }}
  .kind {{ color:var(--accent); font-size:11px; font-weight:700; text-transform:uppercase; }}
  .name {{ min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:13px; }}
  .meta {{ color:var(--muted); font-size:12px; white-space:nowrap; }}
  .empty {{ color:var(--muted); padding:20px 0; }}
  footer {{ color:var(--muted); font-size:12px; padding:18px 0 4px; }}
  @media (max-width:640px) {{
    main {{ padding:16px; }}
    header {{ display:block; }}
    .count {{ display:inline-block; margin-top:10px; }}
    .item {{ grid-template-columns:1fr; gap:4px; }}
    .name {{ white-space:normal; overflow:visible; text-overflow:clip; }}
  }}
</style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>{title_esc}</h1>
      <div class="sub">{root_label}</div>
    </div>
    <div class="count">{len(artifacts)} artifacts</div>
  </header>
  <section class="list">{listing}</section>
  <footer>Generated by codeglance serve. Refresh this page after regenerating outputs.</footer>
</main>
</body>
</html>
"""


def serve_directory(root: Path, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = False) -> None:
    """Serve `root` until interrupted."""
    root = root.resolve()
    handler = partial(_OutputHandler, directory=str(root), title=f"codeglance outputs: {root.name}")
    server = ThreadingHTTPServer((host, port), handler)
    actual_host, actual_port = server.server_address
    local_url = f"http://127.0.0.1:{actual_port}/"
    lan = lan_ip()
    lan_url = f"http://{lan}:{actual_port}/" if lan else ""
    print(f"Serving {root}")
    print(f"Desktop: {local_url}")
    if host in {"0.0.0.0", ""} and lan_url:
        print(f"Phone on same Wi-Fi: {lan_url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(local_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


def lan_ip() -> str:
    """Best-effort LAN IP address for phone access hints."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return ""


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def _quote_url_part(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


class _OutputHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler that serves a generated index at the root."""

    def __init__(self, *args, title: str, **kwargs):
        self._title = title
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path in {"", "/", "/index.html"}:
            body = build_index_html(Path(self.directory), self._title).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/__file__/"):
            self.path = "/" + self.path.removeprefix("/__file__/")
        super().do_GET()
