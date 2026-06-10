# Canvas CLI Example

A tiny pure-Python CLI project that renders a simple canvas scene as SVG or ASCII.

- `canvas_cli/cli.py` - argparse entry point
- `canvas_cli/models.py` - canvas, point, and shape models
- `canvas_cli/palette.py` - named color palette helpers
- `canvas_cli/renderer.py` - SVG and ASCII renderers
- `canvas_cli/commands.py` - command handlers and demo scene builder

Run:

```bash
python -m canvas_cli --format svg --output scene.svg
python -m canvas_cli --format ascii
codeglance examples/canvas-cli
```
