# codeglance — brand kit (Dark Ocean)

Flat matte identity for `codeglance`, built on the project's default theme.

## Palette
| Role | Hex |
|---|---|
| matte ocean black (bg) | `#0B141D` |
| panel / lens interior | `#0F1B26` |
| ocean blue gradient | `#38BDF8 → #0E7490` |
| lens gradient | `#22D3EE → #2DD4BF` (cyan → teal) |
| deep node | `#155E75` |
| slate text | `#7E8C9A` |
| terminal text | `#C7D6DF` |

Font stack: `'JetBrains Mono','Fira Code','Cascadia Code',Consolas,monospace`

## Assets
| File | Size | Use |
|---|---|---|
| codeglance-banner.svg | 1280×360 | README header (centered lockup) |
| codeglance-social-card.svg | 1280×640 | GitHub Settings → Social preview (render to PNG first) |
| codeglance-app-icon.svg | 512 | PyPI avatar, desktop, anywhere square |
| codeglance-favicon.svg | 64 | `<link rel="icon" type="image/svg+xml" href="codeglance-favicon.svg">` — legible at 16px |
| codeglance-logo-light.svg | 820×180 | docs sites / light backgrounds (transparent) |
| codeglance-mono.svg | 280 | single-color stencil, recolors via CSS `currentColor` |
| codeglance-badge.svg | 262×28 | shields-style `codeglance | v0.1.0 · py3` — version is one <text> element |
| codeglance-divider.svg | 1280×40 | horizontal rule between README sections |

## Embeds
```markdown
![codeglance](assets/codeglance-banner.svg)
![version](assets/codeglance-badge.svg)
```
```css
/* mono stencil recolor */
.logo { color: #22D3EE; }
```
