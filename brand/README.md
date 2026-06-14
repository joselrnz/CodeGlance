# codeglance - brand kit

Wide banner identity for `codeglance`, built around the code window, realistic magnifying glass,
evidence-map motif, and bold wordmark.

## Palette
| Role | Hex |
|---|---|
| matte ocean black (bg) | `#071017` |
| panel / lens interior | `#0D1720` / `#0A151D` |
| rim / glass accent | `#8CF4FF -> #22D3EE -> #0EA5E9` |
| handle accent | `#6EE7F9 -> #22D3EE -> #14B8A6` |
| deep node | `#155E75` |
| slate text | `#99B4C0` |
| terminal text | `#D7E8EF` |

Wordmark font stack: `Bahnschrift,'Aptos Display','Segoe UI',Arial,sans-serif`
Command font stack: `'JetBrains Mono','Cascadia Code',Consolas,monospace`

## Assets
| File | Size | Use |
|---|---|---|
| codeglance-banner.svg | 1600x420 | README header and canonical brand banner |
| codeglance-local-adapters.svg | 1400x620 | README product visual for scan, evidence graph, and local adapter workflows |
| codeglance-workflow.svg | 1400x520 | README workflow visual from repo scan to generated outputs |
| codeglance-hippocampus.svg | 1400x640 | README visual for context memory lanes and prompt-budget compression |
| codeglance-social-card.svg | 1280×640 | GitHub Settings → Social preview (render to PNG first) |
| codeglance-app-icon.svg | 512 | PyPI avatar, desktop, anywhere square |
| codeglance-favicon.svg | 64 | `<link rel="icon" type="image/svg+xml" href="codeglance-favicon.svg">` — legible at 16px |
| codeglance-logo-light.svg | 900x220 | docs sites / light backgrounds (transparent) |
| codeglance-mono.svg | 280 | single-color stencil; inline or use as a mask to recolor |
| codeglance-badge.svg | 286x28 | shields-style `codeglance | v0.0.1 · py3` — version is one <text> element |
| codeglance-divider.svg | 1280×40 | horizontal rule between README sections |

## Embeds
```markdown
![codeglance](codeglance-banner.svg)
![codeglance local adapters](codeglance-local-adapters.svg)
![codeglance workflow](codeglance-workflow.svg)
![codeglance hippocampus context](codeglance-hippocampus.svg)
![version](codeglance-badge.svg)
```
Third-party marks in `codeglance-local-adapters.svg` identify local adapter targets only. No
affiliation, endorsement, or partnership is implied.
```css
/* mono stencil recolor */
.logo { color: #22D3EE; }
```
